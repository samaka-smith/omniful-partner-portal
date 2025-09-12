import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db, User
from src.models.company import Company
from src.models.deal import Deal
from src.models.deal_file import DealFile
from src.models.deal_comment import DealComment
from src.models.target import Target
from src.models.pam_company_association import pam_company_association
from src.models.proof_of_change import ProofOfChange
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.company import company_bp
from src.routes.deal import deal_bp
from src.routes.file import file_bp
from src.routes.target_management import target_management_bp
from src.routes.user_creation import user_creation_bp
from src.routes.company_management import company_management_bp
from src.routes.pam_assignments import pam_assignments_bp
from src.routes.deal_status import deal_status_bp
from src.routes.integration import integration_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(company_bp, url_prefix='/api')
app.register_blueprint(deal_bp, url_prefix='/api')
app.register_blueprint(file_bp, url_prefix='/api')
app.register_blueprint(target_management_bp, url_prefix='/api')
app.register_blueprint(user_creation_bp, url_prefix='/api')
app.register_blueprint(company_management_bp, url_prefix='/api')
app.register_blueprint(pam_assignments_bp, url_prefix='/api')
app.register_blueprint(deal_status_bp, url_prefix='/api')
app.register_blueprint(integration_bp, url_prefix='/api')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def init_database():
    """Initialize database with default data"""
    from werkzeug.security import generate_password_hash
    
    # Create all tables
    db.create_all()
    
    # Check if Omniful company exists
    omniful_company = Company.query.filter_by(name='Omniful').first()
    if not omniful_company:
        omniful_company = Company(name='Omniful')
        db.session.add(omniful_company)
        db.session.commit()
        print("Created Omniful company")
    
    # Check if super admin user exists
    admin_user = User.query.filter_by(email='mahmoud.ali@omniful.ai').first()
    if not admin_user:
        admin_user = User(
            username='Mahmoud Ali',
            email='mahmoud.ali@omniful.ai',
            password_hash=generate_password_hash('mahmoud.ali@omniful.ai'),
            role='Portal Administrator',
            company_id=omniful_company.id,
            status='active',
            force_password_change=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Created super admin user: mahmoud.ali@omniful.ai with master password")

with app.app_context():
    init_database()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
