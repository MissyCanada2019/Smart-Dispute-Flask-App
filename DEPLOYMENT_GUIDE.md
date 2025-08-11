# Deployment Guide - Enhanced Health Check Functionality

## Overview

This guide provides step-by-step instructions for deploying the enhanced health check functionality for the Smart Dispute Canada Flask application.

## Prerequisites

1. Access to the Railway account where the application is deployed
2. Git repository access
3. Railway CLI installed and configured
4. Required environment variables (see RAILWAY_ENV_SETUP_GUIDE.md)

## Deployment Steps

### 1. Verify Code Changes

Ensure all code changes have been committed to the repository:

- `utils/error_handling.py` - Contains all enhanced health check methods
- `requirements.txt` - Includes `psutil==5.9.5` dependency
- All debugging documentation files

### 2. Check Git Branch

The deployment script (`deploy.sh`) checks if you're on the `main` branch. If not, you'll be prompted to confirm deployment.

### 3. Prepare Environment Variables

Ensure you have a `railway.env` file with all required environment variables:

- `FLASK_ENV=production`
- `SECRET_KEY=your-secure-key-here`
- `DATABASE_URL=postgresql://user:pass@host/dbname`
- Any other required variables (OpenAI API key, etc.)

### 4. Run Deployment Script

Execute the deployment script:

```bash
./deploy.sh
```

This script will:

1. Check for the `railway.env` file
2. Verify you're on the correct Git branch
3. Set Railway variables from the `railway.env` file
4. Deploy the application to Railway

### 5. Alternative Deployment Method

If you prefer to deploy manually:

1. Commit and push changes to the repository:

```bash
git add .
git commit -m "Add enhanced health check functionality"
git push origin main
```

1. Set environment variables in Railway:

```bash
railway variables set -f railway.env
```

3. Deploy the application:

```bash
railway up
```

### 6. Verify Deployment

After deployment, verify that the enhanced health check functionality is working:

1. Check the application logs for any errors
2. Access the health check endpoint:

```
curl https://smartdisputecanada.me/health
```

3. Verify that the response includes all enhanced health check information:
   - Memory usage
   - CPU usage
   - Disk space usage
   - Environment variable validation
   - SSL certificate validation
   - Cache service connectivity
   - Email service connectivity
   - Enhanced database statistics

### 7. Run Verification Script

After deployment, run the verification script to ensure file integrity:

```bash
bash scripts/verify_deployment.sh
```

## Enhanced Health Check Features

The enhanced health check now includes:

1. **Memory Usage Monitoring** - Reports system memory usage with warnings for high usage
2. **CPU Usage Monitoring** - Reports CPU usage with warnings for high usage
3. **Disk Space Monitoring** - Reports disk space usage with warnings for high usage
4. **Environment Variable Validation** - Validates critical environment variables are set
5. **SSL Certificate Validation** - Checks SSL certificate validity for the main domain
6. **Cache Service Connectivity** - Tests cache service connectivity (Redis/Memcached)
7. **Email Service Connectivity** - Tests email service connectivity (SMTP)
8. **Enhanced Database Statistics** - Provides more detailed database statistics

## Troubleshooting

### Common Issues

1. **Missing psutil dependency**:
   - Ensure `psutil==5.9.5` is in `requirements.txt`
   - Check Railway build logs for installation errors

2. **SSL Certificate Validation Failures**:
   - Verify network connectivity to the domain
   - Check firewall or proxy settings

3. **Environment Variable Issues**:
   - Verify all required environment variables are set in Railway
   - Check Railway variables tab for correct values

4. **Service Connectivity Issues**:
   - Verify cache and email services are properly configured
   - Check service credentials and connection parameters

## Rollback Plan

If issues are encountered after deployment:

1. Revert to the previous deployment in Railway
2. Check application logs for error messages
3. Verify environment variables are correctly set
4. Contact support if issues persist

## Conclusion

The enhanced health check functionality provides comprehensive monitoring of the application's health, including system resources, environment configuration, and service connectivity. This will help identify potential issues before they affect users and provide valuable diagnostic information for troubleshooting.
