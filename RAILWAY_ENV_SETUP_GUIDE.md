# Railway Environment Variables Setup Guide

## Required Variables for Smart Dispute Canada
| Variable | Description | Example Value | Notes |
|----------|-------------|---------------|-------|
| `FLASK_ENV` | Application environment | `production` | |
| `SECRET_KEY` | Security key for sessions | `your-secure-key-here` | **Must be changed** |
| `DATABASE_URL` | Database connection URL | `postgresql://user:pass@host/dbname` | Use Railway's PostgreSQL service |
| `OPENAI_API_KEY` | OpenAI API key | `your-actual-key` | Get from [OpenAI](https://platform.openai.com) |
| `ANTHROPIC_API_KEY` | Anthropic API key | `your-actual-key` | Get from [Anthropic](https://www.anthropic.com) |
| `MAX_CONTENT_LENGTH` | Max file upload size | `52428800` | 50MB limit |
| `UPLOAD_FOLDER` | File upload directory | `/tmp/uploads` | Use `/tmp` for ephemeral storage |
| `SESSION_COOKIE_SECURE` | HTTPS cookie setting | `True` | Always enable in production |
| `SESSION_COOKIE_HTTPONLY` | HTTP-only cookies | `True` | Security best practice |
| `SESSION_COOKIE_SAMESITE` | Same-site cookie policy | `'Lax'` | Prevents CSRF attacks |
| `WTF_CSRF_ENABLED` | CSRF protection | `True` | Form security |

## How to Add Variables in Railway
1. Go to your project dashboard: https://railway.app
2. Select your application
3. Click "Variables" tab
4. Add variables using either method:
   - **Manual entry**: Click "Add Variable" and enter KEY/VALUE pairs
   - **Upload .env file**: Click "Add Variable" > "Upload .env File" and select your file

## Important Notes
- Replace placeholder values with your actual keys
- Database should use PostgreSQL in production (Railway provides this)
- File uploads are temporary - use cloud storage for persistence
- After adding variables, Railway will automatically redeploy

## Step 5: Verify Deployment Integrity

To ensure files haven't been corrupted during deployment, run the verification script:

```bash
bash scripts/verify_deployment.sh
```

This script will:
1. Create checksums of critical files
2. Verify the checksums after deployment
3. Report any file corruption issues

> Note: If verification fails, check Railway's deployment logs for errors and consider redeploying.