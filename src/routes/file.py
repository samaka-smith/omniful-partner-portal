from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from src.models.user import db, User
from src.models.deal import Deal
from src.models.deal_file import DealFile
import jwt
import os
import uuid
from datetime import datetime

file_bp = Blueprint('file', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
UPLOAD_FOLDER = '/home/ubuntu/partner-portal/uploads'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
    'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'csv'
}

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_bp.route('/files/upload', methods=['POST'])
def upload_file():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        deal_id = request.form.get('deal_id')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not deal_id:
            return jsonify({'error': 'Deal ID is required'}), 400
        
        # Verify deal exists and user has access
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Check user permissions
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            deal.created_by != current_user.id and 
            deal.partner_company_id != current_user.company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        if file and allowed_file(file.filename):
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({'error': 'File size exceeds 5MB limit'}), 400
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Create database record
            deal_file = DealFile(
                deal_id=deal_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                uploaded_by=current_user.id,
                uploaded_at=datetime.utcnow()
            )
            
            db.session.add(deal_file)
            db.session.commit()
            
            return jsonify({
                'message': 'File uploaded successfully',
                'file': deal_file.to_dict()
            }), 201
        
        return jsonify({'error': 'File type not allowed'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/files/deal/<int:deal_id>', methods=['GET'])
def get_deal_files(deal_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Verify deal exists and user has access
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Check user permissions
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            deal.created_by != current_user.id and 
            deal.partner_company_id != current_user.company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        files = DealFile.query.filter_by(deal_id=deal_id).all()
        files_data = []
        
        for file in files:
            file_dict = file.to_dict()
            # Add uploader name
            uploader = User.query.get(file.uploaded_by)
            file_dict['uploader_name'] = uploader.full_name if uploader else 'Unknown'
            files_data.append(file_dict)
        
        return jsonify(files_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        deal_file = DealFile.query.get(file_id)
        if not deal_file:
            return jsonify({'error': 'File not found'}), 404
        
        # Verify deal access
        deal = Deal.query.get(deal_file.deal_id)
        if not deal:
            return jsonify({'error': 'Associated deal not found'}), 404
        
        # Check user permissions
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            deal.created_by != current_user.id and 
            deal.partner_company_id != current_user.company_id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if file exists on disk
        if not os.path.exists(deal_file.file_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        return send_file(
            deal_file.file_path,
            as_attachment=True,
            download_name=deal_file.filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        deal_file = DealFile.query.get(file_id)
        if not deal_file:
            return jsonify({'error': 'File not found'}), 404
        
        # Verify deal access
        deal = Deal.query.get(deal_file.deal_id)
        if not deal:
            return jsonify({'error': 'Associated deal not found'}), 404
        
        # Check user permissions (only uploader, admins, or PAMs can delete)
        if (current_user.role not in ['Portal Administrator', 'Partner Account Manager'] and 
            deal_file.uploaded_by != current_user.id):
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete file from disk
        if os.path.exists(deal_file.file_path):
            os.remove(deal_file.file_path)
        
        # Delete database record
        db.session.delete(deal_file)
        db.session.commit()
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/files/stats', methods=['GET'])
def get_file_stats():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Authorization required'}), 401
        
        # Get accessible deals based on user role
        if current_user.role in ['Portal Administrator', 'Partner Account Manager']:
            accessible_deals = Deal.query.all()
        else:
            accessible_deals = Deal.query.filter(
                (Deal.created_by == current_user.id) | 
                (Deal.partner_company_id == current_user.company_id)
            ).all()
        
        deal_ids = [deal.id for deal in accessible_deals]
        
        if not deal_ids:
            return jsonify({
                'total_files': 0,
                'total_size': 0,
                'files_by_type': {}
            }), 200
        
        files = DealFile.query.filter(DealFile.deal_id.in_(deal_ids)).all()
        
        total_files = len(files)
        total_size = sum(file.file_size for file in files)
        
        # Group by file type
        files_by_type = {}
        for file in files:
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'unknown'
            files_by_type[ext] = files_by_type.get(ext, 0) + 1
        
        return jsonify({
            'total_files': total_files,
            'total_size': total_size,
            'files_by_type': files_by_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

