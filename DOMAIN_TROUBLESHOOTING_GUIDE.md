# Smart Dispute Canada Domain Troubleshooting Guide

Follow these steps to diagnose and resolve domain issues:

## Step 1: Verify DNS Configuration
```bash
chmod +x scripts/verify_domain.sh
./scripts/verify_domain.sh
```

### Expected Output:
- Green checkmarks for all DNS records
- Valid SSL certificate dates
- Cloudflare proxy enabled

## Step 2: Check SSL Certificates
```bash
chmod +x scripts/check_ssl_certificates.sh
./scripts/check_ssl_certificates.sh
```

### Key Things to Check:
1. Certificate pack status should be "active"
2. Validation method should be correct (HTTP/TXT/CNAME)
3. Universal SSL should be enabled

## Step 3: Common Issues & Solutions

### Issue 1: DNS Propagation Delay
```bash
# Check propagation globally
dig +trace smartdisputecanada.me
```

**Solution:** Wait 24-48 hours for DNS changes to propagate globally

### Issue 2: SSL Certificate Pending
```bash
# Force certificate validation
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/ssl/verification/YOUR_CERT_ID" \
  -H "X-Auth-Email: YOUR_EMAIL" \
  -H "X-Auth-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"validation_method":"http"}'
```

**Solution:** Manually trigger validation using above command

### Issue 3: Cloudflare Proxy Disabled
```bash
# Enable Cloudflare proxy
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/dns_records/YOUR_DNS_RECORD_ID" \
  -H "X-Auth-Email: YOUR_EMAIL" \
  -H "X-Auth-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  --data '{"proxied":true}'
```

**Solution:** Ensure all DNS records have proxy enabled (orange cloud)

## Step 4: Final Verification
```bash
# Check website availability
curl -I https://smartdisputecanada.me
curl -I https://www.smartdisputecanada.me

# Check health endpoint
curl https://smartdisputecanada.me/health
```

## Step 5: Railway Configuration
```bash
# Verify Railway domain settings
railway domain list
```

## Support
If issues persist, contact:
- Cloudflare Support: https://support.cloudflare.com
- Railway Support: https://docs.railway.app/help