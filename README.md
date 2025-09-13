# AI User Learning System

A comprehensive system that learns about users through their interactions and stores personalized insights. The AI analyzes conversations, extracts preferences, and builds detailed user profiles over time.

## 🚀 Features

- **🤖 AI-Powered Learning**: Automatic sentiment analysis, topic extraction, and pattern recognition
- **👤 User Management**: Complete user registration and profile management
- **💬 Interaction Recording**: Real-time conversation and interaction tracking
- **🧠 Smart Insights**: AI-generated insights about user behavior and preferences
- **📊 Analytics Dashboard**: Interactive web interface with real-time data visualization
- **🔒 Privacy & Security**: Data encryption, JWT authentication, and GDPR compliance
- **🔍 Pattern Analysis**: Behavioral pattern detection and time-based analysis
- **📈 Learning Analytics**: Track learning progress and system performance

## 🏗️ Architecture

- **Backend**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **AI Engine**: Custom NLP processing without heavy ML dependencies
- **Frontend**: Interactive HTML/CSS/JavaScript dashboard
- **Security**: bcrypt password hashing, JWT tokens, data encryption

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aiforhumans/smart.git
   cd smart
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
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