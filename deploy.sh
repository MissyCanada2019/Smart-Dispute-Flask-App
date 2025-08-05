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
railway login
railway link
railway variables set -f railway.env
railway up

echo "✅ Deployment complete! Monitor at https://railway.app/project/<your-project-id>"