from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.company import Company
from src.models.deal import Deal
from src.models.deal_comment import DealComment
import jwt
import os

deal_bp = Blueprint('deal', __name__)

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

@deal_bp.route('/deals', methods=['GET'])
def get_deals():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Role-based filtering
        if current_user.role == 'Portal Administrator':
            deals = Deal.query.all()
        elif current_user.role == 'Partner Account Manager':
            # PAM can see deals from assigned companies (for now, all deals)
            deals = Deal.query.all()
        elif current_user.role == 'Partner SPOC Admin':
            # SPOC can only see deals from their company
            deals = Deal.query.filter_by(partner_company_id=current_user.company_id).all()
        else:
            # View only users can see deals from assigned companies
            deals = Deal.query.filter_by(partner_company_id=current_user.company_id).all()
        
        deals_data = []
        for deal in deals:
            deal_dict = deal.to_dict()
            # Add partner company name
            partner_company = Company.query.get(deal.partner_company_id)
            deal_dict['partner_company_name'] = partner_company.name if partner_company else None
            # Add creator name
            creator = User.query.get(deal.created_by_user_id)
            deal_dict['creator_name'] = creator.full_name if creator else None
            deals_data.append(deal_dict)
        
        return jsonify(deals_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deal_bp.route('/deals/<int:deal_id>', methods=['GET'])
def get_deal(deal_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Check permissions
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            current_user.company_id != deal.partner_company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        deal_dict = deal.to_dict()
        # Add partner company name
        partner_company = Company.query.get(deal.partner_company_id)
        deal_dict['partner_company_name'] = partner_company.name if partner_company else None
        # Add creator name
        creator = User.query.get(deal.created_by_user_id)
        deal_dict['creator_name'] = creator.full_name if creator else None
        
        return jsonify(deal_dict), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deal_bp.route('/deals', methods=['POST'])
def create_deal():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        if current_user.role == 'View only users':
            return jsonify({'error': 'View only users cannot create deals'}), 403
        
        data = request.get_json()
        
        # Determine partner company based on user role
        if current_user.role == 'Portal Administrator':
            partner_company_id = data.get('partner_company_id')
        elif current_user.role == 'Partner Account Manager':
            # PAM can select from assigned companies (for now, any company)
            partner_company_id = data.get('partner_company_id')
        else:
            # SPOC Admin uses their own company
            partner_company_id = current_user.company_id
        
        deal = Deal(
            partner_company_id=partner_company_id,
            customer_company_name=data.get('customer_company_name'),
            customer_spoc=data.get('customer_spoc'),
            customer_company_url=data.get('customer_company_url'),
            customer_email=data.get('customer_email'),
            customer_spoc_email=data.get('customer_spoc_email'),
            customer_spoc_phone=data.get('customer_spoc_phone'),
            comments=data.get('comments'),
            customer_company_logo=data.get('customer_company_logo'),
            revenue_arr_estimation=data.get('revenue_arr_estimation'),
            status=data.get('status', 'Open'),
            created_by_user_id=current_user.id
        )
        
        db.session.add(deal)
        db.session.commit()
        
        return jsonify({'message': 'Deal created successfully', 'deal': deal.to_dict()}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deal_bp.route('/deals/<int:deal_id>', methods=['PUT'])
def update_deal(deal_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Check permissions
        if (current_user.role == 'View only users' or
            (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
             current_user.company_id != deal.partner_company_id)):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields
        for field in ['partner_company_id', 'customer_company_name', 'customer_spoc', 'customer_company_url',
                     'customer_email', 'customer_spoc_email', 'customer_spoc_phone',
                     'comments', 'customer_company_logo', 'revenue_arr_estimation', 'status']:
            if field in data:
                setattr(deal, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': 'Deal updated successfully', 'deal': deal.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deal_bp.route('/deals/<int:deal_id>/comments', methods=['GET'])
def get_deal_comments(deal_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Check permissions
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            current_user.company_id != deal.partner_company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        comments = DealComment.query.filter_by(deal_id=deal_id).order_by(DealComment.created_at.desc()).all()
        
        return jsonify([comment.to_dict() for comment in comments]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deal_bp.route('/deals/<int:deal_id>/comments', methods=['POST'])
def add_deal_comment(deal_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Check permissions
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            current_user.company_id != deal.partner_company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        comment = DealComment(
            deal_id=deal_id,
            user_id=current_user.id,
            comment=data.get('comment')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comment added successfully', 'comment': comment.to_dict()}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

