web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: celery -A app.celery worker --loglevel=info --concurrency=2