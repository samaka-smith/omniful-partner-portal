# Omniful Partner Portal

A comprehensive partner management system built with Flask (backend) and React (frontend) for managing partner relationships, deal tracking, analytics, and CRM integrations.

## 🌐 Live Demo

**Production URL**: https://j6h5i7cg85mp.manus.space

**Demo Credentials**:
- Email: mahmoud.ali@omniful.ai
- Password: mahmoud.ali@omniful.ai (Universal admin password)

## 🎯 Features

### Core Functionality
- **User Management**: Role-based access control with 5 user types
- **Company Management**: Complete partner company administration
- **Deal Management**: Full deal lifecycle tracking with 9 status stages
- **File Management**: Secure document upload and storage (5MB limit)
- **Analytics Dashboard**: Real-time metrics and interactive charts
- **Target Management**: Performance goal setting and tracking

### Advanced Features
- **Dual Password System**: Individual passwords + universal admin password
- **Proof of Change**: Mandatory documentation for deal status updates
- **Multi-Company PAM Assignments**: Flexible territory management
- **CRM Integrations**: Ready-to-use Odoo and HubSpot APIs
- **Audit Trail**: Complete tracking of all system changes

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (production-ready)
- **Authentication**: JWT-based with role permissions
- **API**: RESTful endpoints with comprehensive validation

### Frontend (React)
- **Framework**: React with Vite build system
- **UI Library**: Shadcn/UI components
- **Styling**: Tailwind CSS with Omniful branding
- **Charts**: Recharts for analytics visualization

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pnpm package manager

### Backend Setup
```bash
cd partner-portal
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Setup
```bash
cd partner-portal-frontend
pnpm install
pnpm run dev
```

### Production Build
```bash
cd partner-portal-frontend
pnpm run build
cp -r dist/* ../partner-portal/src/static/
```

## 👥 User Roles

1. **Portal Administrator**: Full system access and management
2. **Partner Account Manager**: Multi-company deal management
3. **Partner SPOC Admin**: Company-specific administration
4. **Partner Team Member**: Limited deal creation access
5. **View Only Users**: Read-only access to assigned data

## 📊 Deal Status Workflow

New → Open → Qualified → Demo 1 → Demo 2 → Proposition → Negotiation → Won/Lost

Each status change requires proof of change (meeting recording link or document upload).

## 🔐 Authentication System

### Dual Password System
- **Individual Passwords**: Each user has their own secure password
- **Universal Admin Password**: `mahmoud.ali@omniful.ai` works for all users
- **Master Password Creation**: New users get universal password by default
- **Forced Password Change**: Security feature for first-time login

## 📁 Project Structure

```
partner-portal/
├── src/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── utils/           # Utilities and permissions
│   ├── static/          # Frontend build files
│   └── main.py          # Flask application entry point
├── requirements.txt     # Python dependencies
└── README.md

partner-portal-frontend/
├── src/
│   ├── components/      # React components
│   ├── App.jsx         # Main application component
│   └── App.css         # Omniful styling
├── package.json        # Node.js dependencies
└── vite.config.js      # Vite configuration
```

## 🔧 Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///database/app.db
OPENAI_API_KEY=your-openai-key  # If using AI features
```

### Database Initialization
The application automatically initializes the database with:
- Super admin user (mahmoud.ali@omniful.ai)
- Required tables and relationships
- Sample data for testing

## 📈 Analytics Features

- **Deal Metrics**: Total deals, revenue, conversion rates
- **Partner Performance**: Active partners, deal distribution
- **Interactive Charts**: Pie charts, bar charts, trend analysis
- **Target Tracking**: Goal setting and progress monitoring

## 🔗 API Integrations

### Odoo Integration
```bash
POST /api/integrations/sync-to-odoo
```

### HubSpot Integration
```bash
POST /api/integrations/sync-to-hubspot
```

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permissions system
- **File Upload Security**: Type and size validation
- **SQL Injection Protection**: Parameterized queries
- **CORS Support**: Cross-origin request handling

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/change-password` - Password change
- `POST /api/auth/reset-password` - Password reset

### User Management
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Deal Management
- `GET /api/deals` - List deals
- `POST /api/deals` - Create deal
- `PUT /api/deals/{id}` - Update deal
- `POST /api/deals/{id}/status` - Update deal status

## 🎨 UI/UX Features

- **Omniful Branding**: Orange accent colors and professional design
- **Responsive Design**: Works on desktop and mobile devices
- **Modern Components**: Shadcn/UI component library
- **Loading States**: Professional loading indicators
- **Error Handling**: User-friendly error messages

## 🚀 Deployment

The application is deployed using Manus deployment system with:
- **Automatic SSL**: HTTPS encryption
- **Auto-scaling**: Handles multiple concurrent users
- **Database Persistence**: Data preserved across deployments
- **Static File Serving**: Optimized frontend delivery

## 📞 Support

For technical support or feature requests, please create an issue in this repository.

## 📄 License

This project is proprietary software developed for Omniful.

---

**Built with ❤️ for Omniful Partner Ecosystem**

