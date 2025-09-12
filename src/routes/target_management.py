# /home/ubuntu/partner-portal/src/routes/target_management.py
from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.company import Company
from src.models.target import Target
from src.models.deal import Deal
from src.utils.permissions import check_permissions
from datetime import datetime, date
from sqlalchemy import func

target_management_bp = Blueprint('target_management', __name__)

@target_management_bp.route('/targets', methods=['GET'])
@check_permissions('manage_targets')
def get_all_targets():
    """Get all targets with current progress"""
    try:
        targets = Target.query.all()
        targets_data = []
        
        for target in targets:
            target_dict = target.to_dict()
            
            # Calculate current progress
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            if target.target_type == 'PAM':
                # Get deals for this PAM
                pam = User.query.get(target.target_entity_id)
                if pam:
                    target_dict['target_entity_name'] = pam.full_name
                    # Get company IDs for this PAM
                    company_ids = [c.id for c in pam.companies]
                    deals = Deal.query.filter(
                        Deal.partner_company_id.in_(company_ids),
                        func.extract('year', Deal.created_at) == current_year,
                        func.extract('month', Deal.created_at) == current_month
                    ).all()
                else:
                    deals = []
                    target_dict['target_entity_name'] = 'Unknown PAM'
                    
            elif target.target_type == 'Company':
                # Get deals for this company
                company = Company.query.get(target.target_entity_id)
                if company:
                    target_dict['target_entity_name'] = company.name
                    deals = Deal.query.filter(
                        Deal.partner_company_id == target.target_entity_id,
                        func.extract('year', Deal.created_at) == current_year,
                        func.extract('month', Deal.created_at) == current_month
                    ).all()
                else:
                    deals = []
                    target_dict['target_entity_name'] = 'Unknown Company'
                    
            elif target.target_type == 'SPOC':
                # Get deals for this SPOC (user)
                spoc = User.query.get(target.target_entity_id)
                if spoc:
                    target_dict['target_entity_name'] = spoc.full_name
                    deals = Deal.query.filter(
                        Deal.created_by == target.target_entity_id,
                        func.extract('year', Deal.created_at) == current_year,
                        func.extract('month', Deal.created_at) == current_month
                    ).all()
                else:
                    deals = []
                    target_dict['target_entity_name'] = 'Unknown SPOC'
            else:
                deals = []
                target_dict['target_entity_name'] = 'Unknown'
            
            # Calculate progress based on target metric
            if target.target_metric == 'deals_count':
                current_value = len(deals)
            elif target.target_metric == 'revenue':
                current_value = sum(deal.revenue_arr_estimation or 0 for deal in deals)
            elif target.target_metric == 'won_deals':
                current_value = len([d for d in deals if d.status == 'Won'])
            else:
                current_value = 0
            
            target_dict['current_value'] = current_value
            target_dict['progress_percentage'] = (current_value / target.target_value * 100) if target.target_value > 0 else 0
            target_dict['is_achieved'] = current_value >= target.target_value
            
            targets_data.append(target_dict)
        
        return jsonify(targets_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@target_management_bp.route('/targets', methods=['POST'])
@check_permissions('manage_targets')
def create_target():
    """Create a new target"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['target_type', 'target_entity_id', 'target_metric', 'target_value', 'target_period']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate target type
        valid_types = ['PAM', 'Company', 'SPOC']
        if data['target_type'] not in valid_types:
            return jsonify({'error': f'Invalid target type. Valid types: {", ".join(valid_types)}'}), 400
        
        # Validate target metric
        valid_metrics = ['deals_count', 'revenue', 'won_deals']
        if data['target_metric'] not in valid_metrics:
            return jsonify({'error': f'Invalid target metric. Valid metrics: {", ".join(valid_metrics)}'}), 400
        
        # Validate target period
        valid_periods = ['monthly', 'quarterly', 'yearly']
        if data['target_period'] not in valid_periods:
            return jsonify({'error': f'Invalid target period. Valid periods: {", ".join(valid_periods)}'}), 400
        
        # Validate entity exists
        if data['target_type'] == 'PAM':
            entity = User.query.filter_by(id=data['target_entity_id'], role='Partner Account Manager').first()
            if not entity:
                return jsonify({'error': 'PAM not found'}), 404
        elif data['target_type'] == 'Company':
            entity = Company.query.get(data['target_entity_id'])
            if not entity:
                return jsonify({'error': 'Company not found'}), 404
        elif data['target_type'] == 'SPOC':
            entity = User.query.filter_by(id=data['target_entity_id'], role='Partner SPOC Admin').first()
            if not entity:
                return jsonify({'error': 'SPOC not found'}), 404
        
        # Check for existing target
        existing_target = Target.query.filter_by(
            target_type=data['target_type'],
            target_entity_id=data['target_entity_id'],
            target_metric=data['target_metric'],
            target_period=data['target_period']
        ).first()
        
        if existing_target:
            return jsonify({'error': 'Target already exists for this entity, metric, and period'}), 400
        
        # Create new target
        target = Target(
            target_type=data['target_type'],
            target_entity_id=data['target_entity_id'],
            target_metric=data['target_metric'],
            target_value=data['target_value'],
            target_period=data['target_period'],
            description=data.get('description', '')
        )
        
        db.session.add(target)
        db.session.commit()
        
        return jsonify({
            'message': 'Target created successfully',
            'target': target.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@target_management_bp.route('/targets/<int:target_id>', methods=['PUT'])
@check_permissions('manage_targets')
def update_target(target_id):
    """Update an existing target"""
    try:
        target = Target.query.get(target_id)
        if not target:
            return jsonify({'error': 'Target not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'target_value' in data:
            target.target_value = data['target_value']
        
        if 'description' in data:
            target.description = data['description']
        
        if 'target_metric' in data:
            valid_metrics = ['deals_count', 'revenue', 'won_deals']
            if data['target_metric'] not in valid_metrics:
                return jsonify({'error': f'Invalid target metric. Valid metrics: {", ".join(valid_metrics)}'}), 400
            target.target_metric = data['target_metric']
        
        if 'target_period' in data:
            valid_periods = ['monthly', 'quarterly', 'yearly']
            if data['target_period'] not in valid_periods:
                return jsonify({'error': f'Invalid target period. Valid periods: {", ".join(valid_periods)}'}), 400
            target.target_period = data['target_period']
        
        target.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Target updated successfully',
            'target': target.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@target_management_bp.route('/targets/<int:target_id>', methods=['DELETE'])
@check_permissions('manage_targets')
def delete_target(target_id):
    """Delete a target"""
    try:
        target = Target.query.get(target_id)
        if not target:
            return jsonify({'error': 'Target not found'}), 404
        
        db.session.delete(target)
        db.session.commit()
        
        return jsonify({'message': 'Target deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@target_management_bp.route('/targets/entities', methods=['GET'])
@check_permissions('manage_targets')
def get_target_entities():
    """Get all entities that can have targets set"""
    try:
        # Get all PAMs
        pams = User.query.filter_by(role='Partner Account Manager').all()
        pam_data = [{'id': pam.id, 'name': pam.full_name, 'type': 'PAM'} for pam in pams]
        
        # Get all companies
        companies = Company.query.all()
        company_data = [{'id': company.id, 'name': company.name, 'type': 'Company'} for company in companies]
        
        # Get all SPOCs
        spocs = User.query.filter_by(role='Partner SPOC Admin').all()
        spoc_data = [{'id': spoc.id, 'name': spoc.full_name, 'type': 'SPOC'} for spoc in spocs]
        
        return jsonify({
            'pams': pam_data,
            'companies': company_data,
            'spocs': spoc_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@target_management_bp.route('/targets/metrics', methods=['GET'])
def get_target_metrics():
    """Get available target metrics and periods"""
    return jsonify({
        'metrics': [
            {'value': 'deals_count', 'label': 'Number of Deals'},
            {'value': 'revenue', 'label': 'Revenue (ARR)'},
            {'value': 'won_deals', 'label': 'Won Deals Count'}
        ],
        'periods': [
            {'value': 'monthly', 'label': 'Monthly'},
            {'value': 'quarterly', 'label': 'Quarterly'},
            {'value': 'yearly', 'label': 'Yearly'}
        ]
    }), 200

