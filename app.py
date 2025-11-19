from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from celery import Celery
import os
import redis
import json
from datetime import datetime
from config import Config
from models import db, Product, Webhook, UploadLog

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    CORS(app)
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def create_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

app = create_app()
celery = create_celery(app)

# Redis client for progress tracking
redis_client = redis.from_url(app.config['REDIS_URL'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Only CSV files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start background task
        task = process_csv_file.delay(filepath, filename)
        
        return jsonify({
            'task_id': task.id,
            'message': 'File upload started',
            'status': 'processing'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_progress/<task_id>')
def upload_progress(task_id):
    try:
        # Get progress from Redis
        progress_data = redis_client.get(f"upload_progress:{task_id}")
        if progress_data:
            progress = json.loads(progress_data)
            return jsonify(progress)
        
        # Check database for upload log
        upload_log = UploadLog.query.filter_by(task_id=task_id).first()
        if upload_log:
            return jsonify(upload_log.to_dict())
        
        return jsonify({'error': 'Task not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        active_filter = request.args.get('active')
        
        query = Product.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.sku.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        if active_filter is not None:
            active_bool = active_filter.lower() == 'true'
            query = query.filter(Product.active == active_bool)
        
        # Paginate results
        products = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'products': [p.to_dict() for p in products.items],
            'total': products.total,
            'page': page,
            'per_page': per_page,
            'pages': products.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('sku'):
            return jsonify({'error': 'Name and SKU are required'}), 400
        
        # Check if SKU already exists (case-insensitive)
        existing = Product.find_by_sku(data['sku'])
        if existing:
            return jsonify({'error': 'SKU already exists'}), 400
        
        product = Product(
            name=data['name'],
            sku=data['sku'],
            description=data.get('description', ''),
            active=data.get('active', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Trigger webhook
        trigger_webhook_task.delay('product.created', product.to_dict())
        
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Check if SKU change conflicts with existing SKU
        if data.get('sku') and data['sku'].lower() != product.sku.lower():
            existing = Product.find_by_sku(data['sku'])
            if existing and existing.id != product.id:
                return jsonify({'error': 'SKU already exists'}), 400
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'sku' in data:
            product.sku = data['sku']
        if 'description' in data:
            product.description = data['description']
        if 'active' in data:
            product.active = data['active']
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Trigger webhook
        trigger_webhook_task.delay('product.updated', product.to_dict())
        
        return jsonify(product.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product_data = product.to_dict()  # Store before deletion
        
        db.session.delete(product)
        db.session.commit()
        
        # Trigger webhook
        trigger_webhook_task.delay('product.deleted', product_data)
        
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/bulk', methods=['DELETE'])
def bulk_delete_products():
    try:
        count = Product.query.count()
        Product.query.delete()
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {count} products',
            'count': count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Webhook management endpoints
@app.route('/api/webhooks', methods=['GET'])
def get_webhooks():
    try:
        webhooks = Webhook.query.all()
        return jsonify([w.to_dict() for w in webhooks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks', methods=['POST'])
def create_webhook():
    try:
        data = request.get_json()
        
        if not data.get('name') or not data.get('url'):
            return jsonify({'error': 'Name and URL are required'}), 400
        
        webhook = Webhook(
            name=data['name'],
            url=data['url'],
            event_types=data.get('event_types', ['product.created', 'product.updated', 'product.deleted']),
            active=data.get('active', True),
            secret=data.get('secret'),
            headers=data.get('headers', {})
        )
        
        db.session.add(webhook)
        db.session.commit()
        
        return jsonify(webhook.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks/<int:webhook_id>', methods=['PUT'])
def update_webhook(webhook_id):
    try:
        webhook = Webhook.query.get_or_404(webhook_id)
        data = request.get_json()
        
        if 'name' in data:
            webhook.name = data['name']
        if 'url' in data:
            webhook.url = data['url']
        if 'event_types' in data:
            webhook.event_types = data['event_types']
        if 'active' in data:
            webhook.active = data['active']
        if 'secret' in data:
            webhook.secret = data['secret']
        if 'headers' in data:
            webhook.headers = data['headers']
        
        webhook.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(webhook.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks/<int:webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    try:
        webhook = Webhook.query.get_or_404(webhook_id)
        db.session.delete(webhook)
        db.session.commit()
        
        return jsonify({'message': 'Webhook deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks/<int:webhook_id>/test', methods=['POST'])
def test_webhook(webhook_id):
    try:
        webhook = Webhook.query.get_or_404(webhook_id)
        
        # Start test webhook task
        task = test_webhook_task.delay(webhook_id)
        
        return jsonify({
            'message': 'Webhook test started',
            'task_id': task.id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@celery.task
def process_csv_file(filepath, filename):
    """Background task to process CSV file"""
    import csv
    import uuid
    
    task_id = process_csv_file.request.id
    
    try:
        # Create upload log entry
        upload_log = UploadLog(
            task_id=task_id,
            filename=filename,
            status='processing'
        )
        db.session.add(upload_log)
        db.session.commit()
        
        # Read CSV file to count total rows first
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            # Count total rows
            reader = csv.reader(csvfile, delimiter=delimiter)
            rows = list(reader)
            total_rows = len(rows) - 1  # Subtract header row
        
        if total_rows <= 0:
            raise Exception("No data rows found in CSV file")
        
        # Update total rows count
        upload_log.total_rows = total_rows
        db.session.commit()
        
        # Validate required columns
        header_row = rows[0]
        required_columns = ['name', 'sku', 'description']
        
        # Create case-insensitive column mapping
        column_mapping = {}
        for required_col in required_columns:
            found = False
            for i, header in enumerate(header_row):
                if header.lower().strip() == required_col.lower():
                    column_mapping[required_col] = i
                    found = True
                    break
            if not found:
                raise Exception(f"Missing required column: {required_col}")
        
        # Process rows in smaller batches for better real-time updates
        batch_size = 100
        processed_rows = 0
        success_count = 0
        error_count = 0
        errors = []
        
        for i in range(1, len(rows), batch_size):  # Start from 1 to skip header
            batch_end = min(i + batch_size, len(rows))
            batch = rows[i:batch_end]
            
            for row_index, row in enumerate(batch, start=i):
                try:
                    # Extract data using column mapping
                    name = row[column_mapping['name']].strip() if column_mapping['name'] < len(row) else ''
                    sku = row[column_mapping['sku']].strip() if column_mapping['sku'] < len(row) else ''
                    description = row[column_mapping['description']].strip() if column_mapping['description'] < len(row) else ''
                    
                    if not name or not sku:
                        raise Exception("Name and SKU are required")
                    
                    # Check if product exists (case-insensitive SKU)
                    existing_product = Product.find_by_sku(sku)
                    
                    if existing_product:
                        # Update existing product
                        existing_product.name = name
                        existing_product.description = description
                        existing_product.updated_at = datetime.utcnow()
                    else:
                        # Create new product
                        product = Product(
                            name=name,
                            sku=sku,
                            description=description,
                            active=True
                        )
                        db.session.add(product)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_index + 1}: {str(e)}")
                
                processed_rows += 1
                
                # Update progress in Redis and database every 50 rows for more frequent updates
                if processed_rows % 50 == 0:
                    progress_data = {
                        'task_id': task_id,
                        'filename': filename,
                        'total_rows': total_rows,
                        'processed_rows': processed_rows,
                        'success_count': success_count,
                        'error_count': error_count,
                        'progress': (processed_rows / total_rows) * 100,
                        'status': 'processing'
                    }
                    
                    # Store in Redis with 1 hour expiration
                    redis_client.setex(
                        f"upload_progress:{task_id}",
                        3600,
                        json.dumps(progress_data)
                    )
                    
                    # Update database
                    upload_log.processed_rows = processed_rows
                    upload_log.success_count = success_count
                    upload_log.error_count = error_count
                    try:
                        db.session.commit()
                    except Exception as commit_error:
                        db.session.rollback()
                        print(f"Commit error: {commit_error}")
            
            # Commit batch
            db.session.commit()
        
        # Final update
        upload_log.processed_rows = processed_rows
        upload_log.success_count = success_count
        upload_log.error_count = error_count
        upload_log.status = 'completed'
        upload_log.completed_at = datetime.utcnow()
        if errors:
            upload_log.error_message = '\n'.join(errors[:10])  # Store first 10 errors
        db.session.commit()
        
        # Final progress update
        final_progress = {
            'task_id': task_id,
            'filename': filename,
            'total_rows': total_rows,
            'processed_rows': processed_rows,
            'success_count': success_count,
            'error_count': error_count,
            'progress': 100,
            'status': 'completed',
            'errors': errors[:10] if errors else []
        }
        
        redis_client.setex(
            f"upload_progress:{task_id}",
            3600,
            json.dumps(final_progress)
        )
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return final_progress
        
    except Exception as e:
        # Update upload log with error
        upload_log.status = 'failed'
        upload_log.error_message = str(e)
        upload_log.completed_at = datetime.utcnow()
        db.session.commit()
        
        # Update progress in Redis
        error_progress = {
            'task_id': task_id,
            'filename': filename,
            'status': 'failed',
            'error': str(e)
        }
        
        redis_client.setex(
            f"upload_progress:{task_id}",
            3600,
            json.dumps(error_progress)
        )
        
        raise

@celery.task
def trigger_webhook_task(event_type, product_data):
    """Background task to trigger webhooks"""
    import requests
    import hmac
    import hashlib
    import json
    
    try:
        # Get all active webhooks that listen to this event type
        webhooks = Webhook.query.filter(
            Webhook.active == True,
            Webhook.event_types.contains([event_type])
        ).all()
        
        for webhook in webhooks:
            try:
                payload = {
                    'event': event_type,
                    'data': product_data,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                headers = {
                    'Content-Type': 'application/json',
                    **webhook.headers
                }
                
                # Add signature if secret is provided
                if webhook.secret:
                    signature = hmac.new(
                        webhook.secret.encode(),
                        json.dumps(payload).encode(),
                        hashlib.sha256
                    ).hexdigest()
                    headers['X-Webhook-Signature'] = f'sha256={signature}'
                
                # Send webhook with timeout
                response = requests.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                # Update webhook status
                webhook.last_triggered = datetime.utcnow()
                webhook.last_response_code = response.status_code
                webhook.last_error = None if response.ok else response.text
                
            except Exception as e:
                # Update webhook with error
                webhook.last_triggered = datetime.utcnow()
                webhook.last_response_code = None
                webhook.last_error = str(e)
            
            finally:
                db.session.commit()
                
    except Exception as e:
        print(f"Error in webhook trigger task: {e}")

@celery.task
def test_webhook_task(webhook_id):
    """Background task to test a webhook"""
    import requests
    import json
    
    try:
        webhook = Webhook.query.get(webhook_id)
        if not webhook:
            return {'error': 'Webhook not found'}
        
        # Test payload
        payload = {
            'event': 'webhook.test',
            'data': {
                'message': 'This is a test webhook',
                'webhook_id': webhook_id
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        headers = {
            'Content-Type': 'application/json',
            **webhook.headers
        }
        
        # Add signature if secret is provided
        if webhook.secret:
            import hmac
            import hashlib
            signature = hmac.new(
                webhook.secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = f'sha256={signature}'
        
        # Send test webhook
        response = requests.post(
            webhook.url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        # Update webhook status
        webhook.last_triggered = datetime.utcnow()
        webhook.last_response_code = response.status_code
        webhook.last_error = None if response.ok else response.text
        db.session.commit()
        
        return {
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'success': response.ok
        }
        
    except Exception as e:
        # Update webhook with error
        if 'webhook' in locals():
            webhook.last_triggered = datetime.utcnow()
            webhook.last_response_code = None
            webhook.last_error = str(e)
            db.session.commit()
        
        return {'error': str(e)}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['FLASK_ENV'] == 'development')