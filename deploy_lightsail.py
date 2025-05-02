#!/usr/bin/env python3
import os
import json
import time
import subprocess
import boto3
import sys

# Configuration
AWS_REGION = "us-east-1"
SERVICE_NAME = "feedback-dashboard"
CONTAINER_LABEL = "feedback-dashboard"
ROLE_NAME = "lightsail-dynamodb-role"
SERVICE_POWER = "small"
SERVICE_SCALE = 1

def run_command(command):
    """Run a shell command and return output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def check_prerequisites():
    """Check if required tools are installed"""
    print("Checking prerequisites...")
    
    # Check AWS CLI
    aws_version = run_command("aws --version")
    if not aws_version:
        print("AWS CLI not found. Please install AWS CLI and configure it.")
        return False
    print(f"AWS CLI: {aws_version}")
    
    # Check Docker
    docker_version = run_command("docker --version")
    if not docker_version:
        print("Docker not found. Please install Docker Desktop.")
        return False
    print(f"Docker: {docker_version}")
    
    # Check AWS credentials
    sts = boto3.client('sts')
    try:
        identity = sts.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        return True
    except Exception as e:
        print(f"AWS credentials not configured: {str(e)}")
        print("Please run 'aws configure' to set up your AWS credentials.")
        return False

def build_docker_image():
    """Build the Docker image"""
    print("\nBuilding Docker image...")
    try:
        # Using subprocess.run with check=True to raise an exception if command fails
        subprocess.run(f"docker build -t {CONTAINER_LABEL} .", shell=True, check=True, text=True)
        # Verify image exists
        result = run_command(f"docker images {CONTAINER_LABEL} -q")
        if result:
            print("Successfully built Docker image.")
            return True
        else:
            print("Failed to verify Docker image after build.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Docker image: {str(e)}")
        return False
    except Exception as e:
        print(f"An error occurred during Docker build: {str(e)}")
        return False

def create_iam_role():
    """Create or update IAM role for DynamoDB access"""
    print("\nSetting up IAM role for DynamoDB access...")
    
    # Create IAM client
    iam = boto3.client('iam')
    
    # Check if role already exists
    try:
        iam.get_role(RoleName=ROLE_NAME)
        print(f"Role {ROLE_NAME} already exists. Updating policies...")
    except iam.exceptions.NoSuchEntityException:
        # Create trust policy document
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lightsail.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        # Create role
        iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for Lightsail to access DynamoDB"
        )
        print(f"Created role: {ROLE_NAME}")
    
    # Attach DynamoDB policy
    iam.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    )
    print("Attached DynamoDB access policy to role.")
    
    # Get role ARN
    response = iam.get_role(RoleName=ROLE_NAME)
    return response['Role']['Arn']

def push_to_lightsail():
    """Push Docker image to Lightsail container service"""
    print("\nPushing Docker image to Lightsail...")
    result = run_command(f"aws lightsail push-container-image --region {AWS_REGION} --service-name {SERVICE_NAME} --label {CONTAINER_LABEL} --image {CONTAINER_LABEL}")
    if not result:
        print("Failed to push image to Lightsail.")
        return None
    
    # Extract image name from result
    lines = result.split('\n')
    for line in lines:
        if "Refer to this image as" in line:
            image_name = line.split('"')[1]
            print(f"Image pushed successfully: {image_name}")
            return image_name
    
    return None

def update_container_json(image_name):
    """Update the container JSON file with the correct image name"""
    print(f"\nUpdating container JSON with image: {image_name}")
    
    # Read container JSON
    with open('lightsail-container.json', 'r') as f:
        container_json = json.load(f)
    
    # Update image name
    container_json['containers']['app']['image'] = image_name
    
    # Write updated JSON
    with open('lightsail-container.json', 'w') as f:
        json.dump(container_json, f, indent=2)
    
    print("Updated lightsail-container.json")
    return True

def create_or_update_service():
    """Create or update Lightsail container service"""
    print("\nSetting up Lightsail container service...")
    
    # Check if service exists
    result = run_command(f"aws lightsail get-container-service --service-name {SERVICE_NAME}")
    if result:
        print(f"Container service {SERVICE_NAME} already exists. Updating...")
        run_command(f"aws lightsail update-container-service --service-name {SERVICE_NAME} --power {SERVICE_POWER} --scale {SERVICE_SCALE}")
    else:
        print(f"Creating new container service: {SERVICE_NAME}")
        run_command(f"aws lightsail create-container-service --service-name {SERVICE_NAME} --power {SERVICE_POWER} --scale {SERVICE_SCALE}")
    
    # Wait for service to be ready
    print("Waiting for service to be ready...")
    time.sleep(10)
    
    return True

def attach_role_to_service(role_arn):
    """Attach IAM role to container service"""
    print(f"\nAttaching role to container service...")
    result = run_command(f"aws lightsail set-container-service-role --service-name {SERVICE_NAME} --role-arn {role_arn}")
    if result is None:
        print(f"Successfully attached role {role_arn} to service.")
        return True
    else:
        print(f"Failed to attach role to service: {result}")
        return False

def deploy_container():
    """Deploy container to Lightsail service"""
    print("\nDeploying container to Lightsail...")
    result = run_command(f"aws lightsail create-container-service-deployment --service-name {SERVICE_NAME} --containers file://lightsail-container.json --public-endpoint file://lightsail-container.json")
    if result is None:
        print("Deployment initiated successfully.")
        return True
    else:
        print(f"Failed to deploy container: {result}")
        return False

def wait_for_deployment():
    """Wait for deployment to complete and get the URL"""
    print("\nWaiting for deployment to complete...")
    lightsail = boto3.client('lightsail', region_name=AWS_REGION)
    
    while True:
        response = lightsail.get_container_service(serviceName=SERVICE_NAME)
        state = response['containerService']['state']
        print(f"Service state: {state}")
        
        if state == "ACTIVE":
            url = response['containerService']['url']
            print(f"\nDeployment completed successfully!")
            print(f"Your application is available at: https://{url}")
            print(f"API endpoint: https://{url}/api/feedback")
            return url
        elif state in ["DEPLOYING", "PENDING", "READY"]:
            print("Still deploying... checking again in 30 seconds")
            time.sleep(30)
        else:
            print(f"Unexpected state: {state}. Please check the AWS Lightsail console.")
            return None

def main():
    """Main deployment function"""
    print("==== Feedback Dashboard Deployment to Amazon Lightsail ====\n")
    
    if not check_prerequisites():
        sys.exit(1)
    
    if not build_docker_image():
        sys.exit(1)
    
    role_arn = create_iam_role()
    
    image_name = push_to_lightsail()
    if not image_name:
        sys.exit(1)
    
    update_container_json(image_name)
    
    if not create_or_update_service():
        sys.exit(1)
    
    if not attach_role_to_service(role_arn):
        sys.exit(1)
    
    if not deploy_container():
        sys.exit(1)
    
    url = wait_for_deployment()
    if not url:
        sys.exit(1)
    
    print("\n==== Deployment completed successfully! ====")
    print(f"Dashboard URL: https://{url}")
    print(f"API Endpoint: https://{url}/api/feedback")
    print("\nTo send a test POST request to your API endpoint:")
    print(f"""
curl -X POST https://{url}/api/feedback \\
  -H "Content-Type: application/json" \\
  -d '{{
    "id": "test-1",
    "projectName": "Test Project",
    "query": "How does this work?",
    "answer": "It works by sending feedback data to the API endpoint.",
    "sentiment": "up",
    "user.id": "user-123",
    "user.email": "test@example.com",
    "searchMethod": "direct"
  }}'
""")

if __name__ == "__main__":
    main() 