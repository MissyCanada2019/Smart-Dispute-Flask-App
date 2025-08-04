#!/bin/bash

# Cloud Run Cloudflare Setup Script
# Automates adding Cloudflare API key to Cloud Run environment variables

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found. Please install it first."
    echo "Installation instructions: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in to gcloud
if ! gcloud auth list | grep -q "ACTIVE"; then
    echo "Please log in to gcloud..."
    gcloud auth login
fi

# Set project
read -p "Enter your Google Cloud project ID: " project_id
gcloud config set project $project_id

# Get Cloudflare API key from user
read -p "Enter your Cloudflare API key: " cf_api_key

# Get Cloud Run service name
read -p "Enter your Cloud Run service name: " service_name
read -p "Enter your Cloud Run region (e.g., us-central1): " region

# Add environment variable to Cloud Run
echo "Adding CLOUDFLARE_API_KEY to Cloud Run service $service_name..."
gcloud run services update $service_name \
  --region=$region \
  --set-env-vars="CLOUDFLARE_API_KEY=$cf_api_key"

echo "Setup complete! Your Cloudflare API key is now securely stored in Cloud Run."