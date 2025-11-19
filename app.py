from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import csv
from datetime import datetime
from config import Config
from models import db, Product, Webhook, UploadLog
import requests
import threading
import json

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with engine options
    db.init_app(app)
    
    # Simple database initialization without Redis dependency
    with app.app_context():
        try:
            # Test database connection with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    db.create_all()
                    print("Database tables created successfully")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Database connection attempt {attempt + 1} failed, retrying...")
                        import time
                        time.sleep(2)
                    else:
                        print(f"Database initialization error: {e}")
                        # Continue anyway for local development
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    CORS(app)
    
    # Create upload folder
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    
    return app

app = create_app()

def trigger_webhooks(event_type, product_data):
    """Trigger all active webhooks for a given event type"""
    try:
        with app.app_context():
            # Find all active webhooks that listen to this event type
            active_webhooks = Webhook.query.filter(
                Webhook.active == True
            ).all()
            
            # Filter webhooks that contain the event type in their event_types JSON array
            matching_webhooks = []
            for webhook in active_webhooks:
                if webhook.event_types and event_type in webhook.event_types:
                    matching_webhooks.append(webhook)
            
            if not matching_webhooks:
                return
            
            # Prepare webhook payload
            payload = {
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': product_data
            }
            
            # Send webhooks asynchronously to avoid blocking the main request
            def send_webhook(webhook, payload):
                try:
                    headers = {'Content-Type': 'application/json'}
                    if webhook.headers:
                        headers.update(webhook.headers)
                    
                    # Add secret as header if present
                    if webhook.secret:
                        headers['X-Webhook-Secret'] = webhook.secret
                    
                    response = requests.post(
                        webhook.url,
                        json=payload,
                        headers=headers,
                        timeout=10
                    )
                    
                    # Update webhook with success info
                    with app.app_context():
                        webhook.last_triggered = datetime.utcnow()
                        webhook.last_response_code = response.status_code
                        webhook.last_error = None
                        try:
                            db.session.commit()
                        except:
                            db.session.rollback()
                    
                except Exception as e:
                    # Update webhook with error info
                    with app.app_context():
                        webhook.last_triggered = datetime.utcnow()
                        webhook.last_response_code = None
                        webhook.last_error = str(e)
                        try:
                            db.session.commit()
                        except:
                            db.session.rollback()
            
            # Send webhooks in separate threads
            for webhook in matching_webhooks:
                thread = threading.Thread(target=send_webhook, args=(webhook, payload))
                thread.daemon = True
                thread.start()
                
    except Exception as e:
        print(f"Error triggering webhooks: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        
        query = Product.query
        
        # Search in name, SKU, or description only
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.sku.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Order by updated_at desc to show newest first
        query = query.order_by(Product.updated_at.desc())
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('sku'):
            return jsonify({'error': 'Name and SKU are required'}), 400
        
        # Check if SKU already exists (case-insensitive)
        existing = Product.query.filter(db.func.lower(Product.sku) == db.func.lower(data['sku'])).first()
        if existing:
            return jsonify({'error': 'Product with this SKU already exists'}), 409
        
        product = Product(
            name=data['name'],
            sku=data['sku'],
            description=data.get('description', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Trigger webhooks for product creation
        trigger_webhooks('product.created', product.to_dict())
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if SKU already exists for other products (case-insensitive)
        if 'sku' in data and data['sku'] != product.sku:
            existing = Product.query.filter(
                db.func.lower(Product.sku) == db.func.lower(data['sku']),
                Product.id != product_id
            ).first()
            if existing:
                return jsonify({'error': 'Product with this SKU already exists'}), 409
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'sku' in data:
            product.sku = data['sku']
        if 'description' in data:
            product.description = data['description']
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Trigger webhooks for product update
        trigger_webhooks('product.updated', product.to_dict())
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product_data = product.to_dict()  # Get data before deletion
        
        db.session.delete(product)
        db.session.commit()
        
        # Trigger webhooks for product deletion
        trigger_webhooks('product.deleted', product_data)
        
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/bulk-delete', methods=['DELETE'])
def bulk_delete_products():
    try:
        # Get all products before deletion for webhook triggering
        products = Product.query.all()
        deleted_count = len(products)
        
        # Trigger webhooks for each deleted product
        for product in products:
            trigger_webhooks('product.deleted', product.to_dict())
        
        Product.query.delete()
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {deleted_count} products',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
        # Simple CSV processing - only name, sku, description
        processed_count = 0
        error_count = 0
        updated_count = 0
        errors = []
        
        # Read CSV
        content = file.stream.read().decode('utf-8')
        csv_reader = csv.DictReader(content.splitlines())
        
        for i, row in enumerate(csv_reader, 1):
            try:
                # Check required fields
                if not row.get('name') or not row.get('sku'):
                    errors.append(f"Row {i+1}: Missing name or SKU")
                    error_count += 1
                    continue
                
                # Check for existing product (case-insensitive SKU)
                existing = Product.query.filter(
                    db.func.lower(Product.sku) == db.func.lower(row['sku'].strip())
                ).first()
                
                if existing:
                    # Update existing
                    existing.name = row['name'].strip()
                    existing.description = row.get('description', '').strip()
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                    
                    # Trigger webhook for updated product
                    try:
                        trigger_webhooks('product.updated', existing.to_dict())
                    except:
                        pass  # Don't fail upload if webhook fails
                else:
                    # Create new
                    product = Product(
                        name=row['name'].strip(),
                        sku=row['sku'].strip(),
                        description=row.get('description', '').strip()
                    )
                    db.session.add(product)
                    
                    # Trigger webhook for created product (will trigger after commit)
                    try:
                        db.session.flush()  # Ensure product has an ID
                        trigger_webhooks('product.created', product.to_dict())
                    except:
                        pass  # Don't fail upload if webhook fails
                
                processed_count += 1
                
                # Commit every 50 records
                if processed_count % 50 == 0:
                    db.session.commit()
                    
            except Exception as e:
                error_count += 1
                errors.append(f"Row {i+1}: {str(e)}")
                continue
        
        # Final commit
        db.session.commit()
        
        return jsonify({
            'message': 'Upload completed',
            'processed_count': processed_count,
            'error_count': error_count,
            'updated_count': updated_count,
            'errors': errors[:5]  # First 5 errors only
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks', methods=['GET'])
def get_webhooks():
    try:
        webhooks = Webhook.query.all()
        return jsonify({
            'webhooks': [webhook.to_dict() for webhook in webhooks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks', methods=['POST'])
def create_webhook():
    try:
        data = request.get_json()
        
        if not data or not data.get('name') or not data.get('url'):
            return jsonify({'error': 'Name and URL are required'}), 400
        
        webhook = Webhook(
            name=data['name'],
            url=data['url'],
            event_types=data.get('event_types', []),
            active=data.get('active', True),
            secret=data.get('secret', ''),
            headers=data.get('headers', {})
        )
        
        db.session.add(webhook)
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook created successfully',
            'webhook': webhook.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks/<int:webhook_id>', methods=['PUT'])
def update_webhook(webhook_id):
    try:
        webhook = Webhook.query.get_or_404(webhook_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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
        
        return jsonify({
            'message': 'Webhook updated successfully',
            'webhook': webhook.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks/<int:webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    try:
        webhook = Webhook.query.get_or_404(webhook_id)
        db.session.delete(webhook)
        db.session.commit()
        
        return jsonify({'message': 'Webhook deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhooks/<int:webhook_id>/test', methods=['POST'])
def test_webhook(webhook_id):
    try:
        import requests
        import time
        
        webhook = Webhook.query.get_or_404(webhook_id)
        
        # Prepare test payload
        test_payload = {
            'event_type': 'webhook.test',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'message': 'This is a test webhook from your application'
            }
        }
        
        start_time = time.time()
        
        # Send test request
        headers = {'Content-Type': 'application/json'}
        if webhook.headers:
            headers.update(webhook.headers)
        
        response = requests.post(
            webhook.url,
            json=test_payload,
            headers=headers,
            timeout=30
        )
        
        response_time = round((time.time() - start_time) * 1000, 2)  # ms
        
        # Update webhook with test results
        webhook.last_triggered = datetime.utcnow()
        webhook.last_response_code = response.status_code
        
        if not response.ok:
            webhook.last_error = f"HTTP {response.status_code}: {response.text[:500]}"
        else:
            webhook.last_error = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Webhook test completed',
            'status_code': response.status_code,
            'response_time_ms': response_time,
            'success': response.ok
        })
        
    except Exception as e:
        # Update webhook with error
        webhook = Webhook.query.get(webhook_id)
        if webhook:
            webhook.last_triggered = datetime.utcnow()
            webhook.last_error = str(e)[:500]
            webhook.last_response_code = 0
            db.session.commit()
        
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(host=host, port=port, debug=debug)