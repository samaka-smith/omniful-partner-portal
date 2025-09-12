# /home/ubuntu/partner-portal/src/models/pam_company_association.py
from src.models.user import db

pam_company_association = db.Table('pam_company_association',
    db.Column('pam_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey('companies.id'), primary_key=True)
)


