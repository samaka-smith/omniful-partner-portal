# /home/ubuntu/partner-portal/src/routes/user_creation.py
from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.company import Company
from src.utils.permissions import check_permissions
from datetime import datetime

user_creation_bp = Blueprint('user_creation', __name__)

@user_creation_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user - Portal Admin can create any user, PAM can only create users for their assigned companies"""
    try:
        # Get current user from token
        from flask import g
        import jwt
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization required'}), 401
        
        try:
            token = token.replace('Bearer ', '')
            payload = jwt.decode(token, 'asdf#FGSgvasgf$5$WGT', algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Validate role
        valid_roles = [
            'Portal Administrator', 
            'Partner Account Manager', 
            'Partner SPOC Admin', 
            'Partner Team Member', 
            'View only users'
        ]
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Invalid role. Valid roles: {", ".join(valid_roles)}'}), 400
        
        # Validate company if provided
        company_id = data.get('company_id')
        if company_id:
            company = Company.query.get(company_id)
            if not company:
                return jsonify({'error': 'Invalid company ID'}), 400
            
            # PAM can only create users for companies they manage
            if current_user.role == 'Partner Account Manager':
                pam_company_ids = [c.id for c in current_user.companies]
                if company_id not in pam_company_ids:
                    return jsonify({'error': 'You can only create users for companies you manage'}), 403
        elif current_user.role == 'Partner Account Manager':
            # PAM must specify a company_id
            return jsonify({'error': 'Partner Account Managers must specify a company_id when creating users'}), 400
        
        # Only Portal Admin can create users
        if current_user.role not in ['Portal Administrator', 'Partner Account Manager']:
            return jsonify({'error': 'Insufficient permissions to create users'}), 403
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role=data['role'],
            company_id=company_id if company_id else None
        )
        
        # Set default password
        default_password = data.get('password', 'TempPass123!')
        user.set_password(default_password)
        user.force_password_change = True
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        # Return success response
        user_dict = user.to_dict()
        if company_id:
            company = Company.query.get(company_id)
            user_dict['company_name'] = company.name if company else None
        
        return jsonify({
            'message': 'User created successfully',
            'user': user_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

@user_creation_bp.route('/users/<int:user_id>', methods=['PUT'])
@check_permissions('edit_user')
def update_user(user_id):
    """Update an existing user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already taken by another user'}), 400
            user.email = data['email']
        
        if 'role' in data:
            valid_roles = [
                'Portal Administrator', 
                'Partner Account Manager', 
                'Partner SPOC Admin', 
                'Partner Team Member', 
                'View only users'
            ]
            if data['role'] not in valid_roles:
                return jsonify({'error': f'Invalid role. Valid roles: {", ".join(valid_roles)}'}), 400
            user.role = data['role']
        
        if 'company_id' in data:
            company_id = data['company_id']
            if company_id:
                company = Company.query.get(company_id)
                if not company:
                    return jsonify({'error': 'Invalid company ID'}), 400
            user.company_id = company_id
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Return updated user
        user_dict = user.to_dict()
        if user.company_id:
            company = Company.query.get(user.company_id)
            user_dict['company_name'] = company.name if company else None
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_dict
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update user: {str(e)}'}), 500

@user_creation_bp.route('/users/<int:user_id>', methods=['DELETE'])
@check_permissions('delete_user')
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deletion of the last Portal Administrator
        if user.role == 'Portal Administrator':
            admin_count = User.query.filter_by(role='Portal Administrator').count()
            if admin_count <= 1:
                return jsonify({'error': 'Cannot delete the last Portal Administrator'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete user: {str(e)}'}), 500

