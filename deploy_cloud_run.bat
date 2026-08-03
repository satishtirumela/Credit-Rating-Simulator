@echo off
rem Deployment script for Credit Rating Simulator to Google Cloud Run (Windows)

set PROJECT_ID=credit-rating-simulator
set SERVICE_NAME=credit-rating-simulator
set REGION=us-central1

echo ================================================================================
echo DEPLOYING CREDIT RATING SIMULATOR TO GOOGLE CLOUD RUN
echo Project: %PROJECT_ID% ^| Service: %SERVICE_NAME% ^| Region: %REGION%
echo ================================================================================

call gcloud config set project %PROJECT_ID%
call gcloud services enable run.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com

echo Building container and deploying service to Cloud Run...
call gcloud run deploy %SERVICE_NAME% --source . --region %REGION% --platform managed --allow-unauthenticated --set-secrets GEMINI_API_KEY=gemini-api-key:latest

echo ================================================================================
echo DEPLOYMENT COMPLETE!
echo ================================================================================
