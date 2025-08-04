#!/bin/bash

# Railway Cloudflare Setup Script
# Automates adding Cloudflare API key to Railway environment

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Error: Railway CLI not found. Please install it first."
    echo "Installation instructions: https://docs.railway.app/develop/cli"
    exit 1
fi

# Check if user is logged in to Railway
if ! railway status &> /dev/null; then
    echo "Please log in to Railway..."
    railway login
fi

# Get Cloudflare API key from user
read -p "Enter your Cloudflare API key: " cf_api_key

# Add environment variable to Railway
echo "Adding CLOUDFLARE_API_KEY to Railway environment..."
railway variables set CLOUDFLARE_API_KEY=$cf_api_key

# Verify the variable was set
echo "Verifying environment variable..."
railway variables list | grep CLOUDFLARE_API_KEY

echo "Setup complete! Your Cloudflare API key is now securely stored in Railway."