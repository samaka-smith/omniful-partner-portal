from src.models.user import db
from datetime import datetime

class DealFile(db.Model):
    __tablename__ = 'deal_files'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))  # SOW, GAP Analysis, Workflow, Quotations, Invoices
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DealFile {self.file_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'uploaded_by_user_id': self.uploaded_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

