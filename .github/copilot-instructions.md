# AI User Learning System - Copilot Instructions

## Architecture Overview

This is a **Flask-based AI User Learning System** that processes chatbot conversations to extract and store user insights. The system uses a **Repository pattern** with SQLAlchemy ORM and provides both REST APIs and webhook endpoints for chatbot integration.

### Core Components
- **`app.py`**: Main Flask application with webhook endpoints (`/webhook/chat/*`) and REST APIs (`/api/*`)
- **`ai/learning_engine.py`**: NLP processing engine that extracts facts from conversations (no heavy ML dependencies)
- **`database/__init__.py`**: Repository pattern implementation (UserRepository, InteractionRepository, LearnedFactRepository)
- **`models/__init__.py`**: SQLAlchemy models and enums (User, UserInteraction, LearnedFact, InteractionType, LearningConfidence)
- **`sdk/__init__.py`**: Python client library for chatbot integrations (400+ lines)

### Data Flow
1. Chatbots send interactions via webhook → 2. LearningEngine extracts facts → 3. Repositories persist to SQLite → 4. Insights available via API/SDK

## Development Workflows

### Quick Start Commands
```bash
python start.py              # Automated setup with dependency check
python app.py               # Start Flask server (port 5000)
python test_webhook.py      # Test webhook endpoints
python examples/webhook_demo.py  # Full integration demo
test.bat                    # Windows automated test suite
```

### Testing Integrations
```bash
# Test specific chatbot integrations
python examples/integrations/gradio_example.py    # Gradio UI (port 7860)
python examples/integrations/lm_studio_example.py # LM Studio integration
python examples/integrations/openai_example.py    # OpenAI integration
```

## Critical Patterns

### Enum Value Handling
**Always use `.value` when passing enums to database repositories:**
```python
# ✅ Correct
interaction_type=InteractionType.MESSAGE.value

# ❌ Wrong (causes SQLite binding errors)
interaction_type=InteractionType.MESSAGE
```

### Webhook Authentication
All webhook endpoints require authentication via decorator:
```python
@webhook_auth_required
@rate_limit(max_requests=100, window=300)
def webhook_chat_message():
```
Default API key: `dev-webhook-key-change-in-production`

### Repository Pattern Usage
```python
# Standard pattern for database operations
with db_manager.get_session() as session:
    user_repo = UserRepository(session)
    interaction_repo = InteractionRepository(session)
    
    user = user_repo.get_user_by_username(username)
    interaction = interaction_repo.create_interaction(
        user_id=user.id,
        content=message,
        interaction_type=InteractionType.MESSAGE.value  # Note .value
    )
    session.commit()
```

### SDK Integration Pattern
```python
from sdk import AIUserLearningSDK, ChatMessage

sdk = AIUserLearningSDK("http://localhost:5000")
result = sdk.log_message(ChatMessage(
    user_id="user123",
    message="user input",
    response="bot response"
))
```

## Service Boundaries

### Webhook Layer (`/webhook/chat/*`)
- Message logging, insights retrieval, bulk operations
- Server-Sent Events for real-time streaming (`/webhook/stream/*`)
- Authentication + rate limiting required

### REST API Layer (`/api/*`)
- User management, direct database access
- No authentication required (internal use)

### SDK Layer (`sdk/`)
- Client library with helper classes for major chatbot platforms
- Handles authentication, retries, and data formatting

## Integration Points

### External Dependencies
- **SQLite** (upgradeable to PostgreSQL via connection string)
- **Flask + SQLAlchemy** (no heavy ML frameworks)
- **Requests** for HTTP client functionality

### Chatbot Platform Support
- **Gradio**: `GradioIntegration` helper class with real-time learning
- **LM Studio**: Context injection via `LMStudioIntegration`
- **OpenAI**: Personalization with `OpenAIIntegration`

### Key Files for Integration
- `examples/integrations/` - Working examples for each platform
- `docs/WEBHOOK_SDK_GUIDE.md` - Complete API documentation
- `requirements-integrations.txt` - Optional chatbot-specific dependencies