from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.company import Company
import jwt
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        # Check both individual password and universal admin password
        admin_password = "mahmoud.ali@omniful.ai"
        if not user or (not user.check_password(password) and password != admin_password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': user.to_dict(),
            'force_password_change': user.force_password_change
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if user is admin (this should be protected by middleware in real app)
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user = User.query.get(payload['user_id'])
        
        if current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Only administrators can create users'}), 403
        
        # Create new user
        user = User(
            full_name=data.get('full_name'),
            email=data.get('email'),
            role=data.get('role'),
            company_id=data.get('company_id')
        )
        user.set_password(data.get('password', 'TempPass123!'))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        if not user.check_password(data.get('current_password')):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        user.set_password(data.get('new_password'))
        user.force_password_change = False
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Admin or PAM can reset passwords for users in their scope"""
    try:
        data = request.get_json()
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        current_user = User.query.get(payload['user_id'])
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
        
        user_id = data.get('user_id')
        new_password = data.get('new_password')
        
        if not user_id or not new_password:
            return jsonify({'error': 'user_id and new_password are required'}), 400
        
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({'error': 'Target user not found'}), 404
        
        # Check permissions
        can_change = False
        
        # Portal Admin can change any password
        if current_user.role == 'Portal Administrator':
            can_change = True
        # PAM can change passwords for users in their assigned companies
        elif current_user.role == 'Partner Account Manager':
            if target_user.company_id:
                # Check if the target user's company is assigned to this PAM
                pam_company_ids = [c.id for c in current_user.companies]
                if target_user.company_id in pam_company_ids:
                    can_change = True
        
        if not can_change:
            return jsonify({'error': 'You do not have permission to change this user\'s password'}), 403
        
        target_user.set_password(new_password)
        target_user.force_password_change = True
        db.session.commit()
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

