#!/bin/bash

# Cloudflare SSL Certificate Check Script
# Uses Cloudflare API to verify SSL certificate status

set -e

echo "🔒 Cloudflare SSL Certificate Diagnostic Tool"
echo "============================================"

# Configuration
API_EMAIL="your_cloudflare_email@example.com"
API_KEY="your_cloudflare_api_key"
ZONE_ID="your_zone_id"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to make API calls with error handling
cloudflare_api() {
  endpoint=$1
  name=$2
  
  response=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/$endpoint" \
    -H "X-Auth-Email: $API_EMAIL" \
    -H "X-Auth-Key: $API_KEY" \
    -H "Content-Type: application/json" -w "\n%{http_code}")
  
  http_code=$(echo "$response" | tail -n1)
  json_response=$(echo "$response" | sed '$d')
  
  if [ "$http_code" != "200" ]; then
    echo -e "${RED}❌ $name check failed with HTTP $http_code${NC}"
    echo "$json_response" | jq '.'
    return 1
  fi
  
  echo "$json_response" | jq '.'
  return 0
}

# Check certificate packs
echo -e "${YELLOW}🔍 Checking certificate packs...${NC}"
if ! cloudflare_api "ssl/certificate_packs" "Certificate packs"; then
  echo -e "${RED}❌ Failed to retrieve certificate packs${NC}"
else
  echo -e "${GREEN}✅ Certificate packs retrieved successfully${NC}"
fi

# Check SSL verification details
echo -e "\n${YELLOW}🔍 Checking SSL verification details...${NC}"
if ! cloudflare_api "ssl/verification" "SSL verification"; then
  echo -e "${RED}❌ Failed to retrieve SSL verification details${NC}"
else
  echo -e "${GREEN}✅ SSL verification details retrieved successfully${NC}"
fi

# Check universal SSL settings
echo -e "\n${YELLOW}🔍 Checking universal SSL settings...${NC}"
if ! cloudflare_api "ssl/universal/settings" "Universal SSL settings"; then
  echo -e "${RED}❌ Failed to retrieve universal SSL settings${NC}"
else
  echo -e "${GREEN}✅ Universal SSL settings retrieved successfully${NC}"
fi

echo -e "\n${YELLOW}📝 Interpretation Guide:${NC}"
echo "1. Look for 'status' fields in certificate packs"
echo "2. Check 'validation_method' for each certificate"
echo "3. Verify 'enabled' status in universal SSL settings"
echo "4. Look for any 'errors' in the response"
echo "5. Check 'certificate_status' for pending validations"