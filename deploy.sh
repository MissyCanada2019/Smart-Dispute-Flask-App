#!/bin/bash

# Smart Dispute Flask App - Cloud Run Deployment Script
# Rapid deployment for Canadian legal self-advocacy platform

set -e

echo "🚀 Starting Smart Dispute deployment to Google Cloud Run..."

# Configuration
PROJECT_ID=${PROJECT_ID:-"smartdispute-legal"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="smartdispute-app"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Authenticating with Google Cloud..."
    gcloud auth login
fi

# Set project
echo "📝 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy
echo "🏗️ Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 80 \
    --max-instances 10 \
    --set-env-vars "FLASK_ENV=production,PYTHONPATH=/app" \
    --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Your Smart Dispute app is live at: $SERVICE_URL"
echo ""
echo "📋 Next steps:"
echo "1. Set up your OpenAI API key: gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars OPENAI_API_KEY=your_key"
echo "2. Set up your Anthropic API key: gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars ANTHROPIC_API_KEY=your_key"
echo "3. Configure custom domain (optional): https://cloud.google.com/run/docs/mapping-custom-domains"
echo ""
echo "💰 E-transfer payments configured for: admin@justice-bot.command"
echo "🔐 Health check available at: $SERVICE_URL/health"
echo "👑 Admin dashboard at: $SERVICE_URL/admin"