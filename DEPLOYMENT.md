# Deployment Guide for Acme Inc Product Import System

This guide will walk you through deploying the Product Import System to Render with Supabase as the database.

## Prerequisites

1. **GitHub Account** - To host your code
2. **Render Account** - For deployment ([render.com](https://render.com))
3. **Supabase Account** - For PostgreSQL database ([supabase.com](https://supabase.com))
4. **Redis Cloud Account** - For Redis (optional, Render provides Redis)

## Step 1: Setup Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the database to be provisioned
3. Go to Settings > Database and note down:
   - `Host` (usually something like `db.xxx.supabase.co`)
   - `Database name` (usually `postgres`)
   - `Username` (usually `postgres`)
   - `Password` (you set this during setup)
   - `Port` (usually `5432`)
4. Go to Settings > API and note down:
   - `Project URL` (this is your SUPABASE_URL)
   - `anon/public` key (this is your SUPABASE_KEY)
5. Construct your DATABASE_URL:
   ```
   postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
   ```

## Step 2: Push Code to GitHub

1. Create a new repository on GitHub
2. Push all the code to your repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

## Step 3: Deploy to Render

### Option A: Using render.yaml (Recommended)

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" and select "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Set the following environment variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `DATABASE_URL`: Your Supabase PostgreSQL connection string
   - `REDIS_URL`: Will be auto-generated when Redis service is created
6. Deploy the services

### Option B: Manual Setup

1. **Create Redis Service**:
   - Go to Render Dashboard
   - Click "New +" → "Redis"
   - Choose "Free" plan
   - Name it `acme-redis`
   - Copy the Internal Redis URL

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `acme-product-import`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
     - **Plan**: Free
   - Set Environment Variables:
     ```
     FLASK_ENV=production
     FLASK_SECRET_KEY=[generate a secure key]
     SUPABASE_URL=[your supabase url]
     SUPABASE_KEY=[your supabase anon key]
     DATABASE_URL=[your supabase database url]
     REDIS_URL=[your redis internal url]
     ```

3. **Create Background Worker**:
   - Click "New +" → "Background Worker"
   - Connect the same GitHub repository
   - Configure:
     - **Name**: `acme-product-worker`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `celery -A app.celery worker --loglevel=info --concurrency=2`
   - Use the same environment variables as the web service

## Step 4: Initialize Database

After deployment, the database tables will be automatically created when the application starts.

If you need to manually initialize:
1. Go to your Render web service logs
2. The tables should be created automatically on first start
3. If not, you can access the Render shell and run:
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
   ```

## Step 5: Test the Application

1. Open your Render web service URL
2. Test file upload with a small CSV file first
3. Test product management features
4. Configure webhooks if needed

## Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `FLASK_SECRET_KEY` | Flask secret key | `your-secret-key-here` |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbG...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:pass@host:5432/postgres` |
| `REDIS_URL` | Redis connection string | `redis://red-xxx:6379` |

## Troubleshooting

### Common Issues:

1. **Database Connection Error**:
   - Verify DATABASE_URL is correct
   - Ensure Supabase project is active
   - Check if IP restrictions are set in Supabase

2. **Redis Connection Error**:
   - Verify REDIS_URL is correct
   - Ensure Redis service is running

3. **File Upload Timeout**:
   - Large files may timeout on free tier
   - Consider upgrading Render plan for longer timeouts
   - Use smaller test files first

4. **Worker Not Processing**:
   - Check worker service logs
   - Verify Redis connection
   - Restart worker service

### Monitoring:

- Check Render service logs for errors
- Monitor database usage in Supabase dashboard
- Watch Redis usage in Render dashboard

## Performance Optimization

For production use, consider:

1. **Upgrading Render Plans**: For better performance and no timeouts
2. **Database Indexing**: Additional indexes for large datasets
3. **Redis Optimization**: Dedicated Redis instance for high volume
4. **File Storage**: Use cloud storage for uploaded files
5. **Monitoring**: Set up application monitoring

## Security Considerations

1. **Environment Variables**: Never commit secrets to git
2. **Database Access**: Use connection pooling for better performance
3. **File Uploads**: Validate file types and sizes
4. **Webhook Security**: Use secrets for webhook verification
5. **HTTPS**: Ensure SSL is enabled (Render provides this automatically)

## Maintenance

- Monitor application logs regularly
- Keep dependencies updated
- Backup database periodically via Supabase
- Monitor resource usage and scale as needed

---

**Note**: The free tier has limitations. For production use with 500K+ records, consider upgrading to paid plans for better performance and reliability.