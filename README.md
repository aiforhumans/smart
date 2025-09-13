# 🧠 AI User Learning System

> **Build chatbots that truly understand and remember their users**

An intelligent system that learns from conversations, extracts user insights, and enables personalized AI interactions. Perfect for creating chatbots that get smarter with every conversation.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ What Makes This Special

- **🎯 Zero-Config Learning**: Drop-in solution that starts learning immediately
- **🔗 Universal Integration**: Works with any chatbot platform (Gradio, OpenAI, LM Studio, etc.)
- **📊 Real-time Insights**: Live user profiling and personalization suggestions
- **🛡️ Privacy-First**: GDPR compliant with configurable data retention
- **🚀 Production-Ready**: Webhook APIs, authentication, rate limiting, and monitoring

## 🚀 Quick Start

### 1-Command Setup
```bash
# Clone and start
git clone https://github.com/aiforhumans/smart.git
cd smart
python start.py
```

The system will auto-install dependencies and start on `http://localhost:5000`

### Instant Integration
```python
from sdk import AIUserLearningSDK, ChatMessage

# Connect to your learning system
sdk = AIUserLearningSDK("http://localhost:5000")

# Log any conversation
result = sdk.log_message(ChatMessage(
    user_id="user123",
    message="I love hiking and playing guitar",
    response="That's great! Tell me more about your interests."
))
print(f"✅ Learned {result['learned_facts_count']} new facts")

# Get personalized context for next conversation
context = sdk.get_personalization_context("user123")
print(f"🧠 What I know: {context}")
```

## 🎯 Core Features

### 🤖 Intelligent Learning Engine
- **Fact Extraction**: Automatically identifies user preferences, skills, and interests
- **Sentiment Analysis**: Understands user emotional patterns and communication style
- **Behavioral Modeling**: Learns from interaction patterns and timing
- **Context Building**: Creates rich user profiles for personalization

### 🔌 Universal Chatbot Integration
- **Webhook APIs**: RESTful endpoints for any platform
- **Python SDK**: Pre-built helpers for popular chatbot frameworks
- **Real-time Streaming**: Server-Sent Events for live learning updates
- **Bulk Operations**: Efficient processing of conversation histories

### 📊 Analytics & Insights
- **User Profiles**: Comprehensive personality and preference mapping
- **Interaction Analytics**: Conversation patterns and engagement metrics
- **Learning Progress**: Track how well the AI understands each user
- **Personalization Suggestions**: AI-generated conversation starters

## 🛠️ Installation & Setup

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB for basic installation
- **OS**: Windows, macOS, Linux

### Manual Installation
```bash
# 1. Clone repository
git clone https://github.com/aiforhumans/smart.git
cd smart

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python -c "from database import db_manager; db_manager.create_tables()"

# 5. Start the system
python app.py
```

### Docker Installation
```bash
# Coming soon - Docker support planned for v2.0
```

## 🎮 Usage Examples

### Basic Chatbot Integration
```python
from sdk import AIUserLearningSDK, ChatMessage

sdk = AIUserLearningSDK("http://localhost:5000")

# Simple conversation logging
sdk.log_message(ChatMessage(
    user_id="user123",
    message="I work as a software engineer",
    response="Interesting! What programming languages do you use?"
))

# Get insights for personalization
insights = sdk.get_user_insights("user123", limit=5)
for fact in insights['facts']:
    print(f"• {fact['value']} (confidence: {fact['confidence']})")
```

### Advanced Learning Patterns
```python
# Bulk import conversation history
conversations = [
    {"user_id": "user123", "message": "I love Python", "response": "Great choice!"},
    {"user_id": "user123", "message": "I work remotely", "response": "How do you like it?"}
]

result = sdk.bulk_upload_interactions("user123", conversations)
print(f"Processed {result['interactions_created']} conversations")

# Real-time learning stream
for update in sdk.stream_learning_updates("user123"):
    print(f"New insight: {update['fact_learned']}")
```

### Gradio Chatbot Example
```python
import gradio as gr
from sdk import AIUserLearningSDK, GradioIntegration

# Initialize with learning
learning_sdk = AIUserLearningSDK("http://localhost:5000")
gradio_helper = GradioIntegration(learning_sdk)

def chat_with_learning(message, history, user_id):
    # Your AI response logic here
    response = "Your AI response"
    
    # Log and learn from interaction
    gradio_helper.log_interaction(user_id, message, response)
    
    # Get personalized context for next response
    context = gradio_helper.get_user_context(user_id)
    
    return response

# Launch chatbot with learning
iface = gr.ChatInterface(chat_with_learning)
iface.launch()
```

