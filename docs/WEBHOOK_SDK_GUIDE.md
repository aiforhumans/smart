# Webhook & SDK Integration Guide

This guide explains how to integrate your chatbots (Gradio, LM Studio, OpenAI, etc.) with the AI User Learning System using webhooks and the Python SDK.

## 🚀 Quick Start

### 1. Install the SDK

```bash
# Copy the SDK from the project
cp -r sdk/ your_project/
# Or add to Python path
sys.path.append('/path/to/smart')
```

### 2. Basic Integration

```python
from sdk import AIUserLearningSDK, ChatMessage

# Initialize SDK
sdk = AIUserLearningSDK("http://localhost:5000")

# Log a chat interaction
message = ChatMessage(
    user_id="user123",
    message="I love playing guitar",
    response="That's great! What style of music do you play?"
)

result = sdk.log_message(message)
print(f"Logged interaction: {result}")

# Get user insights
insights = sdk.get_user_insights("user123")
print(f"User facts: {insights['facts']}")
```

## 📡 Webhook Endpoints

### Authentication

All webhook endpoints require authentication via:

1. **Bearer Token**: `Authorization: Bearer YOUR_API_KEY`
2. **API Key Header**: `X-API-Key: YOUR_API_KEY`

Set your API key via environment variable:
```bash
export WEBHOOK_API_KEY="your-secure-api-key"
```

### Rate Limits

- **Message logging**: 50 requests per 5 minutes
- **Insights retrieval**: 100 requests per 5 minutes  
- **Bulk upload**: 10 requests per 5 minutes
- **Streaming**: 10 connections per 5 minutes

### Endpoints Overview

| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|------------|
| `/webhook/chat/message` | POST | Log single interaction | 50/5min |
| `/webhook/chat/insights/<user_id>` | GET | Get user insights | 100/5min |
| `/webhook/chat/bulk` | POST | Bulk upload interactions | 10/5min |
| `/webhook/stream/insights/<user_id>` | GET | Real-time insights stream | 10/5min |
| `/webhook/stream/learning/<user_id>` | GET | Learning process stream | 5/5min |

## 🔗 Detailed Webhook API

### 1. Log Chat Message

**Endpoint**: `POST /webhook/chat/message`

**Purpose**: Log a chat interaction and trigger AI learning

**Headers**:
```
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
```

