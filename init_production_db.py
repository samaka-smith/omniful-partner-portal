#!/usr/bin/env python3
"""
Initialize production database with super admin user
"""
import os
from src.main import app, db
from src.models.user import User
from src.models.company import Company
from werkzeug.security import generate_password_hash

def init_production_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if Omniful company exists
        omniful_company = Company.query.filter_by(name='Omniful').first()
        if not omniful_company:
            omniful_company = Company(name='Omniful')
            db.session.add(omniful_company)
            db.session.commit()
            print("Created Omniful company")
        
        # Check if super admin user exists
        admin_user = User.query.filter_by(email='mahmoud.ali@omniful.ai').first()
        if not admin_user:
            admin_user = User(
                username='Mahmoud Ali',
                email='mahmoud.ali@omniful.ai',
                password_hash=generate_password_hash('TempPass123!'),
                role='Portal Administrator',
                company_id=omniful_company.id,
                status='active',
                force_password_change=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created super admin user: mahmoud.ali@omniful.ai")
        else:
            # Update existing user with correct password
            admin_user.password_hash = generate_password_hash('TempPass123!')
            admin_user.force_password_change = True
            db.session.commit()
            print("Updated super admin user password")
        
        print("Production database initialized successfully!")

if __name__ == '__main__':
    init_production_db()

