# Omniful Partner Portal - Permanent Deployment Guide

This guide provides step-by-step instructions for deploying the Omniful Partner Portal to various hosting platforms for permanent, production-ready hosting.

---

## 🚀 Quick Deploy Options

### Option 1: Render.com (Recommended - Free Tier Available)

**Render.com** offers free hosting for web services with automatic deployments from GitHub.

#### Steps:

1. **Sign up at Render.com**
   - Go to https://render.com
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `samaka-smith/omniful-partner-portal`
   - Select branch: `branch-12`

3. **Configure Service**
   - **Name:** omniful-partner-portal
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python3 create_admin_user.py`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 src.main:app`

4. **Environment Variables**
   - Add: `FLASK_ENV=production`
   - Add: `SECRET_KEY=your-secret-key-here` (generate a secure random string)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your portal will be live at: `https://omniful-partner-portal.onrender.com`

**Pros:**
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ HTTPS included
- ✅ Easy setup

**Cons:**
- ⚠️ Free tier spins down after inactivity (30 seconds to wake up)

---

### Option 2: Railway.app (Easy & Fast)

**Railway.app** offers simple deployment with generous free tier.

#### Steps:

1. **Sign up at Railway.app**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `samaka-smith/omniful-partner-portal`
   - Branch: `branch-12`

3. **Configure**
   - Railway will auto-detect Python
   - Add environment variable: `SECRET_KEY=your-secret-key-here`

4. **Deploy**
   - Railway automatically deploys
   - Get your URL from the deployment dashboard

**Pros:**
- ✅ Very easy setup
- ✅ Fast deployments
- ✅ Always-on (no spin down)
- ✅ Free tier: $5 credit/month

---

### Option 3: Heroku (Most Reliable)

**Heroku** is a mature platform with excellent Python support.

#### Steps:

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   cd /path/to/omniful-partner-portal
   heroku create omniful-partner-portal
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key-here
   ```

5. **Deploy**
   ```bash
   git push heroku branch-12:main
   ```

6. **Initialize Database**
   ```bash
   heroku run python3 create_admin_user.py
   ```

7. **Open Portal**
   ```bash
   heroku open
   ```

**Pros:**
- ✅ Very reliable
- ✅ Excellent documentation
- ✅ Add-ons available (databases, monitoring)

**Cons:**
- ⚠️ No free tier (starts at $7/month)

---

### Option 4: Docker Deployment (Any Platform)

Deploy using Docker on any platform that supports containers (DigitalOcean, AWS, Google Cloud, etc.)

#### Steps:

1. **Build Docker Image**
   ```bash
   cd /path/to/omniful-partner-portal
   docker build -t omniful-partner-portal .
   ```

2. **Run Container**
   ```bash
   docker run -d -p 5000:5000 --name omniful-portal omniful-partner-portal
   ```

3. **Or use Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access Portal**
   - Open: http://localhost:5000
   - Or configure reverse proxy (Nginx) for production

**Pros:**
- ✅ Works anywhere
- ✅ Consistent environment
- ✅ Easy scaling

---

### Option 5: DigitalOcean App Platform

**DigitalOcean** offers managed app hosting with $5/month plans.

#### Steps:

1. **Sign up at DigitalOcean**
   - Go to https://www.digitalocean.com
   - Create account

2. **Create New App**
   - Go to Apps → Create App
   - Connect GitHub repository
   - Select: `samaka-smith/omniful-partner-portal`
   - Branch: `branch-12`

3. **Configure**
   - **Build Command:** `pip install -r requirements.txt && python3 create_admin_user.py`
   - **Run Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 src.main:app`
   - **HTTP Port:** 5000

4. **Environment Variables**
   - Add: `FLASK_ENV=production`
   - Add: `SECRET_KEY=your-secret-key-here`

5. **Deploy**
   - Click "Create Resources"
   - Wait for deployment

**Pros:**
- ✅ Reliable infrastructure
- ✅ $5/month basic plan
- ✅ Good performance

---

## 🔧 Configuration Details

### Environment Variables

All platforms require these environment variables:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

**Generate a secure SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### Database

The portal uses SQLite by default. For production with high traffic, consider:

1. **PostgreSQL** (recommended for production)
2. **MySQL**
3. **MongoDB** (requires code changes)

### Admin User

The admin user is automatically created on deployment:
- **Email:** mahmoud@portal.omniful
- **Password:** Admin123

**Important:** Change the admin password after first login!

---

## 📊 Platform Comparison

| Platform | Free Tier | Always On | Setup Difficulty | Best For |
|----------|-----------|-----------|------------------|----------|
| Render.com | ✅ Yes | ⚠️ Spins down | ⭐ Easy | Testing/Demo |
| Railway.app | ✅ $5 credit | ✅ Yes | ⭐ Very Easy | Small projects |
| Heroku | ❌ No | ✅ Yes | ⭐⭐ Moderate | Production |
| DigitalOcean | ❌ No | ✅ Yes | ⭐⭐ Moderate | Production |
| Docker | N/A | ✅ Yes | ⭐⭐⭐ Advanced | Custom hosting |

---

## 🔒 Security Checklist

Before going to production:

- [ ] Change SECRET_KEY to a secure random value
- [ ] Change admin password after first login
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Set up database backups
- [ ] Configure monitoring/logging
- [ ] Review and update CORS settings
- [ ] Set up rate limiting (optional)
- [ ] Configure firewall rules (if using VPS)

---

## 🎯 Recommended Deployment Path

**For Quick Testing:**
→ Use **Render.com** (free, easy, 5 minutes setup)

**For Production:**
→ Use **Railway.app** (affordable, reliable) or **Heroku** (most reliable)

**For Custom Infrastructure:**
→ Use **Docker** on DigitalOcean/AWS/Google Cloud

---

## 📝 Post-Deployment Steps

1. **Test the Portal**
   - Login with admin credentials
   - Create test users
   - Test all features

2. **Change Admin Password**
   - Login as admin
   - Go to profile settings
   - Change password

3. **Configure DNS (Optional)**
   - Point your custom domain to the deployment URL
   - Most platforms support custom domains

4. **Set Up Monitoring**
   - Configure uptime monitoring
   - Set up error tracking
   - Enable logging

5. **Backup Database**
   - Set up automated backups
   - Test restore process

---

## 🆘 Troubleshooting

### Common Issues:

**Issue: App won't start**
- Check logs for errors
- Verify environment variables are set
- Ensure all dependencies are installed

**Issue: Database errors**
- Run `python3 create_admin_user.py` to initialize
- Check database permissions
- Verify database file path

**Issue: Login not working**
- Check SECRET_KEY is set
- Verify admin user was created
- Check JWT token configuration

---

## 📞 Support

For deployment help:
- Check platform documentation
- Review application logs
- Contact platform support

For application issues:
- Check GitHub repository
- Review SECURITY_AND_DEPLOYMENT.md
- Check application logs

---

## 🎉 Quick Start (Render.com)

**Fastest way to get your portal live:**

1. Go to https://render.com and sign up
2. Click "New +" → "Web Service"
3. Connect GitHub: `samaka-smith/omniful-partner-portal`
4. Use these settings:
   - Build: `pip install -r requirements.txt && python3 create_admin_user.py`
   - Start: `gunicorn --bind 0.0.0.0:$PORT --workers 4 src.main:app`
5. Add environment variable: `FLASK_ENV=production`
6. Click "Create Web Service"
7. Wait 5-10 minutes
8. Your portal is live! 🎉

**Login:** mahmoud@portal.omniful / Admin123

---

**Need help? Check the platform-specific documentation or contact support.**

