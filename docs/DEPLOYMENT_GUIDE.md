# 🚀 Deployment Guide - HMM Trading Dashboard

## 📋 Overview

This guide covers deploying your HMM Trading Dashboard to production environments.

---

## 🌐 Deployment Options

### **Option 1: Streamlit Cloud (Recommended)**
- ✅ Free tier available
- ✅ Easy setup
- ✅ Automatic updates
- ✅ SSL included
- ⚠️ Public by default (can make private)

### **Option 2: Self-Hosted**
- ✅ Full control
- ✅ Can be private
- ⚠️ Requires server management
- ⚠️ SSL setup needed

### **Option 3: Docker**
- ✅ Consistent environment
- ✅ Easy scaling
- ⚠️ Requires Docker knowledge

---

## 🚀 Streamlit Cloud Deployment

### **Prerequisites**
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### **Step 1: Prepare Repository**

1. **Initialize Git (if not already)**
```bash
cd C:\Traning\stock_analysis
git init
git add .
git commit -m "Initial commit - HMM Trading Dashboard"
```

2. **Create GitHub Repository**
- Go to https://github.com/new
- Create repository: `hmm-trading-dashboard`
- Don't initialize with README

3. **Push to GitHub**
```bash
git remote add origin https://github.com/YOUR_USERNAME/hmm-trading-dashboard.git
git branch -M main
git push -u origin main
```

---

### **Step 2: Deploy to Streamlit Cloud**

1. **Go to Streamlit Cloud**
- Visit: https://share.streamlit.io
- Sign in with GitHub

2. **Create New App**
- Click "New app"
- Select your repository: `hmm-trading-dashboard`
- Main file path: `app.py`
- Python version: 3.12

3. **Configure Secrets (Optional)**
- Click "Advanced settings"
- Add secrets in TOML format:

```toml
[email]
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "your-email@gmail.com"
smtp_password = "your-app-password"
recipient_email = "recipient@example.com"

[general]
environment = "production"
debug_mode = false
log_level = "INFO"
```

4. **Deploy**
- Click "Deploy!"
- Wait 5-10 minutes for initial deployment
- Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

### **Step 3: Configure hmmlearn**

**Option A: Make hmmlearn Optional (Current Setup)**
- Dashboard works without hmmlearn
- Shows warning: "hmmlearn not installed"
- Users can view data but not train models

**Option B: Install hmmlearn on Streamlit Cloud**

Add to `packages.txt`:
```
build-essential
gcc
g++
gfortran
libopenblas-dev
liblapack-dev
python3-dev
```

Note: This may increase build time significantly.

---

### **Step 4: Test Deployment**

1. **Visit your deployed app**
2. **Test core features:**
   - [ ] Data loading
   - [ ] Dashboard displays
   - [ ] Charts render
   - [ ] Configuration panel works
   - [ ] Backtest runs (if hmmlearn installed)

3. **Check logs:**
- Click "Manage app" in Streamlit Cloud
- View logs for errors

---

## 🖥️ Self-Hosted Deployment

### **Using Nginx + Systemd (Linux)**

### **Step 1: Install Dependencies**

```bash
# Install Python 3.12
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip

# Install system dependencies
sudo apt install build-essential gcc g++ gfortran libopenblas-dev liblapack-dev
```

### **Step 2: Setup Application**

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/hmm-trading-dashboard.git
cd hmm-trading-dashboard

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install hmmlearn
```

### **Step 3: Create Systemd Service**

Create `/etc/systemd/system/hmm-dashboard.service`:

```ini
[Unit]
Description=HMM Trading Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/hmm-trading-dashboard
Environment="PATH=/path/to/hmm-trading-dashboard/venv/bin"
ExecStart=/path/to/hmm-trading-dashboard/venv/bin/streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable hmm-dashboard
sudo systemctl start hmm-dashboard
```

### **Step 4: Configure Nginx**

Create `/etc/nginx/sites-available/hmm-dashboard`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/hmm-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 5: Add SSL (Let's Encrypt)**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🐳 Docker Deployment

### **Step 1: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir hmmlearn

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Step 2: Create docker-compose.yml**

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

### **Step 3: Deploy**

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔒 Security Considerations

### **Production Checklist**

- [ ] **Environment Variables**
  - Never commit `.env` or `secrets.toml`
  - Use environment variables for sensitive data
  
- [ ] **HTTPS**
  - Always use SSL in production
  - Let's Encrypt for free certificates
  
- [ ] **Database**
  - Regular backups
  - Restrict file permissions
  
- [ ] **Rate Limiting**
  - Consider adding rate limits for API calls
  
- [ ] **Error Handling**
  - Don't expose stack traces to users
  - Log errors server-side
  
- [ ] **Dependencies**
  - Keep dependencies updated
  - Run `pip list --outdated` regularly

---

## 📊 Monitoring

### **Application Monitoring**

1. **Streamlit Cloud (Built-in)**
   - View app logs
   - Check resource usage
   - Monitor uptime

2. **Self-Hosted**
   - Use `systemctl status hmm-dashboard`
   - Check logs: `journalctl -u hmm-dashboard -f`
   - Monitor with tools like Grafana, Prometheus

### **Performance Metrics**

Monitor:
- Response times
- Memory usage
- API call rates (yfinance)
- Error rates

---

## 🔄 Updates & Maintenance

### **Streamlit Cloud**

```bash
# Update code
git add .
git commit -m "Update feature"
git push origin main
```

App updates automatically!

### **Self-Hosted**

```bash
# Pull updates
cd /path/to/hmm-trading-dashboard
git pull origin main

# Restart service
sudo systemctl restart hmm-dashboard
```

### **Docker**

```bash
# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🐛 Troubleshooting

### **Build Fails on Streamlit Cloud**

**Issue:** hmmlearn installation fails

**Solution:** 
- Make hmmlearn optional
- Or add all build dependencies to `packages.txt`

### **App Crashes**

**Check:**
- Logs in Streamlit Cloud dashboard
- Memory usage (increase resources)
- Database file permissions

### **Slow Performance**

**Solutions:**
- Enable caching
- Reduce lookback days
- Optimize data loading
- Use pagination

---

## 📝 Environment Variables

**Available variables:**

```bash
# Environment
ENVIRONMENT=production
DEBUG_MODE=false

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true

# Data
DEFAULT_LOOKBACK_DAYS=60
MAX_LOOKBACK_DAYS=365

# Performance
ENABLE_CACHING=true
CACHE_TTL=3600

# Paper Trading
PAPER_TRADING_ENABLED=true
UPDATE_INTERVAL=300

# Email (optional)
EMAIL_ENABLED=false
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
```

---

## 🎯 Quick Deployment Commands

### **Streamlit Cloud (Easiest)**
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main

# 2. Go to share.streamlit.io
# 3. Deploy from GitHub repo
```

### **Self-Hosted**
```bash
# Setup and run
git clone <repo>
cd hmm-trading-dashboard
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### **Docker**
```bash
# Build and run
docker-compose up -d
```

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] Dashboard loads successfully
- [ ] Can load data
- [ ] Charts render correctly
- [ ] Configuration panel works
- [ ] Backtest runs (if hmmlearn available)
- [ ] Paper trading tab works
- [ ] Export features work (CSV/PDF)
- [ ] No errors in logs
- [ ] Performance is acceptable
- [ ] SSL certificate valid (if applicable)

---

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud
- **Docker Docs:** https://docs.docker.com
- **Nginx Docs:** https://nginx.org/en/docs/

---

**Your dashboard is now ready for production!** 🚀
