from src.models.user import db
from datetime import datetime

class Target(db.Model):
    __tablename__ = 'targets'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50), nullable=False)  # monthly, quarterly, yearly
    target_value = db.Column(db.Numeric(15, 2), nullable=False)
    target_period = db.Column(db.String(50), nullable=False)  # e.g., "2025-01", "2025-Q1", "2025"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Target {self.target_type} {self.target_period}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_value': float(self.target_value) if self.target_value else None,
            'target_period': self.target_period,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

