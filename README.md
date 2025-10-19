# Omniful Partner Portal

A comprehensive Partner Management Portal built with Flask (Python) backend and React frontend, featuring role-based access control, deal tracking, analytics, and partner relationship management.

## 🌟 Features

### Core Functionality
- **User Management** - Role-based user creation, editing, and deletion
- **Company Management** - Partner and customer company profiles
- **Deal Tracking** - Complete deal pipeline management with stages
- **Analytics Dashboard** - Performance metrics and insights
- **Target Management** - Set and track performance targets
- **PAM Assignments** - Assign Partner Account Managers to companies

### Security Features
- **Role-Based Access Control (RBAC)** - Comprehensive permission system
- **JWT Authentication** - Secure token-based authentication
- **Password Management** - Secure password hashing and reset functionality
- **Session Management** - 24-hour token expiration
- **Input Validation** - Server-side validation on all endpoints

## 🔐 User Roles

### Portal Administrator
- Full administrative control across all portal areas
- Can change any user's password
- Can delete users
- Can change user allocations (company assignments)
- Can assign companies to PAMs
- Can view all analytics and set targets

### Partner Account Manager (PAM)
- Administrative view over assigned companies
- Can create users for assigned companies only
- Can change passwords for users in assigned companies
- Can update partner company attributes
- Can view analytics of assigned companies
- Cannot delete users or change user allocations

### Partner SPOC
- Can manage one assigned partner company
- Can add referrals and deals
- Can view analytics for their company
- Cannot edit company data

### Partner Team Member
- Can add leads, deals, or referrals only
- No access to analytics or company data

### View Only Users
- Read-only access to analytics and dashboards
- Cannot modify any data

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip3
- Node.js 22+ (for frontend development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/samaka-smith/omniful-partner-portal.git
   cd omniful-partner-portal
   ```

2. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Initialize the database and create admin user**
   ```bash
   python3 create_admin_user.py
   ```

4. **Start the server**
   ```bash
   python3 src/main.py
   ```

5. **Access the portal**
   Open your browser and navigate to: `http://localhost:5000`

### Default Admin Credentials
**Email:** mahmoud@portal.omniful  
**Password:** Admin123

## 📁 Project Structure

```
omniful-partner-portal/
├── src/
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── deal.py
│   │   ├── target.py
│   │   └── pam_company_association.py
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication routes
│   │   ├── user.py          # User management
│   │   ├── company.py       # Company management
│   │   ├── deal.py          # Deal management
│   │   ├── target_management.py
│   │   └── pam_assignments.py
│   ├── utils/               # Utility functions
│   │   └── permissions.py   # Permission checking
│   ├── static/              # Frontend build files
│   ├── database/            # SQLite database
│   └── main.py              # Application entry point
├── create_admin_user.py     # Admin user creation script
├── requirements.txt         # Python dependencies
├── SECURITY_AND_DEPLOYMENT.md  # Security documentation
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/change-password` - Change own password
- `POST /api/auth/reset-password` - Reset user password (Admin/PAM)

### User Management
- `GET /api/users` - List all users
- `GET /api/users/:id` - Get user details
- `POST /api/users` - Create new user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Company Management
- `GET /api/companies` - List all companies
- `POST /api/companies` - Create company
- `PUT /api/companies/:id` - Update company
- `DELETE /api/companies/:id` - Delete company

### Deal Management
- `GET /api/deals` - List deals
- `POST /api/deals` - Create deal
- `PUT /api/deals/:id` - Update deal
- `DELETE /api/deals/:id` - Delete deal

### PAM Assignments
- `GET /api/users/:id/companies` - Get PAM's assigned companies
- `POST /api/users/:id/companies/:company_id` - Assign company to PAM
- `DELETE /api/users/:id/companies/:company_id` - Remove company from PAM

### Target Management
- `GET /api/targets` - List targets
- `POST /api/targets` - Create target
- `PUT /api/targets/:id` - Update target
- `DELETE /api/targets/:id` - Delete target

## 🛡️ Security Implementation

### Password Management
- **Portal Admin**: Can change any user's password
- **PAM**: Can only change passwords for users in managed companies
- **All Users**: Can change their own passwords

### User Deletion
- **Portal Admin**: Can delete any user (except themselves)
- **Other Roles**: Cannot delete users

### User Allocation
- **Portal Admin**: Can change any user's company assignment
- **Other Roles**: Cannot modify user allocations

### User Creation
- **Portal Admin**: Can create users for any company
- **PAM**: Can only create users for companies they manage

## 🧪 Testing

The portal has been thoroughly tested with comprehensive security tests:

- ✅ Admin password change permissions
- ✅ PAM password change within scope
- ✅ PAM password change outside scope (denied)
- ✅ User deletion permissions
- ✅ User allocation change permissions
- ✅ Self-service password change
- ✅ User creation permissions

See [SECURITY_AND_DEPLOYMENT.md](SECURITY_AND_DEPLOYMENT.md) for detailed test results.

## 🗄️ Database Schema

### Users
- id, username, email, password_hash
- role, company_id, status
- force_password_change
- created_at, updated_at

### Companies
- id, name, company_type
- partner_stage, published_on_website
- created_at, updated_at

### Deals
- id, partner_company_id, customer_company_name
- deal_size, deal_stage
- created_at, updated_at

### Targets
- id, target_type, target_entity_id
- target_metric, target_value, target_period
- created_at, updated_at

### PAM Company Association
- pam_id, company_id (Many-to-Many relationship)

## 🔧 Technology Stack

- **Backend Framework**: Flask 3.1.1
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (PyJWT 2.10.1)
- **Password Security**: Werkzeug
- **Frontend**: React.js
- **API Design**: RESTful
- **CORS**: Flask-CORS 6.0.0

## 📝 Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=sqlite:///src/database/app.db
```

## 🚀 Deployment

### Production Deployment

1. **Update SECRET_KEY** in production environment
2. **Use production WSGI server** (e.g., Gunicorn)
   ```bash
   pip3 install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```
3. **Configure reverse proxy** (e.g., Nginx)
4. **Enable HTTPS** with SSL certificates
5. **Set up database backups**

### Docker Deployment (Coming Soon)
Docker support will be added in future updates.

## 📊 Features Roadmap

- [ ] Docker containerization
- [ ] Email notifications
- [ ] File upload for company logos
- [ ] Advanced analytics and reporting
- [ ] Export functionality (CSV, PDF)
- [ ] Audit logging
- [ ] Two-factor authentication
- [ ] API rate limiting

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software owned by Omniful.

## 👥 Authors

- **Development Team** - Omniful Partner Portal Team

## 📞 Support

For support, please contact the development team or open an issue in the repository.

## 🙏 Acknowledgments

- Flask community for excellent documentation
- React team for the frontend framework
- All contributors and testers

---

**Version:** 1.0.0  
**Last Updated:** October 19, 2025  
**Status:** Production Ready ✅

