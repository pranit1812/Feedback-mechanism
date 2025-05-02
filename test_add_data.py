import json
import os
from datetime import datetime, timedelta

# Generate test data with various sentiment values
test_data_list = [
    {
        "id": "test-123",
        "projectName": "Project Alpha",
        "query": "How does this work?",
        "answer": "It works like this: first you connect to the API, then you send your request...",
        "sentiment": "up",
        "user.id": "user-123",
        "user.email": "user1@example.com",
        "searchMethod": "direct",
        "timestamp": (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "test-124",
        "projectName": "Project Alpha",
        "query": "Why is my code not working?",
        "answer": "There might be a syntax error in your implementation.",
        "sentiment": "down",
        "user.id": "user-456",
        "user.email": "user2@example.com",
        "searchMethod": "search",
        "timestamp": (datetime.now() - timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "test-125",
        "projectName": "Project Beta",
        "query": "How do I implement authentication?",
        "answer": "You should use JWT tokens for authentication and store them securely.",
        "sentiment": "up",
        "user.id": "user-789",
        "user.email": "user3@example.com",
        "searchMethod": "direct",
        "timestamp": (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "test-126",
        "projectName": "Project Beta",
        "query": "What's the best database for my app?",
        "answer": "It depends on your specific requirements. For relational data, consider PostgreSQL...",
        "sentiment": "comment",
        "user.id": "user-987",
        "user.email": "user4@example.com",
        "searchMethod": "recommended",
        "commentText": "This was helpful, but I would like more specific examples for my use case.",
        "timestamp": (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "test-127",
        "projectName": "Project Gamma",
        "query": "How do I deploy to production?",
        "answer": "You need to configure your deployment settings in the CI/CD pipeline.",
        "sentiment": "down",
        "user.id": "user-654",
        "user.email": "user5@example.com",
        "searchMethod": "search",
        "timestamp": (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "test-128",
        "projectName": "Project Gamma",
        "query": "Can you explain how the API works?",
        "answer": "Our API uses REST principles with JSON for data exchange...",
        "sentiment": "comment",
        "user.id": "user-321",
        "user.email": "user6@example.com",
        "searchMethod": "direct",
        "commentText": "Great explanation! Could you also provide an example request?",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

# Ensure data directory exists
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Path to the JSON file
data_file = os.path.join(data_dir, "feedback_data.json")

# Clear existing data and add new test data
with open(data_file, "w") as f:
    json.dump(test_data_list, f, indent=2)

print(f"Test data added successfully! Total items: {len(test_data_list)}")
print(f"Data saved to: {os.path.abspath(data_file)}")
print("Refresh your Streamlit dashboard to see the new data.")
print("\nTest data includes:")
print(f"- {sum(1 for item in test_data_list if item['sentiment'] == 'up')} positive feedbacks (up)")
print(f"- {sum(1 for item in test_data_list if item['sentiment'] == 'down')} negative feedbacks (down)")
print(f"- {sum(1 for item in test_data_list if item['sentiment'] == 'comment')} comments") 