import subprocess
import sys
import time

def run_command(command):
    """Run a shell command and print output"""
    print(f"\n> {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    return process.poll()

def main():
    # Step 1: Build the Docker image
    print("Building Docker image...")
    if run_command("docker build -t feedback-dashboard .") != 0:
        print("Failed to build Docker image")
        sys.exit(1)
        
    # Step 2: Login to AWS (ensure you've already configured AWS CLI with 'aws configure')
    print("\nEnsuring AWS credentials are configured...")
    if run_command("aws sts get-caller-identity") != 0:
        print("AWS credentials not configured. Please run 'aws configure' first.")
        sys.exit(1)
    
    # Step 3: Create DynamoDB table if it doesn't exist
    print("\nCreating DynamoDB table if it doesn't exist...")
    run_command("""
    aws dynamodb create-table --table-name feedback \
        --attribute-definitions AttributeName=id,AttributeType=S \
        --key-schema AttributeName=id,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region us-east-1
    """)
    print("Note: If the table already exists, you'll see an error which you can ignore.")
    
    # Step 4: Deploy manually to Amazon Lightsail
    print("\n=== INSTRUCTIONS FOR MANUAL DEPLOYMENT TO AMAZON LIGHTSAIL ===")
    print("""
1. Sign in to the AWS Management Console and open the Lightsail console:
   https://console.aws.amazon.com/lightsail/

2. Choose Container services in the left navigation pane.

3. Choose "Create container service".

4. Select a region (us-east-1 is recommended for this deployment).

5. Choose the "Small" container service plan.

6. Enter "feedback-dashboard" as the name for your container service.

7. Choose "Setup your first deployment" and then select "Specify a custom deployment".

8. For the container name, enter "app".

9. For the image, use Docker Hub. Since we can't directly upload from Docker Desktop,
   you need to push the image to Docker Hub first. If you haven't already:
   
   a. Create a Docker Hub account at https://hub.docker.com/
   b. On your local machine, tag the image:
      docker tag feedback-dashboard yourusername/feedback-dashboard
   c. Login to Docker Hub:
      docker login
   d. Push the image:
      docker push yourusername/feedback-dashboard
   e. Use "yourusername/feedback-dashboard:latest" as the image in Lightsail

10. Set the port to 8501.

11. In the Environment variables section, add:
    - AWS_REGION: us-east-1

12. Click "Add open ports" and add port 8501 with protocol HTTP.

13. Under Public endpoint, choose the "app" container and port 8501.

14. Choose "Create container service".

15. After deployment is complete, note the URL of your container service. It will be:
    https://your-service-name.region.lightsail.aws.com

16. Set up IAM permissions for DynamoDB:
    a. Go to IAM console: https://console.aws.amazon.com/iam/
    b. Create a role with the following trust policy:
       {
         "Version": "2012-10-17",
         "Statement": [
           {
             "Effect": "Allow",
             "Principal": {
               "Service": "lightsail.amazonaws.com"
             },
             "Action": "sts:AssumeRole"
           }
         ]
       }
    c. Attach the "AmazonDynamoDBFullAccess" policy to this role
    d. Back in the Lightsail container service console, attach this role to your container service
    """)
    
    print("\nFor more information on Lightsail container services, visit:")
    print("https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-container-services")

if __name__ == "__main__":
    main() 