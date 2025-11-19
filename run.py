#!/usr/bin/env python3
"""
Main application runner
Run this file to start the Flask application locally
"""
from app_simple import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)