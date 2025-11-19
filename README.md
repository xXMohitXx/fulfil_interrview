# Product Management System

A Flask-based web application for managing products with CSV import capabilities and webhook notifications.

## Features

- 📦 **Product Management**: Create, read, update, and delete products
- 📄 **CSV Import**: Bulk import products from CSV files (up to 500K records)
- 🔄 **Real-time Progress**: Live progress tracking for CSV uploads
- 🪝 **Webhooks**: Automated notifications for product events (create/update/delete)
- 🎯 **Simplified Schema**: Optimized with only essential fields (name, SKU, description)
- 🔍 **Smart Duplicate Handling**: Case-insensitive SKU matching
- 💾 **Database**: PostgreSQL with Supabase integration

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Copy `.env.example` to `.env` and configure your database:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DATABASE_URL=postgresql://username:password@host:port/database
```

### 3. Initialize Database
```bash
python reset_db.py
```

### 4. Create Demo Webhooks (Optional)
```bash
python create_demo_webhooks.py
```

### 5. Run Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## File Structure

```
├── run.py                    # Main application runner
├── app_simple.py            # Flask application with routes
├── models.py                # Database models
├── config.py                # Configuration settings
├── reset_db.py              # Database initialization
├── create_demo_webhooks.py  # Demo webhook setup
├── simple_test.csv          # Sample CSV for testing
├── templates/
│   └── index.html          # Web interface
├── .env.example            # Environment template
└── requirements.txt        # Python dependencies
```

## Usage

### Product Management
- **Add Products**: Use the web interface or API endpoints
- **CSV Import**: Upload CSV files with columns: name, sku, description
- **Bulk Operations**: Delete all products at once

### Webhook Management  
- **View Webhooks**: See all configured webhooks and their status
- **Test Webhooks**: Send test requests to verify webhook endpoints
- **Auto-Triggering**: Webhooks automatically fire on product events

### API Endpoints
- `GET /api/products` - List products with pagination
- `POST /api/products` - Create new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product
- `POST /upload` - Upload CSV file
- `GET /api/webhooks` - List webhooks
- `POST /api/webhooks` - Create webhook

## CSV Format

Your CSV file should have these columns:
```csv
name,sku,description
Product Name,SKU123,Product description
Another Product,SKU456,Another description
```

## Development

### Reset Database
```bash
python reset_db.py
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key for sessions

## Production Notes

This is configured for local development. For production deployment:
1. Set `debug=False` in run.py
2. Use a proper WSGI server (gunicorn, uwsgi)
3. Configure environment variables securely
4. Set up proper logging and monitoring

- 📁 **Large CSV Upload**: Import up to 500,000 products with real-time progress tracking
- 🔄 **Background Processing**: Asynchronous processing using Celery and Redis
- 🎯 **Product Management**: Full CRUD operations with filtering and pagination
- 🗑️ **Bulk Operations**: Delete all products with confirmation
- 🔗 **Webhook Management**: Configure and test multiple webhooks
- 🚀 **Cloud Ready**: Deployed on Render with Supabase PostgreSQL

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Celery
- **Database**: Supabase (PostgreSQL)
- **Cache/Queue**: Redis
- **Frontend**: HTML, JavaScript, Bootstrap
- **Deployment**: Render

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables (see `.env.example`)
4. Run the application:
   ```bash
   python app.py
   ```
5. Start Celery worker:
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

## Environment Variables

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
DATABASE_URL=your_supabase_database_url
REDIS_URL=your_redis_url
FLASK_SECRET_KEY=your_secret_key
```

## CSV Format

The application expects a CSV file with the following headers:
- `name`: Product name
- `sku`: Unique product SKU (case-insensitive)
- `description`: Product description

## Deployment

This application is configured for deployment on Render with:
- Automatic builds from Git
- Environment variable configuration
- Background worker processes
- PostgreSQL database (Supabase)
- Redis instance

## API Endpoints

- `POST /upload` - Upload CSV file
- `GET /upload_progress/<task_id>` - Check upload progress
- `GET /api/products` - List products with pagination and filtering
- `POST /api/products` - Create new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product
- `DELETE /api/products/bulk` - Delete all products
- `GET /api/webhooks` - List webhooks
- `POST /api/webhooks` - Create webhook
- `PUT /api/webhooks/<id>` - Update webhook
- `DELETE /api/webhooks/<id>` - Delete webhook
- `POST /api/webhooks/<id>/test` - Test webhook

## License

MIT