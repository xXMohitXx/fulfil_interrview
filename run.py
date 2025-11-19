#!/usr/bin/env python3
"""
Main application runner
Run this file to start the Flask application locally
"""
import os
from app import app

if __name__ == '__main__':
    # Force local development settings
    os.environ['FLASK_ENV'] = 'development'
    app.run(host='127.0.0.1', port=5000, debug=True)