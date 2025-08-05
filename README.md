# Smart Dispute - Canadian Legal Self-Advocacy Platform

A comprehensive platform helping Canadians navigate family court, tribunal proceedings, and parental rights with confidence.

## 🚀 Quick Deployment

### Deploy to Google Cloud Run (Ready for Production)

1. **One-Click Deploy:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Manual Deploy:**
   ```bash
   gcloud run deploy smartdispute-app \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --set-env-vars "FLASK_ENV=production"
   ```

3. **Set Domain Configuration:**
   ```bash
   gcloud run services update smartdispute-app \
     --region us-central1 \
     --set-env-vars APP_DOMAIN=justice-bot.com
   ```

## 🌟 Features

### Core Functionality
- **Canadian Court Forms** - All provinces and territories supported
- **Secure File Storage** - End-to-end encryption for sensitive legal documents
- **Progress Tracking** - Case milestones and deadline management
- **E-Transfer Payments** - Integrated Canadian payment processing
- **Document Automation** - AI-assisted form filling and document generation

### Justice-bot.com Integration
- All services connected to Justice-bot.com domain
- Unified authentication and user management
- Centralized case management dashboard

## 🔒 Security
- All data encrypted at rest and in transit
- Regular security audits
- Compliance with Canadian privacy laws (PIPEDA)

## 🛠️ Development
```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run locally
python main.py
```

## 📄 License
This project is licensed under the [Justice-bot.com Platform Agreement](https://justice-bot.com/terms)