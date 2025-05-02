from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
            
            # Save data to file
            data_dir = Path(__file__).resolve().parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            
            data_file = data_dir / 'feedback_data.json'
            
            # Read existing data
            existing_data = []
            if data_file.exists():
                try:
                    with open(data_file, 'r') as f:
                        existing_data = json.load(f)
                except json.JSONDecodeError:
                    # If file is corrupted, start with empty data
                    existing_data = []
            
            # Add new data
            existing_data.append(data)
            
            # Write back to file
            with open(data_file, 'w') as f:
                json.dump(existing_data, f)
            
            # Return success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Feedback data saved successfully'
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
            'message': 'Feedback API is running'
        }).encode('utf-8')) 