# Product Import Application

A scalable Flask web application for importing and managing large CSV datasets (up to 500,000 records) with real-time progress tracking and webhook support.

## Features

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