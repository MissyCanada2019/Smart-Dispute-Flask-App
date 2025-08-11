# Railway Deployment Guide for Smart Dispute Canada

## Prerequisites

1. Railway account (https://railway.app)
2. Git installed on your system
3. Railway CLI installed (`npm install -g @railway/cli`)

## Deployment Steps

### 1. Connect to Railway

```bash
railway login
```

### 2. Create a new project

```bash
railway init
```

Choose a name for your project (e.g., "smart-dispute-canada")

### 3. Add PostgreSQL database

In the Railway dashboard:
1. Go to your project
2. Click "+ New" and select "Database"
3. Choose "PostgreSQL"
4. Note the database connection details

### 4. Configure environment variables

Set the environment variables in Railway:

```bash
railway variables set -f railway.env
```

Or manually set these variables in the Railway dashboard:
- `FLASK_ENV=production`
- `SECRET_KEY` (generate a secure key)
- `DATABASE_URL` (will be automatically set by Railway when you add PostgreSQL)
- `OPENAI_API_KEY` (your OpenAI API key)
- `ANTHROPIC_API_KEY` (your Anthropic API key)

### 5. Deploy the application

```bash
railway up
```

### 6. Initialize the database

After deployment, initialize the database:

```bash
railway run python init_db_production.py
```

### 7. Configure custom domain (optional)

1. In the Railway dashboard, go to your service
2. Click "Settings"
3. Under "Domains", add your custom domain
4. Follow the instructions to configure DNS records

### 8. SSL Configuration

Railway automatically provides SSL certificates for your application. If you're using a custom domain:

1. Add your domain to Railway
2. Railway will automatically provision an SSL certificate
3. Update your DNS records as instructed

## Environment Variables

The following environment variables should be configured in Railway:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `FLASK_ENV` | Environment mode | `production` |
| `SECRET_KEY` | Flask secret key | Generate a secure random string |
| `DATABASE_URL` | PostgreSQL connection URL | Set automatically by Railway |
| `OPENAI_API_KEY` | OpenAI API key | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key | Your Anthropic API key |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Use TLS | `True` |
| `MAIL_USERNAME` | SMTP username | Your email |
| `MAIL_PASSWORD` | SMTP password | Your app password |

## Health Checks

Railway will automatically check the `/health` endpoint to monitor application health.

## Scaling

Railway automatically scales your application based on traffic. You can configure scaling settings in the Railway dashboard.

## Monitoring

Railway provides built-in logging and monitoring. You can view logs in the Railway dashboard or using the CLI:

```bash
railway logs
```

## Troubleshooting

### Common Issues

1. **Database connection errors**: Ensure `DATABASE_URL` is correctly set
2. **SSL certificate issues**: Check that certificate files are in the correct location
3. **Environment variables not set**: Verify all required variables are configured

### Checking Logs

```bash
railway logs
```

### Running Commands

```bash
railway run <command>
```

For example, to run the database initialization:
```bash
railway run python init_db_production.py
```

## Next Steps

1. Configure your custom domain
2. Set up monitoring and alerts
3. Configure backup strategies for your database
4. Test all application features in the production environment