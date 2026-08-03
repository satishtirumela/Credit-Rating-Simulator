#!/usr/bin/env bash
# Deployment script for Credit Rating Simulator to Google Cloud Run

set -e

PROJECT_ID="credit-rating-simulator"
SERVICE_NAME="credit-rating-simulator"
REGION="us-central1"

echo "================================================================================"
echo "DEPLOYING CREDIT RATING SIMULATOR TO GOOGLE CLOUD RUN"
echo "Project: $PROJECT_ID | Service: $SERVICE_NAME | Region: $REGION"
echo "================================================================================"

# 1. Set active GCP project
gcloud config set project $PROJECT_ID

# 2. Enable necessary GCP APIs
echo "Enabling GCP APIs (run, secretmanager, cloudbuild)..."
gcloud services enable run.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com

# 3. Create Secret in Secret Manager for GEMINI_API_KEY if missing
if [ -n "$GEMINI_API_KEY" ]; then
    echo "Updating GEMINI_API_KEY in GCP Secret Manager..."
    echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- 2>/dev/null || \
    echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
else
    echo "[NOTE] GEMINI_API_KEY environment variable not set locally; ensure secret 'gemini-api-key' exists in Secret Manager."
fi

# 4. Build source and deploy to Cloud Run
echo "Building container and deploying service to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"

# 5. Retrieve deployed service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "================================================================================"
echo "DEPLOYMENT COMPLETE!"
echo "Service URL: $SERVICE_URL"
echo "Health Endpoint: $SERVICE_URL/health"
echo "================================================================================"

# 6. Verify health endpoint
echo "Verifying health endpoint response..."
curl -s "$SERVICE_URL/health"
echo ""
