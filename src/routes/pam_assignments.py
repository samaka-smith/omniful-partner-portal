# /home/ubuntu/partner-portal/src/routes/pam_assignments.py
from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.company import Company
from src.models.pam_company_association import pam_company_association
from src.utils.permissions import check_permissions
from datetime import datetime

pam_assignments_bp = Blueprint('pam_assignments', __name__)

@pam_assignments_bp.route('/users/<int:user_id>/companies', methods=['GET'])
@check_permissions('view_users')
def get_user_companies(user_id):
    """Get companies assigned to a PAM"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'Partner Account Manager':
            return jsonify({'error': 'User is not a Partner Account Manager'}), 400
        
        companies = list(user.companies)
        return jsonify([company.to_dict() for company in companies]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pam_assignments_bp.route('/users/<int:user_id>/companies', methods=['POST'])
@check_permissions('edit_user')
def assign_companies_to_pam(user_id):
    """Assign multiple companies to a PAM"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'Partner Account Manager':
            return jsonify({'error': 'User is not a Partner Account Manager'}), 400
        
        data = request.get_json()
        if not data or 'company_ids' not in data:
            return jsonify({'error': 'Company IDs are required'}), 400
        
        company_ids = data['company_ids']
        
        # Validate that all company IDs exist
        companies = Company.query.filter(Company.id.in_(company_ids)).all()
        if len(companies) != len(company_ids):
            return jsonify({'error': 'One or more company IDs are invalid'}), 400
        
        # Clear existing assignments
        user.companies.clear()
        
        # Add new assignments
        for company in companies:
            user.companies.append(company)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Companies assigned successfully',
            'assigned_companies': [company.to_dict() for company in companies]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pam_assignments_bp.route('/users/<int:user_id>/companies/<int:company_id>', methods=['POST'])
@check_permissions('edit_user')
def add_company_to_pam(user_id, company_id):
    """Add a single company to a PAM's assignments"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'Partner Account Manager':
            return jsonify({'error': 'User is not a Partner Account Manager'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Check if already assigned
        if company in user.companies:
            return jsonify({'error': 'Company already assigned to this PAM'}), 400
        
        user.companies.append(company)
        db.session.commit()
        
        return jsonify({
            'message': 'Company assigned successfully',
            'company': company.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pam_assignments_bp.route('/users/<int:user_id>/companies/<int:company_id>', methods=['DELETE'])
@check_permissions('edit_user')
def remove_company_from_pam(user_id, company_id):
    """Remove a company from a PAM's assignments"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role != 'Partner Account Manager':
            return jsonify({'error': 'User is not a Partner Account Manager'}), 400
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Check if assigned
        if company not in user.companies:
            return jsonify({'error': 'Company not assigned to this PAM'}), 400
        
        user.companies.remove(company)
        db.session.commit()
        
        return jsonify({'message': 'Company removed from PAM successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pam_assignments_bp.route('/companies/<int:company_id>/pams', methods=['GET'])
@check_permissions('view_users')
def get_company_pams(company_id):
    """Get all PAMs assigned to a company"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        pams = list(company.pams)
        return jsonify([pam.to_dict() for pam in pams]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pam_assignments_bp.route('/pam-assignments/overview', methods=['GET'])
@check_permissions('view_users')
def get_pam_assignments_overview():
    """Get an overview of all PAM-Company assignments"""
    try:
        # Get all PAMs
        pams = User.query.filter_by(role='Partner Account Manager').all()
        
        assignments = []
        for pam in pams:
            companies = list(pam.companies)
            assignments.append({
                'pam': pam.to_dict(),
                'assigned_companies': [company.to_dict() for company in companies],
                'company_count': len(companies)
            })
        
        return jsonify(assignments), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

