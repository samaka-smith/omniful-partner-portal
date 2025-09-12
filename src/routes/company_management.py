# /home/ubuntu/partner-portal/src/routes/company_management.py
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.company import Company
from src.utils.permissions import check_permissions
from datetime import datetime

company_management_bp = Blueprint('company_management', __name__)

@company_management_bp.route('/companies', methods=['GET'])
@check_permissions('view_companies')
def get_companies():
    """Get all companies (Super Admin only)"""
    try:
        companies = Company.query.all()
        return jsonify([company.to_dict() for company in companies]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_management_bp.route('/companies', methods=['POST'])
@check_permissions('create_company')
def create_company():
    """Create a new company (Super Admin only)"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Company name is required'}), 400
        
        # Check if company already exists
        existing_company = Company.query.filter_by(name=data['name']).first()
        if existing_company:
            return jsonify({'error': 'Company with this name already exists'}), 400
        
        # Create new company
        company = Company(
            name=data['name']
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({
            'message': 'Company created successfully',
            'company': company.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_management_bp.route('/companies/<int:company_id>', methods=['PUT'])
@check_permissions('edit_company')
def update_company(company_id):
    """Update a company (Super Admin only)"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update company name if provided
        if 'name' in data:
            # Check if another company with this name exists
            existing_company = Company.query.filter(
                Company.name == data['name'],
                Company.id != company_id
            ).first()
            if existing_company:
                return jsonify({'error': 'Company with this name already exists'}), 400
            
            company.name = data['name']
        
        company.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Company updated successfully',
            'company': company.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_management_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@check_permissions('delete_company')
def delete_company(company_id):
    """Delete a company (Super Admin only)"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Check if company has associated users or deals
        from src.models.user import User
        from src.models.deal import Deal
        
        users_count = User.query.filter_by(company_id=company_id).count()
        deals_count = Deal.query.filter_by(partner_company_id=company_id).count()
        
        if users_count > 0 or deals_count > 0:
            return jsonify({
                'error': f'Cannot delete company. It has {users_count} users and {deals_count} deals associated with it.'
            }), 400
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({'message': 'Company deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@company_management_bp.route('/companies/<int:company_id>/stats', methods=['GET'])
@check_permissions('view_companies')
def get_company_stats(company_id):
    """Get statistics for a specific company"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        from src.models.user import User
        from src.models.deal import Deal
        
        # Get company statistics
        users_count = User.query.filter_by(company_id=company_id).count()
        deals_count = Deal.query.filter_by(partner_company_id=company_id).count()
        
        # Get deal statistics by status
        deal_stats = db.session.query(
            Deal.status,
            db.func.count(Deal.id).label('count'),
            db.func.sum(Deal.revenue_arr_estimation).label('total_revenue')
        ).filter_by(partner_company_id=company_id).group_by(Deal.status).all()
        
        stats = {
            'company': company.to_dict(),
            'users_count': users_count,
            'deals_count': deals_count,
            'deal_stats': [
                {
                    'status': stat.status,
                    'count': stat.count,
                    'total_revenue': float(stat.total_revenue) if stat.total_revenue else 0
                }
                for stat in deal_stats
            ]
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

