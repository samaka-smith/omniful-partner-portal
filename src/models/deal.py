from src.models.user import db
from datetime import datetime

class Deal(db.Model):
    __tablename__ = 'deals'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    customer_company_name = db.Column(db.String(255), nullable=False)
    customer_spoc = db.Column(db.String(255), nullable=False)
    customer_company_url = db.Column(db.String(255))
    customer_email = db.Column(db.String(255))
    customer_spoc_email = db.Column(db.String(255))
    customer_spoc_phone = db.Column(db.String(50))
    comments = db.Column(db.Text)
    customer_company_logo = db.Column(db.String(255))
    revenue_arr_estimation = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(50), default='Open')  # Open, New, Qualification, Demo1, Demo2, Proposal, Negotiation, Won, Lost
    status_changes = db.relationship('ProofOfChange', back_populates='deal', cascade='all, delete-orphan')
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = db.relationship('DealFile', backref='deal', lazy=True, cascade='all, delete-orphan')
    deal_comments = db.relationship('DealComment', backref='deal', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Deal {self.customer_company_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'partner_company_id': self.partner_company_id,
            'customer_company_name': self.customer_company_name,
            'customer_spoc': self.customer_spoc,
            'customer_company_url': self.customer_company_url,
            'customer_email': self.customer_email,
            'customer_spoc_email': self.customer_spoc_email,
            'customer_spoc_phone': self.customer_spoc_phone,
            'comments': self.comments,
            'customer_company_logo': self.customer_company_logo,
            'revenue_arr_estimation': float(self.revenue_arr_estimation) if self.revenue_arr_estimation else None,
            'status': self.status,
            'created_by_user_id': self.created_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

