# SSL Configuration Guide for Smart Dispute Canada

## Overview

This guide explains how to configure SSL/TLS certificates for the Smart Dispute Canada Flask application. The application supports SSL both in development and production environments.

## Certificate Files

The Cloudflare Origin Certificate and Private Key have been saved to:
- Certificate: `config/certificates/smartdispute-canada.me.pem`
- Private Key: `config/certificates/smartdispute-canada.me.key`

## Development Environment SSL Configuration

The Flask application can be run with SSL support in development by simply having the certificate files in the expected location. The application will automatically detect and use them.

### Running with SSL in Development

```bash
python main.py
```

The application will automatically use the SSL certificates if they are found in the default location.

### Custom Certificate Paths

You can specify custom paths for the SSL certificate and key using environment variables:

```bash
export SSL_CERT_PATH=/path/to/your/certificate.pem
export SSL_KEY_PATH=/path/to/your/private.key
python main.py
```

## Production Deployment with Railway

### Option 1: Railway Automatic SSL (Recommended)

Railway automatically provisions and manages SSL certificates for custom domains using Let's Encrypt. This is the recommended approach for most deployments.

1. Add your custom domain in the Railway dashboard:
   - Go to your Railway project
   - Navigate to Settings → Domains
   - Add your domain (e.g., smartdisputecanada.me)
   - Wait 5-15 minutes for certificate provisioning

2. Configure your DNS:
   - Point your domain to the Railway-generated URL
   - For root domains, use an A record pointing to Railway's IP
   - For subdomains, use a CNAME record pointing to Railway's domain

### Option 2: Using Cloudflare Origin Certificate with Railway

If you need to use the provided Cloudflare Origin Certificate with Railway, you'll need to configure your deployment to use a custom web server that supports SSL termination.

1. The Flask application can be run with SSL support using the built-in development server:
   ```bash
   python main.py
   ```

2. For production deployments with SSL, consider using a reverse proxy like Nginx or a WSGI server like Gunicorn with a separate SSL termination layer.

## Cloudflare Configuration

When using Cloudflare as a CDN:

1. Set SSL/TLS encryption mode to "Full" in Cloudflare dashboard
2. Ensure the Cloudflare Origin Certificate is properly installed on your origin server
3. If using Railway's automatic SSL, Cloudflare will handle the edge certificate and communicate with Railway over HTTP

## Testing SSL Configuration

You can test the SSL configuration using curl:

```bash
# Test HTTPS endpoint
curl -k https://localhost:8080/health

# Test certificate details
openssl s_client -connect localhost:8080 -showcerts
```

## Troubleshooting

### Common Issues

1. **Certificate Not Found**: Ensure certificate files exist in the expected location
2. **Permission Denied**: Check file permissions on certificate files
3. **Certificate Expired**: Check certificate expiration date
4. **Domain Mismatch**: Ensure the certificate covers your domain

### Checking Certificate Information

```bash
# Check certificate details
openssl x509 -in config/certificates/smartdispute-canada.me.pem -text -noout

# Check certificate expiration
openssl x509 -in config/certificates/smartdispute-canada.me.pem -noout -enddate
```

## Security Best Practices

1. Store certificate files securely with appropriate permissions (600 for private key)
2. Regularly update certificates before expiration
3. Use strong encryption for private keys
4. Never commit certificate files to version control
5. Monitor certificate expiration dates