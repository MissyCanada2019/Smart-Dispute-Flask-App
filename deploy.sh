#!/bin/bash
# Smart Dispute Canada Deployment Script
set -e

echo "🔒 Checking secrets file"
if [ ! -f "railway.env" ]; then
  echo "❌ Error: railway.env file not found"
  exit 1
fi

echo "🌿 Checking Git branch"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "⚠️ Warning: Not on main branch (current: $CURRENT_BRANCH)"
  read -p "Continue deployment? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

echo "🚀 Deploying to Railway..."
railway variables set -f railway.env
railway up

echo "🔧 Initializing production database..."
railway run python init_db_production.py

echo "✅ Deployment complete!"
echo "📋 Next steps:"
echo "   1. Visit your application at the Railway-provided URL"
echo "   2. Log in with admin credentials:"
echo "      Email: admin@smartdispute.ca"
echo "      Password: ChangeMeImmediately2024!"
echo "   3. Change the admin password immediately after first login"
echo "   4. Configure any additional settings in the admin panel"
echo ""
echo "📝 For detailed deployment instructions, see RAILWAY_DEPLOYMENT_GUIDE.md"
echo "🌐 Monitor at https://railway.app/project/<your-project-id>"