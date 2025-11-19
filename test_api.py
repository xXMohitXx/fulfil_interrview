#!/usr/bin/env python3
"""
Test script for the Product Import System
Run this to test basic functionality locally
"""

import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:5000"  # Change this to your deployed URL

def test_api():
    print("🧪 Testing Product Import System API")
    print("=" * 50)
    
    # Test 1: Create a product
    print("📝 Test 1: Creating a test product...")
    product_data = {
        "name": "Test Product",
        "sku": "TEST-001",
        "description": "This is a test product",
        "active": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/products", json=product_data)
        if response.status_code == 201:
            print("✅ Product created successfully!")
            product_id = response.json()['id']
        else:
            print(f"❌ Failed to create product: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 2: Get products
    print("\n📋 Test 2: Fetching products...")
    try:
        response = requests.get(f"{BASE_URL}/api/products")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['products'])} products")
            print(f"   Total products in database: {data['total']}")
        else:
            print(f"❌ Failed to fetch products: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    # Test 3: Update product
    print(f"\n📝 Test 3: Updating product {product_id}...")
    update_data = {
        "name": "Updated Test Product",
        "description": "This product has been updated"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/products/{product_id}", json=update_data)
        if response.status_code == 200:
            print("✅ Product updated successfully!")
        else:
            print(f"❌ Failed to update product: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    # Test 4: Create webhook
    print("\n🔗 Test 4: Creating a test webhook...")
    webhook_data = {
        "name": "Test Webhook",
        "url": "https://webhook.site/unique-id",  # Use a real webhook.site URL for testing
        "event_types": ["product.created", "product.updated"],
        "active": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/webhooks", json=webhook_data)
        if response.status_code == 201:
            print("✅ Webhook created successfully!")
            webhook_id = response.json()['id']
        else:
            print(f"❌ Failed to create webhook: {response.text}")
            webhook_id = None
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        webhook_id = None
    
    # Test 5: Test webhook (if created)
    if webhook_id:
        print(f"\n🔔 Test 5: Testing webhook {webhook_id}...")
        try:
            response = requests.post(f"{BASE_URL}/api/webhooks/{webhook_id}/test")
            if response.status_code == 200:
                print("✅ Webhook test triggered!")
            else:
                print(f"❌ Failed to test webhook: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
    
    # Test 6: Upload CSV file
    print("\n📤 Test 6: Testing CSV upload...")
    try:
        with open('sample_products.csv', 'rb') as f:
            files = {'file': ('sample_products.csv', f, 'text/csv')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            
            if response.status_code == 202:
                task_id = response.json()['task_id']
                print(f"✅ CSV upload started! Task ID: {task_id}")
                
                # Poll for progress
                print("⏳ Waiting for upload to complete...")
                for i in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    try:
                        progress_response = requests.get(f"{BASE_URL}/upload_progress/{task_id}")
                        if progress_response.status_code == 200:
                            progress_data = progress_response.json()
                            status = progress_data.get('status', 'unknown')
                            progress = progress_data.get('progress', 0)
                            
                            if status == 'completed':
                                print(f"✅ Upload completed! Processed {progress_data.get('processed_rows', 0)} rows")
                                print(f"   Success: {progress_data.get('success_count', 0)}, Errors: {progress_data.get('error_count', 0)}")
                                break
                            elif status == 'failed':
                                print(f"❌ Upload failed: {progress_data.get('error', 'Unknown error')}")
                                break
                            elif status == 'processing':
                                print(f"⏳ Progress: {progress:.1f}%")
                    except:
                        pass
                else:
                    print("⏰ Upload is taking longer than expected...")
            else:
                print(f"❌ Failed to upload CSV: {response.text}")
    except FileNotFoundError:
        print("❌ sample_products.csv not found. Please ensure the file exists.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    # Test 7: Cleanup (delete test product)
    print(f"\n🧹 Test 7: Cleaning up test product...")
    try:
        response = requests.delete(f"{BASE_URL}/api/products/{product_id}")
        if response.status_code == 200:
            print("✅ Test product deleted successfully!")
        else:
            print(f"❌ Failed to delete test product: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    # Test 8: Cleanup webhook
    if webhook_id:
        print(f"\n🧹 Test 8: Cleaning up test webhook...")
        try:
            response = requests.delete(f"{BASE_URL}/api/webhooks/{webhook_id}")
            if response.status_code == 200:
                print("✅ Test webhook deleted successfully!")
            else:
                print(f"❌ Failed to delete test webhook: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
    
    print("\n🎉 Test suite completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_api()