#!/bin/bash

# Simple deployment script for Weather Datetime API

set -e

# Default values
AWS_REGION=${AWS_REGION:-us-east-1}
PROJECT_NAME="weather-datetime-api"
IMAGE_TAG=$e{IMAGE_TAG:-latest}

echo "=== Weather Datetime API Deployment ==="
echo "AWS Region: $AWS_REGION"
echo "Project: $PROJECT_NAME"
echo "Image Tag: $IMAGE_TAG"

# Step 1: Create ECR repository
echo "Step 1: Creating ECR repository..."
aws ecr create-repository --repository-name $PROJECT_NAME --region $AWS_REGION || true

# Step 2: Build and push Docker image
echo "Step 2: Building and pushing Docker image..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}"

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URL
docker build -t "${ECR_URL}:${IMAGE_TAG}" .
docker push "${ECR_URL}:${IMAGE_TAG}"

# Step 3: Deploy with Terraform
echo "Step 3: Deploying with Terraform..."
cd terraform

# Create terraform.tfvars if it doesn't exist
if [[ ! -f terraform.tfvars ]]; then
  cp terraform.tfvars.example terraform.tfvars
  sed -i "s|your-openweather-api-key-here|${OPENWEATHER_API_KEY}|g" terraform.tfvars
  sed -i "s|123456789012.dkr.ecr.us-east-1.amazonaws.com/weather-datetime-api|${ECR_URL}|g" terraform.tfvars
fi

terraform init
terraform plan
terraform apply -auto-approve

echo "Deployment completed!"
echo "API Endpoints:"
terraform output -json | jq -r '.api_endpoints.value | to_entries[] | "\(.key): \(.value)'
