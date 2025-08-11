# Cloudflare SSL Fix Instructions for Smart Dispute Canada

## Issue Summary
The website smartdisputecanada.me is experiencing an SSL certificate issue with the error "ERR_SSL_VERSION_OR_CIPHER_MISMATCH". Both the main domain and www subdomain are failing SSL handshake with "sslv3 alert handshake failure".

## Root Cause
The SSL certificate is not properly configured for the domain, likely due to:

1. Missing certificate for one or both domains
2. SSL/TLS version or cipher mismatch between client and server
3. Improper SSL settings in Cloudflare

## Fix Instructions

### Step 1: Access Cloudflare Dashboard
1. Log in to your Cloudflare account at https://dash.cloudflare.com
2. Select the appropriate account if you have multiple
3. Click on the "smartdisputecanada.me" domain

### Step 2: Check Current SSL Settings
1. In the dashboard, click on "SSL/TLS" in the left sidebar
2. Click on "Overview"
3. Note the current SSL/TLS encryption mode

### Step 3: Update SSL/TLS Encryption Mode
1. In the "SSL/TLS" section, click on "Edge Certificates"
2. Find "SSL/TLS encryption mode" and click "Edit"
3. Select "Full" encryption mode (not "Flexible" or "Full (strict)")
4. Click "Save"

### Step 4: Enable Additional Security Features
1. In the "Edge Certificates" section, ensure these settings are enabled:

   - Always Use HTTPS: On
   - Opportunistic Encryption: On
   - TLS 1.3: On
2. Toggle these settings to "On" if they're not already

### Step 5: Check Certificate Status
1. In the "SSL/TLS" section, click on "Origin Server"
2. Check if there's an existing certificate
3. Note its expiration date and covered domains

### Step 6: Reissue Origin Certificate (if needed)
1. In the "Origin Server" section, click "Reissue Certificate"
2. Select a validity period (15 years recommended)
3. Ensure both domains are included:

   - smartdisputecanada.me
   - *.smartdisputecanada.me
4. Click "Reissue" and confirm
5. Save the generated certificate and private key in a secure location

### Step 7: Check Edge Certificate Status
1. In the "SSL/TLS" section, click on "Edge Certificates"
2. Scroll down to "Certificate status"
3. Check if there are any issues with the certificate

### Step 8: Reinstall Edge Certificate (if needed)
1. If there are issues with the edge certificate:
   - Contact Cloudflare support for assistance
   - Or wait for automatic reissuance

### Step 9: Verify DNS Records
1. Click on "DNS" in the left sidebar
2. Verify that you have the correct records:

   - A CNAME record for "@" (root domain) pointing to your Railway app
   - A CNAME record for "www" pointing to "smartdisputecanada.me" or your Railway app
3. Ensure both records have the orange cloud (proxied) enabled

### Step 10: Wait for Propagation
1. Wait 5-15 minutes for Cloudflare to propagate the SSL settings
2. SSL certificate provisioning can take up to 30 minutes in some cases

### Step 11: Verify the Fix
1. After waiting, test both domains:
   - https://smartdisputecanada.me
   - https://www.smartdisputecanada.me
2. Check that the browser shows a secure connection (padlock icon)
3. Verify that there are no SSL warnings or errors

## Troubleshooting

### If Issues Persist After 30 Minutes

1. Check Cloudflare's SSL/TLS analyzer tool
2. Review Cloudflare's documentation on SSL errors
3. Check if there are any firewall or security rules blocking SSL traffic

### Certificate Specific Issues

1. If the certificate doesn't include both domains:
   - Contact Cloudflare support to issue a new certificate
   - Or remove and re-add the domains in Railway

### Mixed Content Issues

1. Ensure all resources are loaded over HTTPS
2. Check your application code for any hardcoded HTTP URLs

## Additional Notes
- DNS changes may take up to 24 hours to propagate globally
- SSL certificate provisioning typically takes 5-30 minutes
- Cloudflare automatically manages certificates for proxied domains
- Make sure your origin server (Railway) is properly configured to handle SSL