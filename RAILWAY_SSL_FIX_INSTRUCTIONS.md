# Railway SSL Fix Instructions for Smart Dispute Canada

## Issue Summary
The website smartdisputecanada.me is experiencing an SSL certificate issue with the error "ERR_SSL_VERSION_OR_CIPHER_MISMATCH". Both the main domain and www subdomain are failing SSL handshake with "sslv3 alert handshake failure".

## Root Cause
The SSL certificate is not properly configured for the domain, likely due to:
1. Missing certificate for one or both domains
2. SSL/TLS version or cipher mismatch between client and server
3. Improper domain configuration in Railway

## Fix Instructions

### Step 1: Access Railway Dashboard
1. Log in to your Railway account at https://railway.app
2. Navigate to the Smart Dispute Canada project

### Step 2: Remove Existing Domains
1. In the project dashboard, click on "Settings" in the left sidebar
2. Click on "Domains" in the settings menu
3. Locate both domains:
   - smartdisputecanada.me
   - www.smartdisputecanada.me
4. Click the "Remove" button next to each domain
5. Confirm removal when prompted

### Step 3: Wait for Cleanup
1. Wait 1-2 minutes for Railway to fully remove the domains and associated certificates

### Step 4: Re-add Domains
1. In the same "Domains" section, click "Add Domain"
2. Add the main domain first:
   - Enter "smartdisputecanada.me" in the domain field
   - Click "Add Domain"
3. Wait for Railway to provision the SSL certificate (indicated by a green checkmark)
4. Add the www subdomain:
   - Click "Add Domain" again
   - Enter "www.smartdisputecanada.me" in the domain field
   - Click "Add Domain"
5. Wait for Railway to provision the SSL certificate for the subdomain

89-96tep 5: Verify DNS Records (if prompted)\
1. Railway may provide DNS records that need to be configured
2. If prompted, copy the provided DNS records
3. Configure these records in your DNS provider (likely Cloudflare)

### Step 6: Wait for Certificate Provisioning
1. Wait 5-15 minutes for Railway to fully provision the SSL certificates
2. The certificates should automatically include both domains as Subject Alternative Names (SANs)

### Step 7: Verify the Fix
1. After waiting, test both domains:
   - https://smartdisputecanada.me
   - https://www.smartdisputecanada.me
2. Check that the browser shows a secure connection (padlock icon)
3. Verify that there are no SSL warnings or errors

## Troubleshooting

### If Issues Persist After 15 Minutes
1. Check the Railway deployment logs for any errors
2. Ensure your application is running and accessible
3. Verify that the custom domains are correctly pointed to your Railway application

### If Only One Domain Works
1. Repeat the remove/re-add process for the problematic domain
2. Ensure both domains are added to the same Railway application

## Additional Notes
- DNS changes may take up to 24 hours to propagate globally
- SSL certificate provisioning typically takes 5-15 minutes but can occasionally take longer
- Make sure your application is running and accessible via the default Railway URL before configuring custom domains