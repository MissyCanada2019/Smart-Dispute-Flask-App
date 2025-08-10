# Smart Dispute Canada - Production Deployment Guide

This document provides a comprehensive guide to deploy the Smart Dispute Canada application to production without encountering 500 errors.

## Overview

The Smart Dispute Canada application is a Flask-based web application with a PostgreSQL database backend. This guide will walk you through the steps to deploy the application to Railway, a cloud platform that simplifies deployment and scaling.

## Key Changes Made to Fix 500 Errors

1. **Database Initialization**: Created proper database initialization scripts (`init_db_proper.py` and `init_db_production.py`) that create all necessary tables based on the application models.

2. **Production Environment Configuration**: Created `env.production` with proper production settings and Railway-compatible database configuration.

3. **Railway Configuration**: Updated `railway.json` to automatically initialize the database before starting the application.

4. **Database Connection Fix**: Configured the application to use Railway's PostgreSQL service automatically through environment variables.

## Deployment Steps

### 1. Repository Preparation

Ensure your repository contains the following key files:
- `main.py` - Main application file
- `railway.json` - Railway deployment configuration
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration
- `init_db_production.py` - Production database initialization script
- `env.production` - Production environment variables template

### 2. Railway Project Setup

1. Create a new project on Railway (https://railway.app)
2. Connect your GitHub repository
3. Railway will automatically detect the Flask application

### 3. Database Configuration

1. Add a PostgreSQL database service to your Railway project
2. Railway will automatically set the `DATABASE_URL` environment variable
3. No additional configuration is needed for the database connection

### 4. Environment Variables

Set the following environment variables in Railway:

```
FLASK_ENV=production
SECRET_KEY=your-secure-production-key-here
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=/tmp/uploads
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=True
```

### 5. Automatic Database Initialization

The application is configured to automatically initialize the database on startup through the `railway.json` configuration:

```json
"startCommand": "python init_db_production.py && python main.py"
```

This command will:
1. Run the database initialization script to create tables
2. Start the main application

### 6. Deployment Verification

After deployment, verify that:
1. The application starts without errors
2. The database tables are created
3. The health check endpoint (`/health`) returns a healthy status
4. You can log in with the default admin credentials

## Default Credentials

After deployment, use these credentials to log in:
- **Admin User**: admin@smartdispute.ca
- **Password**: ChangeMeImmediately2024!

⚠️ **Important**: Change the admin password immediately after first login!

## Post-Deployment Tasks

1. **Change Default Passwords**: Immediately change the admin password after first login
2. **Configure AI Services**: Add your OpenAI and Anthropic API keys
3. **Set Up Custom Domain**: Configure a custom domain if needed
4. **Monitor Logs**: Regularly check application logs for errors

## Troubleshooting

### Common Issues and Solutions

1. **500 Internal Server Error**:
   - Check deployment logs for database initialization errors
   - Verify all environment variables are set correctly
   - Ensure the database service is properly configured

2. **Database Connection Issues**:
   - Verify the PostgreSQL service is added to your project
   - Check that the `DATABASE_URL` environment variable is set

3. **Application Startup Issues**:
   - Check that all dependencies in `requirements.txt` are installed
   - Verify file permissions for the `/tmp` directory

## Security Considerations

1. **Environment Variables**: Never commit sensitive environment variables to version control
2. **HTTPS**: Railway automatically provides HTTPS for your application
3. **File Uploads**: Use `/tmp` directory for temporary file storage
4. **Session Security**: All session cookies are configured with security flags

## Monitoring and Maintenance

1. **Regular Backups**: Set up database backups through Railway
2. **Log Monitoring**: Monitor application logs for errors
3. **Performance Monitoring**: Monitor application performance and scale resources as needed

## Support

If you encounter issues that you cannot resolve:
1. Check the application logs for detailed error messages
2. Verify that all deployment steps have been completed
3. Contact the development team for assistance
4. Refer to Railway's documentation for platform-specific issues

By following this guide, you should be able to successfully deploy the Smart Dispute Canada application to production without encountering 500 errors.