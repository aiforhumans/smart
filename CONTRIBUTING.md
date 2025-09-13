# Contributing to AI User Learning System

Thank you for your interest in contributing to the AI User Learning System! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use clear, descriptive titles** for your issues
3. **Provide detailed information**:
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. **Check existing feature requests** in Issues
2. **Describe the use case** and why it would be valuable
3. **Provide implementation details** if you have ideas
4. **Consider the scope** - does it fit with the project goals?

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow the coding standards** outlined below
3. **Write comprehensive tests** for new functionality
4. **Update documentation** as needed
5. **Ensure all tests pass** before submitting

## 🔧 Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Local Development

1. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/smart.git
   cd smart
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Run tests**:
   ```bash
   python -m pytest tests/
   ```

5. **Start development server**:
   ```bash
   python app.py
   ```

## 📝 Coding Standards

### Python Code Style

- **Follow PEP 8** for Python code formatting
- **Use meaningful variable and function names**
- **Add type hints** where appropriate
- **Write docstrings** for all public functions and classes
- **Keep functions focused** and under 50 lines when possible

### Example:

```python
def analyze_user_sentiment(interaction_text: str) -> float:
    """
    Analyze the sentiment of user interaction text.
    
    Args:
        interaction_text: The text content to analyze
        
    Returns:
        float: Sentiment score between -1.0 (negative) and 1.0 (positive)
        
    Raises:
        ValueError: If interaction_text is empty or None
    """
    if not interaction_text:
        raise ValueError("Interaction text cannot be empty")
    
    # Implementation here
    return sentiment_score
```

### Documentation

- **Update README.md** for significant changes
- **Add inline comments** for complex logic
- **Document API endpoints** with examples
- **Include usage examples** for new features

### Testing

- **Write unit tests** for all new functions
- **Include integration tests** for API endpoints
- **Test edge cases** and error conditions
- **Maintain test coverage** above 80%

### Example Test:

```python
def test_analyze_user_sentiment():
    """Test sentiment analysis functionality."""
    # Positive sentiment
    assert analyze_user_sentiment("I love this!") > 0
    
    # Negative sentiment
    assert analyze_user_sentiment("This is terrible") < 0
    
    # Error handling
    with pytest.raises(ValueError):
        analyze_user_sentiment("")
```

## 🏗️ Project Structure

Understanding the codebase structure helps with contributions:

```
smart/
├── ai/                     # AI learning components
│   ├── __init__.py
│   └── learning_engine.py  # Core learning algorithms
├── database/               # Database layer
│   ├── __init__.py         # Repository patterns
│   └── init_db.py         # Database initialization
├── models/                 # Data models
│   └── __init__.py         # SQLAlchemy models
├── security/               # Security utilities
│   └── __init__.py         # Authentication & encryption
├── templates/              # Web interface templates
│   ├── index.html
│   └── user_dashboard.html
├── examples/               # Usage examples
├── tests/                  # Test suite
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
└── requirements.txt        # Dependencies
```

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_learning_engine.py

# Run with verbose output
python -m pytest -v
```

### Test Categories

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test REST endpoint functionality
4. **End-to-End Tests**: Test complete user workflows

### Writing Good Tests

- **Use descriptive test names** that explain what is being tested
- **Follow AAA pattern**: Arrange, Act, Assert
- **Test one thing at a time**
- **Include both positive and negative test cases**
- **Mock external dependencies**

## 🚀 Deployment & Release

### Version Management

- We use **semantic versioning** (MAJOR.MINOR.PATCH)
- Version bumps require approval from maintainers
- Each release includes updated CHANGELOG.md

### Release Process

1. **Feature freeze** for the release
2. **Comprehensive testing** of the release candidate
3. **Documentation updates**
4. **Version tagging** and release notes

## 🔒 Security Considerations

### Reporting Security Issues

- **Do not** report security vulnerabilities in public issues
- **Email** maintainers directly for security concerns
- **Provide detailed information** about the vulnerability
- **Allow reasonable time** for fixes before disclosure

### Security Guidelines

- **Never commit** sensitive data (keys, passwords, etc.)
- **Use environment variables** for configuration
- **Validate all user inputs**
- **Follow OWASP guidelines** for web security
- **Keep dependencies updated**

## 📋 Issue Labels

We use the following labels to categorize issues:

- **bug**: Something isn't working correctly
- **enhancement**: New feature or improvement
- **documentation**: Documentation improvements
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention needed
- **priority-high**: Critical issues
- **priority-low**: Nice to have improvements

## 🎯 Development Workflow

### Branch Naming

- **feature/**: New features (`feature/user-preferences`)
- **bugfix/**: Bug fixes (`bugfix/sentiment-analysis`)
- **docs/**: Documentation (`docs/api-reference`)
- **refactor/**: Code refactoring (`refactor/database-layer`)

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(learning): add sentiment analysis for user interactions
fix(api): resolve user creation validation error
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create feature branch** from main
2. **Make changes** and commit regularly
3. **Write/update tests** for your changes
4. **Update documentation** as needed
5. **Run full test suite** and ensure it passes
6. **Create pull request** with detailed description
7. **Respond to review feedback**
8. **Merge** after approval (squash merge preferred)

## 🎉 Recognition

Contributors will be:

- **Listed** in the CONTRIBUTORS.md file
- **Mentioned** in release notes for significant contributions
- **Credited** in documentation where appropriate

## ❓ Questions?

- **GitHub Discussions**: For general questions and ideas
- **GitHub Issues**: For specific bugs or feature requests
- **Documentation**: Check the Wiki for detailed guides

Thank you for contributing to the AI User Learning System! 🚀