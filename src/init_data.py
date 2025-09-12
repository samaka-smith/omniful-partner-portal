#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.company import Company
from src.main import app

def init_database():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if super admin already exists
        admin_user = User.query.filter_by(email='mahmoud.ali@omniful.ai').first()
        if admin_user:
            print("Super admin user already exists!")
            return
        
        # Create Omniful company
        omniful_company = Company.query.filter_by(name='Omniful').first()
        if not omniful_company:
            omniful_company = Company(name='Omniful')
            db.session.add(omniful_company)
            db.session.commit()
            print("Created Omniful company")
        
        # Create super admin user
        admin_user = User(
            full_name='Mahmoud Ali',
            email='mahmoud.ali@omniful.ai',
            role='Portal Administrator',
            company_id=omniful_company.id,
            force_password_change=True
        )
        admin_user.set_password('TempPass123!')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Database initialized successfully!")
        print(f"Super admin created: {admin_user.email}")
        print("Temporary password: TempPass123!")
        print("User will be forced to change password on first login.")

if __name__ == '__main__':
    init_database()

