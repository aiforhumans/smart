# API Usage Examples

This directory contains examples of how to use the AI User Learning System API.

## Available Examples

### 1. Basic API Usage (`basic_api_usage.py`)
Demonstrates basic CRUD operations:
- Creating users
- Recording interactions
- Triggering learning
- Retrieving learned facts

### 2. Advanced Learning (`advanced_learning.py`)
Shows advanced learning scenarios:
- Pattern recognition
- Sentiment analysis
- Behavioral modeling
- Preference extraction

### 3. Privacy and Security (`privacy_examples.py`)
Demonstrates privacy features:
- Data encryption
- Anonymization
- GDPR compliance
- Audit logging

### 4. Integration Examples (`integration_examples.py`)
Shows how to integrate with:
- Web applications
- Mobile apps
- Chatbots
- Analytics systems

## Running Examples

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python database/init_db.py

# Run complete demo
python examples/demo.py

# Run interactive demo
python examples/demo.py --interactive

# Run specific scenario
python examples/demo.py --scenario 1

# Run basic API examples
python examples/basic_api_usage.py

# Test privacy features
python examples/privacy_examples.py
```

## API Quick Reference

### Create User
```python
import requests

response = requests.post('http://localhost:5000/api/users', json={
    'username': 'john_doe',
    'email': 'john@example.com',
    'data_sharing_consent': True,
    'learning_enabled': True
})
user = response.json()
```

### Record Interaction
```python
response = requests.post(f'http://localhost:5000/api/users/{user_id}/interactions', json={
    'type': 'message',
    'content': 'I love learning about artificial intelligence!',
    'source': 'web'
})
```

### Trigger Learning
```python
response = requests.post(f'http://localhost:5000/api/users/{user_id}/learn')
result = response.json()
```

### Get Learned Facts
```python
response = requests.get(f'http://localhost:5000/api/users/{user_id}/facts')
facts = response.json()
```

## Error Handling

All API endpoints return structured error responses:

```json
{
    "error": "Error type",
    "message": "Detailed error message"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `404`: Not Found
- `409`: Conflict (e.g., user already exists)
- `500`: Internal Server Error