## 🏗️ Architecture

### System Components
```
┌─────────────────┬─────────────────┬─────────────────┐
│   Chatbot Layer │  Learning APIs  │  Data Storage   │
├─────────────────┼─────────────────┼─────────────────┤
│ • Gradio        │ • Webhook APIs  │ • SQLite/       │
│ • OpenAI        │ • Python SDK    │   PostgreSQL    │
│ • LM Studio     │ • REST APIs     │ • User Profiles │
│ • Custom Bots   │ • Streaming     │ • Interactions  │
└─────────────────┴─────────────────┴─────────────────┘
```

### Data Flow
1. **Conversation** → Chatbot sends interaction via webhook
2. **Analysis** → AI engine extracts facts and insights  
3. **Storage** → Facts stored with confidence levels
4. **Retrieval** → Context provided for next conversation

### Key Directories
```
smart/
├── 📁 ai/              # Learning engine and NLP processing
├── 📁 database/        # Data persistence and repositories  
├── 📁 models/          # SQLAlchemy models and schemas
├── 📁 sdk/             # Python client library
├── 📁 routes/          # Flask API routes (planned)
├── 📁 utils/           # Common utilities and helpers
├── 📁 examples/        # Usage examples and integrations
├── 📁 docs/            # Comprehensive documentation
└── 📁 templates/       # Web dashboard interface
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///user_learning.db
DATABASE_ECHO=false

# Security
SECRET_KEY=your-secret-key-here
WEBHOOK_API_KEY=your-webhook-api-key

# Features  
ENABLE_REAL_TIME_LEARNING=true
MIN_INTERACTIONS_FOR_LEARNING=3
LEARNING_CONFIDENCE_THRESHOLD=0.7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Production Checklist
- [ ] Set secure `SECRET_KEY` and `WEBHOOK_API_KEY`
- [ ] Configure PostgreSQL database URL
- [ ] Enable HTTPS/TLS encryption
- [ ] Set up monitoring and logging
- [ ] Configure backup procedures
- [ ] Review privacy settings

## 🧪 Testing & Development

### Run Test Suite
```bash
# Quick integration test
python test_webhook.py

# Full demo with examples
python examples/webhook_demo.py

# Platform-specific tests
python examples/integrations/gradio_example.py     # Gradio
python examples/integrations/openai_example.py     # OpenAI
python examples/integrations/lm_studio_example.py  # LM Studio

# Windows batch test
test.bat
```

### Development Workflow
```bash
# Install development dependencies
pip install -r requirements-integrations.txt

# Start with hot reload
python app.py

# Monitor database in real-time  
python -c "from database import db_manager; print(db_manager.health_check())"

# Reset database (development only)
python -c "from database import db_manager; db_manager.drop_tables(); db_manager.create_tables()"
```

## � Documentation

- **[Webhook & SDK Guide](docs/WEBHOOK_SDK_GUIDE.md)** - Complete integration documentation
- **[API Reference](http://localhost:5000/docs)** - Interactive API documentation  
- **[Copilot Instructions](.github/copilot-instructions.md)** - AI coding agent guidelines
- **[Examples README](examples/README.md)** - Usage examples and patterns

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/aiforhumans/smart.git
cd smart
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-integrations.txt
```

### Submit Changes
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)  
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask & SQLAlchemy** - Robust web framework and ORM
- **Natural Language Processing** - Lightweight NLP without heavy dependencies
- **Privacy by Design** - GDPR-compliant architecture from day one
- **Developer Experience** - Focus on simplicity and powerful APIs

---

## 🚀 Ready to Build Smarter Chatbots?

