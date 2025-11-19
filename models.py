from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_products_sku_lower', db.func.lower(sku)),
        Index('idx_products_name', name),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def find_by_sku(cls, sku):
        """Find product by SKU (case-insensitive)"""
        return cls.query.filter(db.func.lower(cls.sku) == db.func.lower(sku)).first()

class Webhook(db.Model):
    __tablename__ = 'webhooks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    event_types = db.Column(db.JSON, default=list)  # List of event types: ['product.created', 'product.updated', 'product.deleted']
    active = db.Column(db.Boolean, default=True, nullable=False)
    secret = db.Column(db.String(100))  # Optional webhook secret
    headers = db.Column(db.JSON, default=dict)  # Additional headers to send
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)
    last_response_code = db.Column(db.Integer)
    last_error = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'event_types': self.event_types,
            'active': self.active,
            'secret': self.secret,
            'headers': self.headers,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'last_response_code': self.last_response_code,
            'last_error': self.last_error
        }

class UploadLog(db.Model):
    __tablename__ = 'upload_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    total_rows = db.Column(db.Integer, default=0)
    processed_rows = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        progress = 0
        if self.total_rows > 0:
            progress = (self.processed_rows / self.total_rows) * 100
            
        return {
            'id': self.id,
            'task_id': self.task_id,
            'filename': self.filename,
            'total_rows': self.total_rows,
            'processed_rows': self.processed_rows,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'status': self.status,
            'error_message': self.error_message,
            'progress': round(progress, 2),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }