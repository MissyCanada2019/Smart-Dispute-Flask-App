#!/bin/bash

# Smart Dispute Canada Domain Verification Script
# Checks all aspects of domain configuration for troubleshooting

set -e

echo "🔍 Smart Dispute Canada Domain Verification"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="smartdisputecanada.me"
RAILWAY_PROJECT="smartdispute-canada"
CLOUDFLARE_ZONE="5d457b0db02ae32d7af7cef5c6d745b5"

echo -e "${BLUE}🔧 Checking DNS Configuration${NC}"
echo "---------------------------------"

# Check A record using host command
echo -e "${YELLOW}A Record (${DOMAIN}):${NC}"
host -t A $DOMAIN 2>&1 | while read line; do
  if [[ $line == *"has address"* ]]; then
    ip=$(echo $line | awk '{print $4}')
    echo -e "  IP Address: $ip"
    echo -n "  Ping Test: "
    if ping -c 1 -W 1 $ip &> /dev/null; then
      echo -e "${GREEN}Reachable ✓${NC}"
    else
      echo -e "${RED}Unreachable ✗${NC}"
    fi
  fi
done

# Check CNAME for www using host command
echo -e "${YELLOW}CNAME Record (www.${DOMAIN}):${NC}"
host -t CNAME www.$DOMAIN 2>&1 | grep "is an alias for"

# Check nameservers using host command
echo -e "${YELLOW}Nameservers:${NC}"
host -t NS $DOMAIN 2>&1 | grep "name server"

echo -e "${BLUE}🔒 Checking SSL/TLS Configuration${NC}"
echo "------------------------------------"

# Check HTTPS connectivity
echo -e "${YELLOW}HTTPS Connection:${NC}"
if curl -s -I https://$DOMAIN --max-time 10 | grep "200 OK"; then
  echo -e "${GREEN}HTTPS connection successful ✓${NC}"
else
  echo -e "${RED}HTTPS connection failed ✗${NC}"
fi

# Check SSL certificate
echo -e "${YELLOW}SSL Certificate:${NC}"
openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -dates

echo -e "${BLUE}🌐 Checking Cloudflare Configuration${NC}"
echo "--------------------------------------"

# Check Cloudflare proxy status
echo -e "${YELLOW}Cloudflare Proxy Status:${NC}"
curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE/dns_records?name=$DOMAIN" \
  -H "Authorization: Bearer $CLOUDFLARE_API_KEY" \
  -H "Content-Type: application/json" | jq '.result[0].proxied'

# Check Cloudflare SSL mode
echo -e "${YELLOW}Cloudflare SSL Mode:${NC}"
curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE/settings/ssl" \
  -H "Authorization: Bearer $CLOUDFLARE_API_KEY" \
  -H "Content-Type: application/json" | jq '.result.value'

echo -e "${BLUE}🚆 Checking Railway Configuration${NC}"
echo "------------------------------------"

# Check Railway domain configuration
echo -e "${YELLOW}Railway Domain Status:${NC}"
railway domain list --project $RAILWAY_PROJECT

# Check Railway environment variables
echo -e "${YELLOW}Cloudflare API Key Configured:${NC}"
railway variables list --project $RAILWAY_PROJECT | grep CLOUDFLARE_API_KEY

echo -e "${BLUE}✅ Verification Complete${NC}"
echo "=========================================="
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Check DNS propagation with: dig +trace $DOMAIN"
echo "2. Test HTTPS manually: curl -vI https://$DOMAIN"
echo "3. Check Railway logs: railway logs --project $RAILWAY_PROJECT"
echo "4. Review Cloudflare dashboard for any warnings"