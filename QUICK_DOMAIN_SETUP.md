# 🚀 Quick Setup: justice-bot.com

## Get Smart Dispute Canada Live on justice-bot.com in 10 Minutes

### ⚡ **Fastest Path (Railway - Recommended)**r

#### Step 1: Deploy to Railway (2 minutes)
```bash
# 1. Push your code to GitHub
git add .
git commit -m "Deploy Smart Dispute Canada to justice-bot.com"
git push origin main

# 2. Go to https://railway.app
# 3. Sign in with GitHub
# 4. Click "New Project" → "Deploy from GitHub repo"
# 5. Select your smartdisputeflaskapp repository
# 6. Railway auto-deploys (uses your Dockerfile)
```

#### Step 2: Add Custom Domain (1 minute)
```bash
# In Railway Dashboard:
# 1. Go to your project → Settings → Domains
# 2. Click "Custom Domain"
# 3. Enter: justice-bot.com
# 4. Click "Add Domain"
# Railway will show you DNS records to configure
```

#### Step 3: Configure DNS (5 minutes)
```dns
# Go to your domain provider (GoDaddy/Namecheap/etc)
# Add these DNS records (Railway provides exact values):

A Record:
Name: @
Value: [Railway IP - shown in dashboard]
TTL: 300

CNAME Record:
Name: www
Value: [your-app].railway.app
TTL: 300
```

#### Step 4: SSL Certificate (Automatic)
```bash
# Railway automatically provisions SSL certificate
# Usually takes 5-15 minutes after DNS propagation
# You'll see "SSL Active" in Railway dashboard
```

### 🔍 **Verification**
```bash
# Test these URLs (wait 10-15 minutes for DNS):
curl -L https://justice-bot.com
curl -L https://www.justice-bot.com
curl -L https://justice-bot.com/health

# Expected: Canadian-themed Smart Dispute app loads
```

---

### 🏃‍♂️ **Alternative: Run Setup Script**
```bash
# Run the automated setup script
./scripts/setup-domain.sh

# Choose option 1 (Railway)
# Follow the interactive prompts
```

---

### 📧 **Email Setup (Optional - 5 minutes)**

#### ForwardEmail.net Setup:
```bash
# 1. Go to https://forwardemail.net
# 2. Add domain: justice-bot.com
# 3. Set forwarding: admin@justice-bot.com → your-email@gmail.com
```

#### DNS Records for Email:
```dns
MX Record:
Name: @
Value: mx1.forwardemail.net
Priority: 10

MX Record:
Name: @
Value: mx2.forwardemail.net
Priority: 20

TXT Record:
Name: @
Value: forward-email=your-email@gmail.com
```

---

### ✅ **Final Result**

Your Smart Dispute Canada will be live at:
- **🏠 Main Site**: https://justice-bot.com
- **🌐 WWW**: https://www.justice-bot.com  
- **💚 Health Check**: https://justice-bot.com/health
- **👑 Admin Panel**: https://justice-bot.com/admin
- **📧 E-Transfer Email**: admin@justice-bot.com

**Features Active:**
- 🍁 Canadian Charter theme
- ⚖️ Professional legal interface
- 🔒 SSL certificate (HTTPS)
- 🚀 Global CDN via Railway
- 💳 E-transfer payment system
- 🏛️ All Canadian court forms

---

### 🆘 **Troubleshooting**

#### Domain Not Loading:
```bash
# Check DNS propagation
dig justice-bot.com
# Should show Railway IP address

# Check globally
curl -s "https://dns.google/resolve?name=justice-bot.com&type=A"
```

#### SSL Issues:
```bash
# Wait 15-30 minutes for SSL provisioning
# Check Railway dashboard for "SSL Active" status
# Force refresh: Railway Settings → Domains → Remove & Re-add
```

#### App Not Responding:
```bash
# Check Railway deployment logs
# Verify environment variables are set
# Test Railway app URL first: [your-app].railway.app
```

---

### 🎯 **Timeline**
- **Minute 0-2**: Push to GitHub, deploy to Railway
- **Minute 2-3**: Add custom domain in Railway  
- **Minute 3-8**: Configure DNS records
- **Minute 8-15**: Wait for DNS propagation
- **Minute 15-30**: SSL certificate provision
- **Minute 30+**: **justice-bot.com live!** 🍁⚖️

**Your professional Canadian legal platform will be serving Charter rights defenders within 30 minutes!**