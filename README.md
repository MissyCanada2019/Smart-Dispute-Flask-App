# Smart Dispute - Canadian Legal Self-Advocacy Platform

A comprehensive AI-powered platform helping Canadians navigate family court, tribunal proceedings, and parental rights with confidence.

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

3. **Set API Keys:**
   ```bash
   gcloud run services update smartdispute-app \
     --region us-central1 \
     --set-env-vars OPENAI_API_KEY=your_openai_key,ANTHROPIC_API_KEY=your_anthropic_key
   ```

## 🌟 Features

### Core Functionality
- **AI-Powered Case Analysis** - Merit scoring and evidence analysis using GPT-4 and Claude
- **Canadian Court Forms** - All provinces and territories supported with AI pre-filling
- **Secure File Storage** - End-to-end encryption for sensitive legal documents
- **Progress Tracking** - Case milestones and deadline management
- **E-Transfer Payments** - Integrated Canadian payment processing

### Provincial Coverage
- Ontario (ON) - Family Court, Superior Court
- British Columbia (BC) - Provincial & Supreme Court
- Alberta (AB) - Provincial Court, Queen's Bench
- Quebec (QC) - Superior Court, Court of Quebec
- All other provinces and territories supported

### Security Features
- Fernet encryption for file storage
- Access control and audit logging
- CSRF protection and secure sessions
- Comprehensive error handling and monitoring

## 💰 Payment Integration

**E-Transfer Address:** `admin@justice-bot.command`

**Service Pricing (CAD):**
- Case Analysis: $49.99
- Form Assistance: $29.99
- Document Review: $39.99
- Full Service Package: $149.99

## 🛠 Technical Stack

- **Backend:** Python Flask with SQLAlchemy ORM
- **AI Services:** OpenAI GPT-4, Anthropic Claude
- **File Processing:** OCR with Tesseract, PDF processing
- **Security:** Fernet encryption, access controls
- **Deployment:** Google Cloud Run, Docker containerization
- **Database:** SQLite (development), PostgreSQL (production)

## 📝 Key Routes

### User Routes
- `/` - Welcome and onboarding page
- `/dashboard` - Main user dashboard
- `/case/create` - Create new legal case
- `/evidence/upload` - Upload evidence files
- `/forms/available` - Browse court forms
- `/payment` - Payment dashboard

### Admin Routes
- `/admin` - Admin dashboard
- `/admin/users` - User management
- `/admin/forms` - Form template management
- `/admin/notifications` - Notification management

### API Routes
- `/health` - Health check endpoint
- `/api/stats` - System statistics
- `/payment/api/pricing` - Service pricing

## 🚀 Getting Started

1. **Create Account** - Sign up and verify email
2. **Create Case** - Describe your legal situation
3. **Upload Evidence** - Add documents and files
4. **Get AI Analysis** - Receive merit scoring and insights
5. **Complete Forms** - AI-assisted court form completion
6. **Track Progress** - Monitor case milestones and deadlines

## 🔐 Security & Privacy

- **End-to-end encryption** for all sensitive documents
- **Audit logging** for all file access and modifications
- **Canadian privacy compliance** with secure data handling
- **Regular security monitoring** and error logging

## 📊 Monitoring & Health

- Health check: `https://your-domain.com/health`
- Application logs in `/logs` directory
- Real-time monitoring and error tracking
- Performance metrics and usage analytics

## 🏗 Development

### Local Setup
```bash
pip install -r requirements.txt
python main.py
```

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export FLASK_ENV="development"
```

### Database Migration
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📞 Support

For technical support or legal questions, contact the admin team through the platform's notification system.

## ⚖️ Legal Disclaimer

**This platform provides self-advocacy assistance and is not legal advice.** While our AI provides analysis and form assistance, it does not replace qualified legal counsel. For complex matters, consider consulting with a licensed lawyer.

---

**Smart Dispute** - Empowering Canadian legal self-advocacy through AI technology.