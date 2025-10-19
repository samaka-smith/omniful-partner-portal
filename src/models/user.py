from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Import the association table for PAM-Company relationships
from src.models.pam_company_association import pam_company_association

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Portal Administrator, Partner Account Manager, Partner SPOC Admin, Partner Team Member, View only users
    # For PAMs, we'll use a simple approach - store assigned companies in a separate table
    # but for now, let's use the primary company_id for all users
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    force_password_change = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Relationship for PAM assigned companies
    companies = db.relationship('Company', secondary='pam_company_association', backref='pams', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'company_id': self.company_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'force_password_change': self.force_password_change
        }
