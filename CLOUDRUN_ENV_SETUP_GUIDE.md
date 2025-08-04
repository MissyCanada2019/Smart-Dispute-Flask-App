# Google Cloud Run Environment Variables Setup Guide

## Required Variables for Smart Dispute Canada
| Variable | Description | Example Value | Notes |
|----------|-------------|---------------|-------|
| `FLASK_ENV` | Application environment | `production` | |
| `SECRET_KEY` | Security key for sessions | `your-secure-key-here` | **Must be changed** |
| `DATABASE_URL` | Database connection URL | `postgresql://user:pass@host/dbname` | Use Cloud SQL PostgreSQL |
| `CLOUDFLARE_API_KEY` | Cloudflare API key | `your-actual-key` | For SSL certificate management |
| `MAX_CONTENT_LENGTH` | Max file upload size | `52428800` | 50MB limit |
| `UPLOAD_FOLDER` | File upload directory | `/tmp/uploads` | Use `/tmp` for ephemeral storage |

## How to Add Variables in Cloud Run
1. Use the setup script to automatically configure Cloud Run:
```bash
bash scripts/setup-cloudflare-cloudrun.sh
```

2. Manual configuration:
```bash
gcloud run services update [SERVICE_NAME] \
  --region=[REGION] \
  --set-env-vars="CLOUDFLARE_API_KEY=your-key"
```

## Deployment Verification
After deployment, run the verification script:
```bash
bash scripts/verify_deployment.sh
```

This will:
1. Create checksums of critical files
2. Verify the checksums after deployment
3. Report any file corruption issues

## Important Notes
- Replace placeholder values with your actual keys
- Database should use Cloud SQL PostgreSQL in production
- File uploads are temporary - use Cloud Storage for persistence
- After adding variables, Cloud Run will automatically redeploy