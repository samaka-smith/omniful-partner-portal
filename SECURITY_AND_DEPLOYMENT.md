# Omniful Partner Portal - Security & Deployment Guide

## 🔐 Security Implementation Summary

### Role-Based Access Control (RBAC)

This portal implements comprehensive role-based access controls with the following security features:

#### 1. Password Management

**Portal Administrator:**
- ✅ Can change any user's password
- ✅ Can reset passwords for all users
- ✅ Can force password changes on next login

**Partner Account Manager (PAM):**
- ✅ Can only change passwords for users in companies they manage
- ✅ Cannot change passwords for users outside their scope
- ✅ Cannot change admin passwords

**All Users:**
- ✅ Can change their own passwords via `/api/auth/change-password`
- ✅ Cannot change other users' passwords
- ✅ Must provide current password to change password

#### 2. User Deletion

**Portal Administrator:**
- ✅ Can delete any user (except themselves)
- ✅ Cannot delete the last Portal Administrator

**Other Roles:**
- ❌ Cannot delete any users
- ❌ PAM, SPOC, Team Members have no delete permissions

#### 3. User Allocation (Company Assignment)

**Portal Administrator:**
- ✅ Can change any user's company assignment
- ✅ Can assign users to any company
- ✅ Full control over user allocations

**Other Roles:**
- ❌ Cannot change user company assignments
- ❌ Users cannot change their own company
- ❌ PAM cannot modify user allocations

#### 4. User Creation

**Portal Administrator:**
- ✅ Can create users for any company
- ✅ Can create users with any role
- ✅ Full user creation privileges

**Partner Account Manager (PAM):**
- ✅ Can create users for companies they manage
- ❌ Cannot create users for companies outside their scope
- ✅ Must specify a company_id when creating users

**Other Roles:**
- ❌ Cannot create users

---

## 🚀 Deployment Information

### Live Portal URL
**Portal URL:** https://5000-iv4hm36xbd5xvrj8xppqf-8e345a94.manusvm.computer/

### Admin Credentials
**Email:** mahmoud@portal.omniful  
**Password:** Admin123

### Test Users Created
1. **Portal Administrator** - mahmoud@portal.omniful (Active)
2. **Portal Administrator** - mahmoud.ali@omniful.ai (Password Change Required)
3. **Partner Account Manager** - pam@test.com (Active, manages Test Partner Company)
4. **Partner Team Member** - user2@test.com (Password Change Required, assigned to Omniful)

---

## 🧪 Security Testing Results

### Test 1: Admin Password Change ✅
- Admin successfully changed password for any user
- Endpoint: `POST /api/auth/reset-password`
- Result: PASSED

### Test 2: PAM Password Change (Within Scope) ✅
- PAM successfully changed password for user in assigned company
- User: user@test.com (company_id: 2)
- PAM: pam@test.com (manages company_id: 2)
- Result: PASSED

### Test 3: PAM Password Change (Outside Scope) ✅
- PAM correctly denied when attempting to change admin password
- Error: "You do not have permission to change this user's password"
- Result: PASSED

### Test 4: PAM User Deletion ✅
- PAM correctly denied when attempting to delete user
- Error: "Only administrators can delete users"
- Result: PASSED

### Test 5: Admin User Deletion ✅
- Admin successfully deleted user (user_id: 4)
- Result: PASSED

### Test 6: User Self-Password Change ✅
- PAM user successfully changed own password
- Old password: TestPass123
- New password: NewPAMPass123
- Result: PASSED

### Test 7: PAM User Allocation Change ✅
- PAM correctly denied when attempting to change user company
- Error: "Access denied"
- Result: PASSED

### Test 8: Admin User Allocation Change ✅
- Admin successfully changed user company assignment
- User moved from company_id: 2 to company_id: 1
- Result: PASSED

---

## 📋 API Endpoints Summary

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/change-password` - User changes own password
- `POST /api/auth/reset-password` - Admin/PAM resets user password

### User Management
- `GET /api/users` - List all users (Admin only)
- `GET /api/users/:id` - Get user details
- `POST /api/users` - Create new user (Admin/PAM)
- `PUT /api/users/:id` - Update user (Admin only for role/company)
- `DELETE /api/users/:id` - Delete user (Admin only)

### Company Management
- `GET /api/companies` - List all companies
- `POST /api/companies` - Create company (Admin only)
- `PUT /api/companies/:id` - Update company (Admin only)
- `DELETE /api/companies/:id` - Delete company (Admin only)

### PAM Assignments
- `GET /api/users/:id/companies` - Get PAM's assigned companies
- `POST /api/users/:id/companies` - Assign companies to PAM (Admin only)
- `POST /api/users/:id/companies/:company_id` - Add single company to PAM
- `DELETE /api/users/:id/companies/:company_id` - Remove company from PAM

### Deal Management
- `GET /api/deals` - List deals (filtered by role)
- `POST /api/deals` - Create deal
- `PUT /api/deals/:id` - Update deal
- `DELETE /api/deals/:id` - Delete deal (Admin only)

### Target Management
- `GET /api/targets` - List targets
- `POST /api/targets` - Create target (Admin only)
- `PUT /api/targets/:id` - Update target (Admin only)
- `DELETE /api/targets/:id` - Delete target (Admin only)

---

## 🔒 Security Best Practices Implemented

1. **JWT Authentication** - All API endpoints require valid JWT tokens
2. **Password Hashing** - Using werkzeug.security for secure password storage
3. **Role-Based Permissions** - Comprehensive permission checks on all endpoints
4. **Input Validation** - Required fields validation on all POST/PUT requests
5. **Error Handling** - Proper error messages without exposing sensitive information
6. **Session Management** - 24-hour token expiration
7. **Database Transactions** - Rollback on errors to maintain data integrity
8. **CORS Enabled** - For frontend-backend communication

---

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** React.js
- **Authentication:** JWT (PyJWT)
- **Password Security:** Werkzeug
- **API:** RESTful API design

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- pip3
- Node.js (for frontend development)

### Backend Setup
```bash
cd /home/ubuntu/omniful-partner-portal
pip3 install -r requirements.txt
python3 src/main.py
```

### Create Admin User
```bash
python3 create_admin_user.py
```

### Access Portal
Open browser and navigate to: http://localhost:5000

---

## 🔄 Database Schema

### Users Table
- id (Primary Key)
- username
- email (Unique)
- password_hash
- role (Portal Administrator, Partner Account Manager, etc.)
- company_id (Foreign Key)
- force_password_change (Boolean)
- status (active/inactive)
- created_at, updated_at

### Companies Table
- id (Primary Key)
- name
- company_type (Partner/Customer)
- partner_stage (Registered/Implementing/Reseller/Strategic)
- published_on_website (Boolean)
- created_at, updated_at

### PAM Company Association Table
- pam_id (Foreign Key to Users)
- company_id (Foreign Key to Companies)

---

## ✅ Verification Checklist

- [x] Portal Admin can change any password
- [x] Portal Admin can delete users
- [x] Portal Admin can change user allocation
- [x] PAM can add users to managed companies
- [x] PAM can change passwords for users in managed companies
- [x] PAM cannot change passwords outside scope
- [x] PAM cannot delete users
- [x] PAM cannot change user allocation
- [x] All users can change own passwords
- [x] Admin user created: mahmoud@portal.omniful
- [x] Portal deployed and accessible
- [x] All sections tested (Dashboard, Users, Companies, Deals, Analytics, Targets)
- [x] Security features verified
- [x] Code integrity maintained

---

## 📞 Support

For any issues or questions, please contact the development team.

**Last Updated:** October 19, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

