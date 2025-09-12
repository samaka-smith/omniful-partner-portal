# /home/ubuntu/partner-portal/src/routes/deal_status.py
from flask import Blueprint, request, jsonify, g
from src.models.user import db
from src.models.deal import Deal
from src.models.proof_of_change import ProofOfChange
from src.utils.permissions import check_permissions
from datetime import datetime
import os
from werkzeug.utils import secure_filename

deal_status_bp = Blueprint('deal_status', __name__)

# Define the valid deal statuses
VALID_STATUSES = [
    'New', 'Open', 'Qualified', 'Demo 1', 'Demo 2', 
    'Proposition', 'Negotiation', 'Won', 'Lost'
]

@deal_status_bp.route('/deals/<int:deal_id>/status', methods=['PUT'])
@check_permissions('edit_deal')
def update_deal_status(deal_id):
    """Update deal status with proof of change requirement"""
    try:
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        data = request.get_json()
        if not data or 'new_status' not in data:
            return jsonify({'error': 'New status is required'}), 400
        
        new_status = data['new_status']
        if new_status not in VALID_STATUSES:
            return jsonify({'error': f'Invalid status. Valid options: {", ".join(VALID_STATUSES)}'}), 400
        
        # Check if status is actually changing
        if deal.status == new_status:
            return jsonify({'error': 'Deal is already in this status'}), 400
        
        # Proof of change is required for status updates
        proof_type = data.get('proof_type')  # 'link' or 'file'
        proof_content = data.get('proof_content')
        
        if not proof_type or not proof_content:
            return jsonify({
                'error': 'Proof of change is required. Please provide either a link or upload a file.'
            }), 400
        
        if proof_type not in ['link', 'file']:
            return jsonify({'error': 'Proof type must be either "link" or "file"'}), 400
        
        # Handle reason for lost if status is Lost
        reason_for_lost = None
        if new_status == 'Lost':
            reason_for_lost = data.get('reason_for_lost')
            if not reason_for_lost or not reason_for_lost.strip():
                return jsonify({'error': 'Reason for lost is required when setting status to Lost'}), 400
            reason_for_lost = reason_for_lost.strip()
        
        # Store the previous status
        previous_status = deal.status
        
        # Create proof of change record
        proof_of_change = ProofOfChange(
            deal_id=deal.id,
            user_id=g.current_user.id,
            previous_status=previous_status,
            new_status=new_status,
            proof_type=proof_type,
            proof_content=proof_content,
            reason_for_lost=reason_for_lost
        )
        
        # Update deal status
        deal.status = new_status
        deal.updated_at = datetime.utcnow()
        
        db.session.add(proof_of_change)
        db.session.commit()
        
        return jsonify({
            'message': 'Deal status updated successfully',
            'deal': deal.to_dict(),
            'proof_of_change': {
                'id': proof_of_change.id,
                'previous_status': previous_status,
                'new_status': new_status,
                'proof_type': proof_type,
                'created_at': proof_of_change.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@deal_status_bp.route('/deals/<int:deal_id>/status-history', methods=['GET'])
@check_permissions('view_deal')
def get_deal_status_history(deal_id):
    """Get the status change history for a deal"""
    try:
        deal = Deal.query.get(deal_id)
        if not deal:
            return jsonify({'error': 'Deal not found'}), 404
        
        # Get all status changes for this deal
        status_changes = ProofOfChange.query.filter_by(deal_id=deal_id).order_by(ProofOfChange.created_at.desc()).all()
        
        history = []
        for change in status_changes:
            history.append({
                'id': change.id,
                'previous_status': change.previous_status,
                'new_status': change.new_status,
                'proof_type': change.proof_type,
                'proof_content': change.proof_content,
                'changed_by': change.user.full_name if change.user else 'Unknown',
                'changed_at': change.created_at.isoformat()
            })
        
        return jsonify({
            'deal_id': deal_id,
            'current_status': deal.status,
            'status_history': history
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deal_status_bp.route('/deals/status-options', methods=['GET'])
def get_status_options():
    """Get all valid deal status options"""
    return jsonify({
        'statuses': VALID_STATUSES,
        'descriptions': {
            'Open': 'Initial status for new deals',
            'New': 'Deal has been reviewed and qualified',
            'Qualification': 'Qualifying customer needs and budget',
            'Demo1': 'First product demonstration scheduled/completed',
            'Demo2': 'Second product demonstration scheduled/completed',
            'Proposal': 'Proposal has been sent to customer',
            'Negotiation': 'Contract terms being negotiated',
            'Won': 'Deal successfully closed',
            'Lost': 'Deal was not successful'
        }
    }), 200

@deal_status_bp.route('/upload-proof', methods=['POST'])
@check_permissions('edit_deal')
def upload_proof_file():
    """Upload a proof file for deal status change"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file size (5MB limit)
        if len(file.read()) > 5 * 1024 * 1024:
            return jsonify({'error': 'File size exceeds 5MB limit'}), 400
        
        file.seek(0)  # Reset file pointer after reading
        
        # Validate file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'proof_files')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        file.save(file_path)
        
        # Return the relative path for storage in database
        relative_path = f"uploads/proof_files/{filename}"
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_path': relative_path,
            'original_filename': file.filename
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@deal_status_bp.route('/proof-files/<path:filename>', methods=['GET'])
@check_permissions('view_deal')
def download_proof_file(filename):
    """Download a proof file"""
    try:
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'proof_files')
        file_path = os.path.join(upload_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        from flask import send_file
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

