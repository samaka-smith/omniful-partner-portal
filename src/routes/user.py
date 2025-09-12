from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.company import Company
import jwt
import os

user_bp = Blueprint('user', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return User.query.get(payload['user_id'])
    except:
        return None

@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        if current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Only administrators can view all users'}), 403
        
        users = User.query.all()
        users_data = []
        
        for user in users:
            user_dict = user.to_dict()
            # Add company name
            if user.company_id:
                company = Company.query.get(user.company_id)
                user_dict['company_name'] = company.name if company else None
            else:
                user_dict['company_name'] = None
            users_data.append(user_dict)
        
        return jsonify(users_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Users can view their own profile, admins can view any profile
        if current_user.id != user_id and current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_dict = user.to_dict()
        # Add company name
        if user.company_id:
            company = Company.query.get(user.company_id)
            user_dict['company_name'] = company.name if company else None
        else:
            user_dict['company_name'] = None
        
        return jsonify(user_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Users can update their own profile, admins can update any profile
        if current_user.id != user_id and current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        # Only admins can change role and company
        if current_user.role == 'Portal Administrator':
            if 'role' in data:
                user.role = data['role']
            if 'company_id' in data:
                user.company_id = data['company_id']
        
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully', 'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        if current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Only administrators can delete users'}), 403
        
        # Prevent self-deletion
        if current_user.id == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