**Request Body**:
```json
{
  "user_id": "user123",
  "message": "I love playing guitar and jazz music",
  "response": "That's wonderful! How long have you been playing?",
  "session_id": "optional_session_id",
  "metadata": {
    "source": "gradio",
    "model": "gpt-3.5-turbo",
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

**Response**:
```json
{
  "success": true,
  "user_id": 1,
  "interaction_id": 123,
  "learned_facts_count": 2,
  "message": "Interaction logged and processed"
}
```

### 2. Get User Insights

**Endpoint**: `GET /webhook/chat/insights/{user_id}`

**Purpose**: Retrieve user insights and facts for personalization

**Query Parameters**:
- `categories`: Comma-separated list (e.g., "interests,behavior")
- `limit`: Max facts to return (default: 10)
- `confidence`: Min confidence level ("low", "medium", "high")

**Example**:
```
GET /webhook/chat/insights/user123?categories=interests,behavior&limit=5&confidence=medium
```

**Response**:
```json
{
  "user_id": 1,
  "username": "user123",
  "facts": [
    {
      "category": "interests",
      "type": "topic_interest",
      "key": "interest_music",
      "value": "Shows strong interest in jazz music",
      "confidence": "high",
      "evidence_count": 5,
      "last_updated": "2025-01-01T12:00:00Z"
    }
  ],
  "recent_interactions": [
    {
      "content": "I love jazz music",
      "type": "message",
      "sentiment": 0.8,
      "topics": ["music", "jazz"],
      "timestamp": "2025-01-01T12:00:00Z"
    }
  ],
  "analytics": {
    "total_interactions": 25,
    "avg_sentiment": 0.6,
    "most_active_hour": 14
  },
  "suggestions": [
    "User shows interest in jazz music",
    "User prefers detailed responses"
  ]
}
```

### 3. Bulk Upload

**Endpoint**: `POST /webhook/chat/bulk`

**Purpose**: Upload multiple interactions for batch processing

**Request Body**:
```json
{
  "user_id": "user123",
  "interactions": [
    {
      "message": "Hello there",
      "timestamp": "2025-01-01T12:00:00Z",
      "metadata": {"session": "session1"}
    },
    {
      "message": "I like programming",
      "timestamp": "2025-01-01T12:01:00Z",
      "metadata": {"session": "session1"}
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "user_id": 1,
  "interactions_created": 2,
  "facts_learned": 1,
  "processing_time_ms": 150
}
```

### 4. Real-time Insights Stream

**Endpoint**: `GET /webhook/stream/insights/{user_id}`

**Purpose**: Server-Sent Events stream for real-time user insights

**JavaScript Example**:
```javascript
const eventSource = new EventSource('/webhook/stream/insights/user123');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('New insights:', data);
    
    // Update UI with new facts
    if (data.updates.new_facts > 0) {
        updateInsightsDisplay(data.latest_facts);
    }
};
```

**Stream Data Format**:
```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "user_id": 1,
  "username": "user123",
  "updates": {
    "new_facts": 1,
    "new_interactions": 2
  },
  "latest_facts": [
    {
      "category": "interests",
      "value": "Shows interest in programming",
      "confidence": "medium",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "analytics": {
    "total_interactions": 27,
    "avg_sentiment": 0.65
  }
}
```

## 🐍 Python SDK Reference

### AIUserLearningSDK

Main SDK class for API interactions.

```python
from sdk import AIUserLearningSDK

sdk = AIUserLearningSDK(
    base_url="http://localhost:5000",
    api_key="your-api-key"  # Optional
)
```

#### Methods

**`log_message(chat_message: ChatMessage) -> Dict`**
- Log a chat interaction
- Returns: API response with interaction details

**`get_user_insights(user_id: str, categories=None, limit=10, min_confidence='low') -> Dict`**
- Get user insights and facts
- Returns: User profile with facts, interactions, and analytics

**`bulk_upload(user_id: str, messages: List[str]) -> Dict`**
- Upload multiple messages for batch processing
- Returns: Processing statistics

**`get_personalization_context(user_id: str) -> str`**
- Get formatted user context for prompt injection
- Returns: Formatted string with user insights

**`health_check() -> bool`**
- Check if API is accessible
- Returns: True if healthy, False otherwise

### ChatMessage

Data class for chat interactions.

```python
from sdk import ChatMessage

message = ChatMessage(
    user_id="user123",
    message="Hello world",
    response="Hi there!",
    session_id="session_123",
    metadata={"source": "gradio"}
)
```

## 🔧 Integration Examples

### Gradio Integration

```python
from sdk import quick_gradio_setup

# Quick setup
gradio_integration = quick_gradio_setup(
    base_url="http://localhost:5000",
    user_id="gradio_user"
)

def chat_function(message, history):
    # This automatically logs interactions and applies learning
    response, updated_history = gradio_integration.chat_with_learning(
        message=message,
        chatbot_response_fn=your_response_function
    )
    return response, updated_history
```

### LM Studio Integration

```python
from sdk import quick_lm_studio_setup

# Setup LM Studio integration
lm_integration = quick_lm_studio_setup(
    learning_url="http://localhost:5000",
    lm_studio_url="http://localhost:1234/v1"
)

# Enhanced chat with learning
messages = [{"role": "user", "content": "Hello"}]
response = lm_integration.enhanced_chat_completion(
    messages=messages,
    user_id="user123",
    model="llama-2-7b-chat"
)
```

### Custom Integration

```python
import requests
from sdk import AIUserLearningSDK

class CustomChatbot:
    def __init__(self):
        self.sdk = AIUserLearningSDK("http://localhost:5000")
    
    def chat(self, user_id: str, message: str) -> str:
        # Get user context
        context = self.sdk.get_personalization_context(user_id)
        
        # Generate response with your model/API
        response = your_model_function(message, context)
        
        # Log interaction
        chat_msg = ChatMessage(
            user_id=user_id,
            message=message,
            response=response,
            metadata={"source": "custom"}
        )
        self.sdk.log_message(chat_msg)
        
        return response
```

## 🌐 Frontend Integration

### JavaScript/HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>Real-time Learning Chat</title>
</head>
<body>
    <div id="insights"></div>
    <div id="chat"></div>
    
    <script>
        // Real-time insights
        const insightsSource = new EventSource('/webhook/stream/insights/user123');
        insightsSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            document.getElementById('insights').innerHTML = 
                `<h3>Latest Insights</h3>
                 <p>Facts: ${data.latest_facts.length}</p>
                 <p>Interactions: ${data.analytics.total_interactions}</p>`;
        };
        
        // Send message function
        async function sendMessage(message) {
            const response = await fetch('/webhook/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'your-api-key'
                },
                body: JSON.stringify({
                    user_id: 'user123',
                    message: message,
                    response: 'Generated response here'
                })
            });
            
            const result = await response.json();
            console.log('Message logged:', result);
        }
    </script>
</body>
</html>
```

## 🔒 Security Best Practices

### 1. API Key Management

```bash
# Set secure API key
export WEBHOOK_API_KEY="$(openssl rand -base64 32)"

# In production, use environment variables
WEBHOOK_API_KEY=your-production-key
```

### 2. Rate Limiting

- Monitor rate limit headers in responses
- Implement exponential backoff for retries
- Use different API keys for different services

### 3. Input Validation

```python
# Always validate user inputs
def validate_user_id(user_id: str) -> bool:
    return user_id.isalnum() and len(user_id) <= 50

def validate_message(message: str) -> bool:
    return len(message) <= 10000 and message.strip()
```

## 🐛 Troubleshooting

### Common Issues

**1. Authentication Errors (401)**
```json
{"error": "Authentication required"}
```
- Check API key is set correctly
- Verify header format: `Authorization: Bearer YOUR_KEY`

**2. Rate Limit Exceeded (429)**
```json
{"error": "Rate limit exceeded", "retry_after": 300}
```
- Wait before retrying
- Implement exponential backoff
- Consider batching requests

**3. User Not Found (404)**
```json
{"error": "User user123 not found"}
```
- User is created automatically on first interaction
- Check user_id format and spelling

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

sdk = AIUserLearningSDK("http://localhost:5000")
sdk.health_check()  # Check connectivity
```

### Health Check

```bash
curl -X GET http://localhost:5000/health
```

## 📊 Monitoring & Analytics

### Track SDK Usage

```python
from sdk import AIUserLearningSDK
import time

class MonitoredSDK(AIUserLearningSDK):
    def log_message(self, chat_message):
        start_time = time.time()
        try:
            result = super().log_message(chat_message)
            duration = time.time() - start_time
            print(f"Message logged in {duration:.2f}s")
            return result
        except Exception as e:
            print(f"Error logging message: {e}")
            raise
```

### System Health Monitoring

```python
def monitor_system_health():
    sdk = AIUserLearningSDK()
    
    if not sdk.health_check():
        print("❌ Learning system is down!")
        # Send alert, use fallback, etc.
    else:
        print("✅ Learning system is healthy")
```

## 🚀 Deployment Tips

### Production Configuration

```python
# Use production settings
sdk = AIUserLearningSDK(
    base_url="https://your-learning-api.com",
    api_key=os.getenv("LEARNING_API_KEY")
)
```

### Docker Integration

```dockerfile
FROM python:3.9-slim
COPY sdk/ /app/sdk/
COPY your_chatbot.py /app/
RUN pip install requests
CMD ["python", "/app/your_chatbot.py"]
```

### Environment Variables

```bash
# Required
LEARNING_SYSTEM_URL=https://your-api.com
WEBHOOK_API_KEY=your-secure-key

# Optional
LEARNING_TIMEOUT=30
LEARNING_RETRY_COUNT=3
```

This documentation provides everything needed to integrate any chatbot with the AI User Learning System! 🎉