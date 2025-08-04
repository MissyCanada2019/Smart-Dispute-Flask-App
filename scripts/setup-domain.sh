#!/bin/bash

# Justice-Bot.com Domain Setup Automation Script
# Smart Dispute Canada - Professional Deployment

set -e

echo "🍁 Setting up smartdisputecanada.me for Smart Dispute Canada"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="smartdisputecanada.me"
PROJECT_NAME="smartdispute-canada"
REGION="us-central1"

echo -e "${BLUE}🚀 Domain Setup Options:${NC}"
echo "1. Railway (Recommended - Easiest)"
echo "2. Google Cloud Run (Enterprise)"
echo "3. Cloudflare + Railway (Professional)"
echo ""

read -p "Choose option (1-3): " OPTION

case $OPTION in
  1)
    echo -e "${GREEN}📋 Railway Deployment Setup${NC}"
    echo "=================================================="
    echo ""
    echo -e "${YELLOW}Step 1: Deploy to Railway${NC}"
    echo "1. Go to https://railway.app"
    echo "2. Sign in with GitHub"
    echo "3. Create new project from GitHub repository"
    echo "4. Railway auto-detects Dockerfile"
    echo ""
    echo -e "${YELLOW}Step 2: Add Custom Domain${NC}"
    echo "1. Go to Project Settings → Domains"
    echo "2. Add custom domain: ${DOMAIN}"
    echo "3. Add www subdomain: www.${DOMAIN}"
    echo ""
    echo -e "${YELLOW}Step 3: Configure DNS${NC}"
    echo "Add these DNS records to your domain provider:"
    echo ""
    echo "A Record:"
    echo "  Name: @"
    echo "  Value: [Railway will provide IP]"
    echo "  TTL: 300"
    echo ""
    echo "CNAME Record:"
    echo "  Name: www"
    echo "  Value: [your-app].railway.app"
    echo "  TTL: 300"
    echo ""
    echo -e "${GREEN}✅ Railway handles SSL automatically!${NC}"
    ;;
    
  2)
    echo -e "${GREEN}📋 Google Cloud Run Setup${NC}"
    echo "=================================================="
    echo ""
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI not found. Install Google Cloud SDK first.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Step 1: Deploy Application${NC}"
    if [ -f "../deploy.sh" ]; then
        echo "Running deployment script..."
        chmod +x ../deploy.sh
        ../deploy.sh
    else
        echo "Manual deployment required:"
        echo "gcloud run deploy smartdispute-app --source . --platform managed --region ${REGION} --allow-unauthenticated"
    fi
    
    echo ""
    echo -e "${YELLOW}Step 2: Map Custom Domain${NC}"
    echo "Mapping ${DOMAIN} to Cloud Run service..."
    
    gcloud run domain-mappings create \
        --service smartdispute-app \
        --domain ${DOMAIN} \
        --region ${REGION} || echo "Domain mapping may already exist"
    
    echo ""
    echo -e "${YELLOW}Step 3: Get DNS Configuration${NC}"
    echo "Required DNS records:"
    gcloud run domain-mappings describe \
        --domain ${DOMAIN} \
        --region ${REGION}
    
    echo ""
    echo -e "${GREEN}✅ Google handles SSL automatically!${NC}"
    ;;
    
  3)
    echo -e "${GREEN}📋 Cloudflare + Railway Professional Setup${NC}"
    echo "=================================================="
    echo ""
    echo -e "${YELLOW}Step 1: Add Domain to Cloudflare${NC}"
    echo "1. Go to https://cloudflare.com"
    echo "2. Add ${DOMAIN} as a site"
    echo "3. Update nameservers at your domain registrar"
    echo ""
    echo -e "${YELLOW}Step 2: Deploy to Railway${NC}"
    echo "1. Follow Railway steps from Option 1"
    echo "2. Get Railway app URL"
    echo ""
    echo -e "${YELLOW}Step 3: Configure Cloudflare DNS${NC}"
    echo "Add these records in Cloudflare Dashboard:"
    echo ""
    echo "A Record (Proxied):"
    echo "  Name: @"
    echo "  Value: [Railway IP]"
    echo "  Proxy: Enabled (Orange Cloud)"
    echo ""
    echo "CNAME Record (Proxied):"
    echo "  Name: www"
    echo "  Value: ${DOMAIN}"
    echo "  Proxy: Enabled (Orange Cloud)"
    echo ""
    echo -e "${YELLOW}Step 4: Enable Cloudflare Features${NC}"
    echo "- SSL/TLS: Full (strict)"
    echo "- Always Use HTTPS: Enabled"
    echo "- Auto Minify: Enabled"
    echo "- Brotli Compression: Enabled"
    echo "- Bot Fight Mode: Enabled"
    echo ""
    echo -e "${GREEN}✅ Cloudflare provides enterprise-grade security!${NC}"
    ;;
    
  *)
    echo -e "${RED}❌ Invalid option${NC}"
    exit 1
    ;;
esac

echo ""
echo -e "${BLUE}🔍 DNS Verification Commands:${NC}"
echo "dig ${DOMAIN}"
echo "dig www.${DOMAIN}"
echo "curl -I https://${DOMAIN}"
echo "curl -L https://${DOMAIN}/health"

echo ""
echo -e "${BLUE}📧 Optional: Email Setup${NC}"
echo "To set up admin@${DOMAIN} for e-transfers:"
echo "1. Use ForwardEmail.net (free)"
echo "2. Add MX records to DNS"
echo "3. Forward admin@${DOMAIN} to your Gmail"

echo ""
echo -e "${GREEN}🎯 Expected Result:${NC}"
echo "Your Smart Dispute Canada app will be live at:"
echo "- https://${DOMAIN}"
echo "- https://www.${DOMAIN}"
echo "- https://${DOMAIN}/health (health check)"
echo "- https://${DOMAIN}/admin (admin dashboard)"
echo "- admin@${DOMAIN} (e-transfer email)"

echo ""
echo -e "${YELLOW}🍁 Smart Dispute Canada - Defending Charter Rights${NC}"
echo -e "${GREEN}⚖️  Professional legal platform ready for Canadians!${NC}"