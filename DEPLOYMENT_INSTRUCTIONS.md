# Smart Dispute Canada - Deployment Instructions

This guide provides step-by-step instructions to deploy the Smart Dispute Canada application without encountering 500 errors.

## Prerequisites

1. A Railway account (https://railway.app)
2. Basic understanding of environment variables
3. Access to the application repository

## Step 1: Prepare the Repository

1. Ensure all files are committed to your repository
2. Verify that the following files exist:
   - `main.py` (main application file)
   - `railway.json` (Railway configuration)
   - `requirements.txt` (Python dependencies)
   - `Dockerfile` (Docker configuration)
   - `init_db_production.py` (Database initialization script)
   - `env.production` (Production environment variables template)

## Step 2: Create a New Railway Project

1. Go to https://railway.app and log in to your account
2. Click "New Project"
3. Select "Deploy from GitHub repo" or "Deploy from template"
4. Choose your repository

## Step 3: Configure Environment Variables

1. In your Railway project dashboard, click on the "Variables" tab
2. Add the following required environment variables:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `FLASK_ENV` | Application environment | `production` |
| `SECRET_KEY` | Security key for sessions | `your-secure-production-key-here` |
| `DATABASE_URL` | PostgreSQL connection URL | Provided by Railway PostgreSQL service |
| `OPENAI_API_KEY` | OpenAI API key | `your-openai-api-key` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `your-anthropic-api-key` |
| `MAX_CONTENT_LENGTH` | Max file upload size | `52428800` |
| `UPLOAD_FOLDER` | File upload directory | `/tmp/uploads` |
| `SESSION_COOKIE_SECURE` | HTTPS cookie setting | `True` |
| `SESSION_COOKIE_HTTPONLY` | HTTP-only cookies | `True` |
| `SESSION_COOKIE_SAMESITE` | Same-site cookie policy | `Lax` |
| `WTF_CSRF_ENABLED` | CSRF protection | `True` |

3. For the `DATABASE_URL`, Railway will automatically provide this when you add a PostgreSQL database service.

## Step 4: Add PostgreSQL Database

1. In your Railway project, click "Add Service"
2. Select "Database" and then "Add PostgreSQL"
3. Railway will automatically configure the `DATABASE_URL` environment variable
4. The database will be automatically connected to your application

## Step 5: Initialize the Database

The application is configured to automatically initialize the database on startup:

1. The `railway.json` file is configured with:
   ```json
   "startCommand": "python init_db_production.py && python main.py"
   ```
   
2. This command will:
   - Run `init_db_production.py` to create database tables
   - Start the main application with `main.py`

## Step 6: Deploy the Application

1. Railway will automatically deploy your application after you've configured the environment variables
2. Monitor the deployment logs in the "Deployments" tab
3. Wait for the deployment to complete successfully

## Step 7: Verify the Deployment

1. Once deployed, click on the generated URL to access your application
2. You should see the Smart Dispute Canada homepage
3. Test the following functionality:
   - Access the health check endpoint at `/health`
   - Try to log in with the default admin credentials:
     - Email: `admin@smartdispute.ca`
     - Password: `ChangeMeImmediately2024!`
   - Create a test user account
   - Navigate through different pages

## Step 8: Post-Deployment Tasks

1. **Change the Admin Password**:
   - Log in as `admin@smartdispute.ca` with the default password
   - Go to the admin panel
   - Change the password immediately
   
2. **Configure AI Services**:
   - Add your OpenAI and Anthropic API keys to the environment variables
   - Restart the application after adding these keys

3. **Set Up Custom Domain** (Optional):
   - In the Railway dashboard, go to "Settings" > "Domains"
   - Add your custom domain
   - Follow Railway's instructions to configure DNS records

## Troubleshooting Common Issues

### 500 Internal Server Error

If you encounter a 500 error:

1. **Check Database Initialization**:
   - Verify that the database tables were created
   - Check the deployment logs for database initialization errors
   - Run the database initialization script manually if needed:
     ```bash
     python init_db_production.py
     ```

2. **Check Environment Variables**:
   - Verify all required environment variables are set
   - Ensure the `SECRET_KEY` is properly configured
   - Check that the `DATABASE_URL` is correct

3. **Check Logs**:
   - View the application logs in the Railway dashboard
   - Look for specific error messages that indicate the cause of the issue

### Database Connection Issues

1. **Verify PostgreSQL Service**:
   - Ensure the PostgreSQL service is added to your project
   - Check that the `DATABASE_URL` environment variable is set correctly

2. **Check Database Permissions**:
   - Ensure the database user has the necessary permissions
   - Verify that the database is not overloaded

### Application Startup Issues

1. **Check Dependencies**:
   - Verify that all dependencies in `requirements.txt` are installed
   - Check for any missing or incompatible packages

2. **Check File Permissions**:
   - Ensure the application has write access to the `/tmp` directory for file uploads

## Security Considerations

1. **Change Default Credentials**:
   - Immediately change the default admin password after first login
   - Do not use default credentials in production

2. **Secure Environment Variables**:
   - Never commit sensitive environment variables to version control
   - Use Railway's built-in secrets management

3. **HTTPS**:
   - Railway automatically provides HTTPS for your application
   - Ensure all cookies are configured with `Secure` flag

## Monitoring and Maintenance

1. **Regular Backups**:
   - Set up regular database backups through Railway
   - Export important data periodically

2. **Log Monitoring**:
   - Regularly check application logs for errors
   - Set up alerts for critical errors

3. **Performance Monitoring**:
   - Monitor application performance and response times
   - Scale resources as needed based on usage

## Support

If you encounter issues that you cannot resolve:

1. Check the application logs for detailed error messages
2. Verify that all deployment steps have been completed
3. Contact the development team for assistance
4. Refer to Railway's documentation for platform-specific issues

By following these instructions, you should be able to deploy the Smart Dispute Canada application without encountering 500 errors.