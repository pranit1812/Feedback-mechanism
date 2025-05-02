from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import boto3
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from botocore.exceptions import ClientError

# Add parent directory to path so we can import from root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Helper class for DynamoDB JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

# Helper function to get DynamoDB resource
def get_dynamodb():
    # Get AWS region from environment variable or use default
    aws_region = os.environ.get("AWS_REGION", "us-east-1")
    return boto3.resource('dynamodb', region_name=aws_region)

# Function to create table if it doesn't exist
def ensure_table_exists():
    dynamodb = get_dynamodb()
    
    try:
        # Check if table exists
        existing_tables = [table.name for table in dynamodb.tables.all()]
        if 'feedback' not in existing_tables:
            # Create the feedback table
            table = dynamodb.create_table(
                TableName='feedback',
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            # Wait until the table exists
            table.meta.client.get_waiter('table_exists').wait(TableName='feedback')
            print("Created DynamoDB table: feedback")
        return True
    except Exception as e:
        print(f"Error ensuring table exists: {str(e)}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['id', 'projectName', 'query', 'answer', 'sentiment', 'user.id', 'user.email', 'searchMethod']
            
            for field in required_fields:
                if field not in data:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }).encode('utf-8'))
                    return
            
            # Validate sentiment value
            if data['sentiment'] not in ['up', 'down', 'comment']:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Sentiment must be "up", "down", or "comment"'
                }).encode('utf-8'))
                return
            
            # Check if commentText is provided when sentiment is "comment"
            if data['sentiment'] == 'comment' and 'commentText' not in data:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'commentText is required when sentiment is "comment"'
                }).encode('utf-8'))
                return
            
            # Add timestamp if not provided
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save data to DynamoDB
            try:
                # Ensure the table exists
                ensure_table_exists()
                
                # Get DynamoDB table
                dynamodb = get_dynamodb()
                table = dynamodb.Table('feedback')
                
                # Add item to DynamoDB
                table.put_item(Item=data)
                
                # Return success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': 'Feedback data saved successfully to DynamoDB'
                }).encode('utf-8'))
            except ClientError as e:
                # Handle DynamoDB-specific errors
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': f'DynamoDB error: {str(e)}'
                }).encode('utf-8'))
            
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Invalid JSON data'
            }).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode('utf-8'))
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_GET(self):
        # Simple health check endpoint
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'ok',
            'message': 'Feedback API is running with DynamoDB integration'
        }).encode('utf-8')) 