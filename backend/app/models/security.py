from datetime import datetime
from ..extensions import db

class APIKey(db.Model):
    """
    Model for tracking Enterprise API Keys.
    Never stores the full key, only the hash and the prefix.
    """
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, nullable=True) # Could link to a future Org model
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    
    # Store prefix for UI identification (e.g., 'sk-live-1a2b...')
    key_prefix = db.Column(db.String(20), nullable=False, unique=True)
    
    # Store secure hash for validation
    key_hash = db.Column(db.String(255), nullable=False)
    
    # Using JSON to store list of APIScope enums
    scopes = db.Column(db.JSON, nullable=False, default=list)
    
    expires_at = db.Column(db.DateTime, nullable=True)
    last_used_at = db.Column(db.DateTime, nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_api_keys_prefix', 'key_prefix'),
    )

class WebhookEndpoint(db.Model):
    """
    Model for managing outbound enterprise webhooks.
    """
    __tablename__ = 'webhook_endpoints'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, nullable=True)
    
    url = db.Column(db.String(1024), nullable=False)
    secret = db.Column(db.String(255), nullable=False) # Used for HMAC signing
    
    subscribed_events = db.Column(db.JSON, nullable=False, default=list)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
