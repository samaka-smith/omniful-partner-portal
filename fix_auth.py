#!/usr/bin/env python3
"""
Authentication Fix Script for Partner Portal
This script will diagnose and fix the login authentication issues
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User
from src.models.company import Company
from flask import Flask

# Create Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def diagnose_database():
    """Diagnose the current state of the database"""
    print("🔍 DIAGNOSING DATABASE...")
    
    with app.app_context():
        # Check if tables exist
        try:
            user_count = User.query.count()
            company_count = Company.query.count()
            print(f"✅ Database accessible - Users: {user_count}, Companies: {company_count}")
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
        
        # Check for super admin user
        admin_user = User.query.filter_by(email='mahmoud.ali@omniful.ai').first()
        if admin_user:
            print(f"✅ Super admin user found: {admin_user.username}")
            print(f"   - Role: {admin_user.role}")
            print(f"   - Status: {admin_user.status}")
            print(f"   - Force password change: {admin_user.force_password_change}")
            
            # Test password verification
            master_password = 'mahmoud.ali@omniful.ai'
            if check_password_hash(admin_user.password_hash, master_password):
                print(f"✅ Password verification PASSED for master password")
            else:
                print(f"❌ Password verification FAILED for master password")
                return False
        else:
            print("❌ Super admin user NOT FOUND")
            return False
    
    return True

def fix_authentication():
    """Fix the authentication by recreating the super admin user"""
    print("\n🛠️ FIXING AUTHENTICATION...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Ensure Omniful company exists
        omniful_company = Company.query.filter_by(name='Omniful').first()
        if not omniful_company:
            omniful_company = Company(name='Omniful')
            db.session.add(omniful_company)
            db.session.commit()
            print("✅ Created Omniful company")
        
        # Remove existing super admin user if exists
        existing_admin = User.query.filter_by(email='mahmoud.ali@omniful.ai').first()
        if existing_admin:
            db.session.delete(existing_admin)
            db.session.commit()
            print("✅ Removed existing super admin user")
        
        # Create new super admin user with master password
        master_password = 'mahmoud.ali@omniful.ai'
        password_hash = generate_password_hash(master_password)
        
        admin_user = User(
            username='Mahmoud Ali',
            email='mahmoud.ali@omniful.ai',
            password_hash=password_hash,
            role='Portal Administrator',
            company_id=omniful_company.id,
            status='active',
            force_password_change=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Created new super admin user with master password")
        
        # Verify the new user
        verification_user = User.query.filter_by(email='mahmoud.ali@omniful.ai').first()
        if verification_user and check_password_hash(verification_user.password_hash, master_password):
            print("✅ Super admin user verification PASSED")
            return True
        else:
            print("❌ Super admin user verification FAILED")
            return False

def main():
    """Main function to run the authentication fix"""
    print("🚀 PARTNER PORTAL AUTHENTICATION FIX")
    print("=" * 50)
    
    # Step 1: Diagnose current state
    if diagnose_database():
        print("\n✅ Database diagnosis PASSED - Authentication should work")
        return
    
    # Step 2: Fix authentication
    if fix_authentication():
        print("\n🎉 AUTHENTICATION FIX COMPLETED SUCCESSFULLY!")
        print("\nCredentials:")
        print("Email: mahmoud.ali@omniful.ai")
        print("Password: mahmoud.ali@omniful.ai")
    else:
        print("\n❌ AUTHENTICATION FIX FAILED")
        return
    
    # Step 3: Final verification
    print("\n🔍 FINAL VERIFICATION...")
    if diagnose_database():
        print("✅ Final verification PASSED - Ready for deployment!")
    else:
        print("❌ Final verification FAILED")

if __name__ == '__main__':
    main()