**Quick Links:**
- 🏃‍♂️ [Quick Start](#-quick-start) - Get running in 60 seconds
- 🔌 [Integration Examples](examples/) - Real chatbot implementations  
- 📖 [Full Documentation](docs/) - Complete guides and references
- 💬 [Community Support](https://github.com/aiforhumans/smart/discussions) - Get help and share ideas

**Start building chatbots that remember and understand your users today!**
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   Open your browser and navigate to `http://localhost:5000`

## 🎯 Quick Start

### Creating Your First User

1. Open the web dashboard at `http://localhost:5000`
2. Use the "User Management" section to create a new user
3. Start recording interactions in the "Record Interaction" section
4. Watch the AI learn about the user in real-time!

### API Usage

The system provides a comprehensive REST API:

```python
import requests

# Create a user
response = requests.post('http://localhost:5000/api/users', json={
    'username': 'john_doe',
    'email': 'john@example.com'
})

user_id = response.json()['user']['id']

# Record an interaction
requests.post(f'http://localhost:5000/api/users/{user_id}/interactions', json={
    'content': 'I love playing guitar and listening to jazz music!',
    'interaction_type': 'message'
})

# Trigger learning
requests.post(f'http://localhost:5000/api/users/{user_id}/learn')

# Get learned facts
facts = requests.get(f'http://localhost:5000/api/users/{user_id}/facts')
print(facts.json())
```

## 📚 API Reference

### User Management
- `POST /api/users` - Create a new user
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Interactions
- `POST /api/users/{id}/interactions` - Record interaction
- `GET /api/users/{id}/interactions` - Get user interactions
- `DELETE /api/interactions/{id}` - Delete interaction

### Learning & Facts
- `POST /api/users/{id}/learn` - Trigger AI learning
- `GET /api/users/{id}/facts` - Get learned facts
- `GET /api/users/{id}/insights` - Get AI insights
- `GET /api/users/{id}/analytics` - Get analytics data

### System
- `GET /api/health` - System health check
- `GET /api/stats` - System statistics

## 🧠 How the AI Learning Works

### 1. **Text Analysis**
- **Sentiment Analysis**: Determines emotional tone (-1 to +1 scale)
- **Topic Extraction**: Identifies key subjects and interests
- **Intent Classification**: Categorizes message types (questions, preferences, etc.)

### 2. **Pattern Recognition**
- **Time Patterns**: When users are most active
- **Communication Style**: Formal vs casual, brief vs detailed
- **Behavioral Trends**: Sentiment changes over time

### 3. **Fact Generation**
- **Preferences**: Likes, dislikes, interests
- **Behavioral Insights**: Communication patterns, learning style
- **Temporal Patterns**: Activity schedules, interaction frequency

### 4. **Confidence Scoring**
- **High Confidence**: 5+ supporting interactions
- **Medium Confidence**: 3-4 supporting interactions  
- **Low Confidence**: 1-2 supporting interactions

## 📊 Web Dashboard Features

### User Management
- Create, edit, and delete users
- View user profiles and statistics
- Manage user privacy settings

### Interaction Recording
- Real-time message input
- Automatic AI processing
- Immediate feedback and analysis

### Learning Visualization
- Live fact updates
- Confidence level indicators
- Evidence tracking
- Category filtering

### Analytics
- User engagement metrics
- Learning progress tracking
- System performance monitoring
- Export capabilities

## 🔒 Privacy & Security

### Data Protection
- **Encryption at Rest**: User data encrypted using Fernet symmetric encryption
- **Secure Authentication**: JWT tokens with bcrypt password hashing
- **Privacy Controls**: Users can control what data is learned and stored
- **GDPR Compliance**: Right to erasure, data portability, and consent management

### Configuration
Create a `.env` file for sensitive settings:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///user_learning.db
ENCRYPTION_KEY=your-encryption-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

## 📁 Project Structure

```
smart/
├── ai/                     # AI learning engine
│   └── learning_engine.py  # NLP and pattern analysis
├── database/               # Database layer
│   └── __init__.py         # Repository patterns and utilities
├── models/                 # Data models
│   └── __init__.py         # SQLAlchemy models
├── security/               # Security utilities
│   └── __init__.py         # Encryption and authentication
├── templates/              # Web interface
│   ├── index.html          # Main dashboard
│   └── user_dashboard.html # User-specific dashboard
├── examples/               # Usage examples
│   ├── basic_usage.py      # Basic API examples
│   ├── advanced_demo.py    # Advanced features demo
│   └── quick_start.py      # Quick start guide
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Flask and SQLAlchemy
- Inspired by modern AI conversation systems
- Designed for privacy-first user learning

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/aiforhumans/smart/issues)
- **Documentation**: [Wiki](https://github.com/aiforhumans/smart/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/aiforhumans/smart/discussions)

---

**Built with ❤️ for better AI-human interactions**