#!/bin/bash
set -e

echo "=== Build started ==="
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

echo "=== Upgrading pip ==="
python -m pip install --upgrade pip

echo "=== Installing dependencies ==="
pip install --no-cache-dir -r requirements-prod.txt

echo "=== Verifying psycopg2 installation ==="
python -c "import psycopg2; print('✅ psycopg2 imported successfully')"

echo "=== Testing database connection ==="
python test_db.py

echo "=== Build completed ==="