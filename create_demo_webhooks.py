#!/usr/bin/env python3
"""
Demo webhook creation script
Creates sample webhooks for testing the webhook functionality
"""
from app import app
from models import db, Webhook

def create_demo_webhooks():
    with app.app_context():
        try:
            # Clear existing webhooks
            Webhook.query.delete()
            
            # Create demo webhooks
            demo_webhooks = [
                {
                    'name': 'Product Sync Webhook',
                    'url': 'https://webhook.site/unique-id-1',
                    'event_types': ['product.created', 'product.updated'],
                    'active': True,
                    'secret': 'demo_secret_123',
                    'headers': {'Authorization': 'Bearer demo_token_123'}
                },
                {
                    'name': 'Inventory Notification',
                    'url': 'https://httpbin.org/post',
                    'event_types': ['product.created', 'product.deleted'],
                    'active': True,
                    'secret': '',
                    'headers': {'Content-Type': 'application/json', 'X-API-Key': 'demo_api_key'}
                },
                {
                    'name': 'Analytics Tracker',
                    'url': 'https://jsonplaceholder.typicode.com/posts',
                    'event_types': ['product.updated'],
                    'active': False,
                    'secret': 'analytics_secret_456',
                    'headers': {}
                },
                {
                    'name': 'Slack Notifications',
                    'url': 'https://hooks.slack.com/services/demo/demo/demo',
                    'event_types': ['product.created', 'product.updated', 'product.deleted'],
                    'active': True,
                    'secret': '',
                    'headers': {'Content-Type': 'application/json'}
                },
                {
                    'name': 'External Database Sync',
                    'url': 'https://postman-echo.com/post',
                    'event_types': ['product.created', 'product.updated'],
                    'active': True,
                    'secret': 'external_db_secret_789',
                    'headers': {'Authorization': 'Bearer external_token', 'X-Source': 'product-system'}
                }
            ]
            
            for webhook_data in demo_webhooks:
                webhook = Webhook(
                    name=webhook_data['name'],
                    url=webhook_data['url'],
                    event_types=webhook_data['event_types'],
                    active=webhook_data['active'],
                    secret=webhook_data['secret'],
                    headers=webhook_data['headers']
                )
                db.session.add(webhook)
            
            db.session.commit()
            print(f"Successfully created {len(demo_webhooks)} demo webhooks!")
            
            # List created webhooks
            webhooks = Webhook.query.all()
            print("\nDemo Webhooks Created:")
            print("-" * 50)
            for webhook in webhooks:
                status = "✅ Active" if webhook.active else "❌ Inactive"
                print(f"{webhook.name} - {status}")
                print(f"  URL: {webhook.url}")
                print(f"  Events: {', '.join(webhook.event_types)}")
                print()
            
        except Exception as e:
            print(f"Error creating demo webhooks: {e}")
            return False
    
    return True

if __name__ == "__main__":
    create_demo_webhooks()