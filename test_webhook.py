import requests
import json

# Test the webhook endpoint directly
url = "http://localhost:5000/webhook/chat/message"
headers = {
    "Authorization": "Bearer dev-webhook-key-change-in-production",
    "Content-Type": "application/json"
}

data = {
    "user_id": "test_user",
    "message": "Hello test",
    "response": "Hi there!",
    "metadata": {"source": "test"}
}

print("Testing webhook endpoint...")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")