#!/bin/bash

# Start script for the web service
echo "Starting Flask application..."

# Initialize database tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Start the application with Gunicorn
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120