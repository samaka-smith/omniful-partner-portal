from src.models.user import db
from datetime import datetime

class DealComment(db.Model):
    __tablename__ = 'deal_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DealComment {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'deal_id': self.deal_id,
            'user_id': self.user_id,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_name': self.commenter.full_name if self.commenter else None
        }

