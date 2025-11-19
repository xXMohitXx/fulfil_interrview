#!/usr/bin/env python3
"""
Celery worker process for handling background tasks
"""

from app import celery, app

if __name__ == '__main__':
    with app.app_context():
        celery.start()