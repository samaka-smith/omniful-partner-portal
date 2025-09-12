from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.company import Company
import jwt
import os

company_bp = Blueprint('company', __name__)

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

@company_bp.route('/companies', methods=['GET'])
def get_companies():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Role-based filtering
        if current_user.role == 'Portal Administrator':
            companies = Company.query.all()
        elif current_user.role == 'Partner Account Manager':
            # PAM can see assigned companies (for now, all companies)
            companies = Company.query.all()
        elif current_user.role == 'Partner SPOC Admin':
            # SPOC can only see their own company
            companies = Company.query.filter_by(id=current_user.company_id).all()
        else:
            # View only users can see assigned companies
            companies = Company.query.filter_by(id=current_user.company_id).all()
        
        return jsonify([company.to_dict() for company in companies]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Check permissions
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            current_user.company_id != company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify(company.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/companies', methods=['POST'])
def create_company():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        if current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Only administrators can create companies'}), 403
        
        data = request.get_json()
        
        company = Company(
            name=data.get('name')
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({'message': 'Company created successfully', 'company': company.to_dict()}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        if current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Only administrators can update companies'}), 403
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        data = request.get_json()
        company.name = data.get('name', company.name)
        
        db.session.commit()
        
        return jsonify({'message': 'Company updated successfully', 'company': company.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        if current_user.role != 'Portal Administrator':
            return jsonify({'error': 'Only administrators can delete companies'}), 403
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({'message': 'Company deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

