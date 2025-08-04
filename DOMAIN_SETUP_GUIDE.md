# 🌐 Justice-Bot.com Domain Setup Guide

## Complete Custom Domain Configuration for Smart Dispute Canada

### 📋 **Prerequisites Checklist**
- [ ] Smart Dispute app deployed (Railway/Google Cloud Run)
- [ ] Domain smartdisputecanada.me registered and accessible
- [ ] DNS management access
- [ ] SSL certificate requirements

---

## 🚀 **Option 1: Railway Custom Domain (Recommended)**

### Step 1: Deploy to Railway
```bash
# 1. Push your code to GitHub
git add .
git commit -m "Deploy Smart Dispute Canada"
git push origin main

# 2. Go to railway.app and deploy from GitHub
# 3. Your app will get a railway.app URL first
```

### Step 2: Add Custom Domain in Railway
1. **Go to Railway Dashboard** → Your Project → Settings
2. **Click "Domains"** tab
3. **Add Custom Domain**: `smartdisputecanada.me`
4. **Add Subdomain**: `www.smartdisputecanada.me`
5. **Railway will provide DNS records**

### Step 3: Configure DNS Records
Add these records to your domain provider (GoDaddy/Namecheap/etc):

```dns
# A Record (Root Domain)
Type: A
Name: @
Value: [Railway's IP Address - provided in dashboard]
TTL: 300

# CNAME Record (WWW Subdomain)
Type: CNAME  
Name: www
Value: [your-app].railway.app
TTL: 300

# CNAME Record (Railway SSL)
Type: CNAME
Name: _acme-challenge
Value: [Railway's ACME challenge - provided in dashboard]
TTL: 300
```

### Step 4: SSL Certificate
- **Railway automatically provisions SSL** via Let's Encrypt
- **Certificate auto-renews** every 90 days
- **HTTPS redirect** enabled automatically

---

## 🌟 **Option 2: Google Cloud Run Custom Domain**

### Step 1: Deploy to Cloud Run
```bash
# Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

### Step 2: Map Custom Domain
```bash
# Map smartdisputecanada.me to your Cloud Run service
gcloud run domain-mappings create \
    --service smartdispute-app \
    --domain smartdisputecanada.me \
    --region us-central1

# Get DNS records to configure
gcloud run domain-mappings describe \
    --domain smartdisputecanada.me \
    --region us-central1
```

### Step 3: Configure DNS Records
```dns
# A Records (from gcloud output)
Type: A
Name: @
Value: 216.239.32.21
TTL: 300

Type: A
Name: @  
Value: 216.239.34.21
TTL: 300

Type: A
Name: @
Value: 216.239.36.21
TTL: 300

Type: A
Name: @
Value: 216.239.38.21
TTL: 300

# CNAME for www
Type: CNAME
Name: www
Value: ghs.googlehosted.com
TTL: 300
```

### Step 4: SSL Certificate (Google-managed)
```bash
# Google automatically provisions SSL certificate
# No additional configuration needed
```

---

## 🛡️ **Option 3: Cloudflare DNS + SSL (Professional)**

### Step 1: Add Domain to Cloudflare
1. **Sign up at cloudflare.com**
2. **Add smartdisputecanada.me** as a site
3. **Update nameservers** at your domain registrar:
   ```
   kane.ns.cloudflare.com
   lola.ns.cloudflare.com
   ```

### Step 2: Configure DNS in Cloudflare
```dns
# A Record (Proxied through Cloudflare)
Type: A
Name: @
Value: [Your deployment IP]
Proxied: ✅ (Orange Cloud)

# CNAME Record  
Type: CNAME
Name: www
Value: smartdisputecanada.me
Proxied: ✅ (Orange Cloud)
```

### Step 3: SSL/TLS Configuration
1. **Go to SSL/TLS** → Overview
2. **Set encryption mode**: Full (strict)
3. **Enable "Always Use HTTPS"**
4. **Enable "Automatic HTTPS Rewrites"**

### Step 4: Security & Performance
```bash
# Enable these Cloudflare features:
- Brotli Compression: ON
- Auto Minify (CSS, JS, HTML): ON  
- Security Level: Medium
- Bot Fight Mode: ON
- Browser Integrity Check: ON
```

---

## 🏃‍♂️ **Quick Setup Commands**

### For Railway Deployment:
```bash
# 1. Deploy to Railway via GitHub
echo "1. Push to GitHub, deploy via Railway dashboard"
echo "2. Add custom domain: smartdisputecanada.me"
echo "3. Configure DNS with provided records"
echo "4. SSL auto-enabled by Railway"
```

### For Google Cloud Run:
```bash
# 1. Deploy application
./deploy.sh

# 2. Map domain
gcloud run domain-mappings create \
    --service smartdispute-app \
    --domain smartdisputecanada.me \
    --region us-central1

# 3. Verify domain mapping
gcloud run domain-mappings list
```

---

## 🔍 **DNS Verification Commands**

```bash
# Check DNS propagation
dig smartdisputecanada.me
dig www.smartdisputecanada.me

# Check SSL certificate
curl -I https://smartdisputecanada.me
openssl s_client -connect smartdisputecanada.me:443 -servername smartdisputecanada.me

# Test application
curl -L https://smartdisputecanada.me/health
```

---

## 📧 **Email Configuration (Optional)**

### Setup admin@smartdisputecanada.me for e-transfers:
```dns
# MX Records for email
Type: MX
Name: @
Value: mx1.forwardemail.net
Priority: 10

Type: MX  
Name: @
Value: mx2.forwardemail.net
Priority: 20
```

### Email Forwarding Setup:
1. **Use ForwardEmail.net** (free)
2. **Forward admin@smartdisputecanada.me** → your-email@gmail.com
3. **Add TXT record for verification**:
   ```dns
   Type: TXT
   Name: @
   Value: forward-email=your-email@gmail.com
   ```

---

## ✅ **Final Verification Checklist**

- [ ] **https://smartdisputecanada.me** loads successfully
- [ ] **https://www.smartdisputecanada.me** redirects to main domain
- [ ] **SSL certificate** shows valid and secure
- [ ] **Health check** responds: https://smartdisputecanada.me/health
- [ ] **Admin dashboard** accessible: https://smartdisputecanada.me/admin
- [ ] **Email forwarding** working: admin@smartdisputecanada.memand

---

## 🆘 **Troubleshooting**

### DNS Not Propagating:
```bash
# Check DNS propagation globally
curl -s "https://dns.google/resolve?name=smartdisputecanada.me&type=A" | jq
```

### SSL Certificate Issues:
```bash
# Force SSL renewal (Cloudflare)
# Dashboard → SSL/TLS → Edge Certificates → Delete & Re-create

# Railway SSL issues
# Dashboard → Domains → Remove & Re-add domain
```

### Application Not Loading:
```bash
# Check deployment status
# Railway: Check deployment logs
# GCloud: gcloud run services list

# Verify health endpoint
curl -v https://smartdisputecanada.me/health
```

---

## 🎯 **Expected Result**

After completion, your Smart Dispute Canada application will be live at:

- **Primary**: https://smartdisputecanada.me
- **WWW**: https://www.smartdisputecanada.me (redirects to primary)
- **Health**: https://smartdisputecanada.me/health
- **Admin**: https://smartdisputecanada.me/admin
- **Email**: admin@smartdisputecanada.memand (forwarding to your email)

**Professional SSL certificate**, **Canadian Charter theme**, and **full legal platform** accessible globally! 🍁⚖️