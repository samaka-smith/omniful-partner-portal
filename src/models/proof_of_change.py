# /home/ubuntu/partner-portal/src/models/proof_of_change.py
from src.models.user import db

class ProofOfChange(db.Model):
    __tablename__ = 'proof_of_change'

    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deals.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    previous_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    proof_type = db.Column(db.String(50), nullable=False)  # 'link' or 'file'
    proof_content = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    deal = db.relationship('Deal', back_populates='status_changes')
    user = db.relationship('User')


