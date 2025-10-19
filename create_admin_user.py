#!/usr/bin/env python3
"""
Create the Portal Admin user: mahmoud@portal.omniful
"""
import os
import sys
from src.main import app, db
from src.models.user import User
from src.models.company import Company
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        
        # Check if Omniful company exists
        omniful_company = Company.query.filter_by(name='Omniful').first()
        if not omniful_company:
            omniful_company = Company(
                name='Omniful',
                company_type='Partner',
                partner_stage='Strategic',
                published_on_website=True
            )
            db.session.add(omniful_company)
            db.session.commit()
            print("✓ Created Omniful company")
        else:
            print("✓ Omniful company already exists")
        
        # Check if the new admin user exists
        admin_email = 'mahmoud@portal.omniful'
        admin_user = User.query.filter_by(email=admin_email).first()
        
        if not admin_user:
            admin_user = User(
                username='Mahmoud Portal Admin',
                email=admin_email,
                password_hash=generate_password_hash('Admin123'),
                role='Portal Administrator',
                company_id=omniful_company.id,
                status='active',
                force_password_change=False  # Don't force password change for this admin
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"✓ Created Portal Admin user: {admin_email}")
            print(f"  Password: Admin123")
        else:
            # Update existing user with correct password
            admin_user.password_hash = generate_password_hash('Admin123')
            admin_user.role = 'Portal Administrator'
            admin_user.force_password_change = False
            admin_user.status = 'active'
            db.session.commit()
            print(f"✓ Updated Portal Admin user: {admin_email}")
            print(f"  Password: Admin123")
        
        print("\n✅ Admin user setup completed successfully!")
        print(f"\nLogin credentials:")
        print(f"  Email: {admin_email}")
        print(f"  Password: Admin123")

if __name__ == '__main__':
    create_admin_user()

