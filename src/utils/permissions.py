# /home/ubuntu/partner-portal/src/utils/permissions.py
from functools import wraps
from flask import request, jsonify, g
from src.models.user import User
from src.models.company import Company
from src.models.deal import Deal
import jwt

def check_permissions(required_permission):
    """
    Decorator to check if the current user has the required permission.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the current user from the JWT token
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
            
            try:
                token = token.replace('Bearer ', '')
                payload = jwt.decode(token, 'asdf#FGSgvasgf$5$WGT', algorithms=['HS256'])
                user_id = payload['user_id']
                user = User.query.get(user_id)
                
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                g.current_user = user
                
                # Check permissions based on role and required permission
                if has_permission(user, required_permission, **kwargs):
                    return f(*args, **kwargs)
                else:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                    
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
                
        return decorated_function
    return decorator

def has_permission(user, permission, **kwargs):
    """
    Check if a user has a specific permission.
    """
    role = user.role
    
    # Portal Administrator has access to everything
    if role == 'Portal Administrator':
        return True
    
    # Permission-specific checks
    elif permission == 'view_companies':
        return role == 'Portal Administrator'
    
    elif permission == 'create_company':
        return role == 'Portal Administrator'
    
    elif permission == 'edit_company':
        return role == 'Portal Administrator'
    
    elif permission == 'delete_company':
        return role == 'Portal Administrator'
    
    elif permission == 'create_user':
        return role in ['Portal Administrator', 'Partner SPOC Admin']
    
    elif permission == 'edit_user':
        return role in ['Portal Administrator', 'Partner SPOC Admin']
    
    elif permission == 'delete_user':
        return role == 'Portal Administrator'
    
    elif permission == 'create_deal':
        return role in ['Portal Administrator', 'Partner Account Manager', 'Partner SPOC Admin', 'Partner Team Member']
    
    elif permission == 'edit_deal':
        if role == 'Portal Administrator':
            return True
        elif role == 'Partner Account Manager':
            # PAM can edit deals for companies they are assigned to
            deal_id = kwargs.get('deal_id')
            if deal_id:
                deal = Deal.query.get(deal_id)
                if deal:
                    return deal.partner_company_id in [c.id for c in user.companies]
            return False
        elif role == 'Partner SPOC Admin':
            # SPOC Admin can edit deals for their company
            deal_id = kwargs.get('deal_id')
            if deal_id:
                deal = Deal.query.get(deal_id)
                if deal:
                    return deal.partner_company_id == user.company_id
            return False
        else:
            return False
    
    elif permission == 'delete_deal':
        return role == 'Portal Administrator'
    
    elif permission == 'view_analytics':
        return role in ['Portal Administrator', 'Partner Account Manager', 'Partner SPOC Admin']
    
    elif permission == 'manage_targets':
        return role == 'Portal Administrator'
    
    elif permission == 'change_user_password':
        # Portal Admin can change any password
        if role == 'Portal Administrator':
            return True
        # PAM can change passwords for users in their assigned companies
        elif role == 'Partner Account Manager':
            target_user_id = kwargs.get('target_user_id')
            if target_user_id:
                target_user = User.query.get(target_user_id)
                if target_user and target_user.company_id:
                    # Check if the target user's company is assigned to this PAM
                    return target_user.company_id in [c.id for c in user.companies]
            return False
        else:
            return False
    
    elif permission == 'change_user_allocation':
        # Only Portal Admin can change user allocation (company assignment)
        return role == 'Portal Administrator'
    
    else:
        return False

def get_accessible_companies(user):
    """
    Get the list of companies that a user can access based on their role.
    """
    role = user.role
    
    if role == 'Portal Administrator':
        return Company.query.all()
    elif role == 'Partner Account Manager':
        return list(user.companies)
    elif role in ['Partner SPOC Admin', 'Partner Team Member', 'View only users']:
        if user.company_id:
            return [Company.query.get(user.company_id)]
        else:
            return []
    else:
        return []

def get_accessible_deals(user):
    """
    Get the list of deals that a user can access based on their role.
    """
    role = user.role
    
    if role == 'Portal Administrator':
        return Deal.query.all()
    elif role == 'Partner Account Manager':
        company_ids = [c.id for c in user.companies]
        return Deal.query.filter(Deal.partner_company_id.in_(company_ids)).all()
    elif role in ['Partner SPOC Admin', 'Partner Team Member', 'View only users']:
        if user.company_id:
            return Deal.query.filter_by(partner_company_id=user.company_id).all()
        else:
            return []
    else:
        return []

