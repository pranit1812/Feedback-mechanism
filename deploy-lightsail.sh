#!/bin/bash

# Set these variables
AWS_REGION="us-east-1"
SERVICE_NAME="feedback-dashboard"

# Install AWS CLI if not installed
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi

# Install Amazon Lightsail plugin
if ! aws lightsail --version &> /dev/null; then
    echo "Installing Lightsail plugin..."
    aws configure set plugins.lightsail true
fi

# Log in to AWS (if not already authenticated)
echo "Please make sure you're authenticated with AWS CLI before continuing"
echo "You can run 'aws configure' if not already authenticated"

# Build the Docker image
echo "Building Docker image..."
docker build -t $SERVICE_NAME .

# Push to Amazon Lightsail
echo "Pushing to Amazon Lightsail..."
aws lightsail push-container-image \
    --region $AWS_REGION \
    --service-name $SERVICE_NAME \
    --label feedback-dashboard \
    --image $SERVICE_NAME

# Create or update the container service
if aws lightsail get-container-services --service-name $SERVICE_NAME &> /dev/null; then
    echo "Updating existing container service..."
    aws lightsail update-container-service \
        --service-name $SERVICE_NAME \
        --power small \
        --scale 1
else
    echo "Creating new container service..."
    aws lightsail create-container-service \
        --service-name $SERVICE_NAME \
        --power small \
        --scale 1
fi

# Deploy using the container JSON file
echo "Deploying container..."
aws lightsail create-container-service-deployment \
    --service-name $SERVICE_NAME \
    --containers file://lightsail-container.json \
    --public-endpoint file://lightsail-container.json

echo "Deployment initiated. Check the AWS Lightsail console for status."
echo "Your app will be available at: https://$SERVICE_NAME.$(aws lightsail get-container-services --service-name $SERVICE_NAME --query 'containerServices[0].url' --output text)" 