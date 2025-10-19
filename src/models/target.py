from src.models.user import db
from datetime import datetime

class Target(db.Model):
    __tablename__ = 'targets'
    
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50), nullable=False)  # PAM, Company, SPOC
    target_entity_id = db.Column(db.Integer, nullable=False)  # ID of PAM, Company, or SPOC
    target_metric = db.Column(db.String(50), nullable=False)  # deals_count, revenue, won_deals
    target_value = db.Column(db.Numeric(15, 2), nullable=False)
    target_period = db.Column(db.String(50), nullable=False)  # monthly, quarterly, yearly
    description = db.Column(db.Text, nullable=True)  # Optional description for the target
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Target {self.target_type} {self.target_period}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'target_type': self.target_type,
            'target_entity_id': self.target_entity_id,
            'target_metric': self.target_metric,
            'target_value': float(self.target_value) if self.target_value else None,
            'target_period': self.target_period,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

