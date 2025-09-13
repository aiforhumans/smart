"""
Basic API usage examples for the AI User Learning System
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:5000'
API_BASE = f'{BASE_URL}/api'

class APIClient:
    """Simple API client for the AI Learning System"""
    
    def __init__(self, base_url=API_BASE):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def create_user(self, username, email=None, **kwargs):
        """Create a new user"""
        data = {'username': username, 'email': email, **kwargs}
        response = self.session.post(f'{self.base_url}/users', json=data)
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id):
        """Get user information"""
        response = self.session.get(f'{self.base_url}/users/{user_id}')
        response.raise_for_status()
        return response.json()
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile"""
        response = self.session.put(f'{self.base_url}/users/{user_id}/profile', json=profile_data)
        response.raise_for_status()
        return response.json()
    
    def record_interaction(self, user_id, content, interaction_type='message', **kwargs):
        """Record a user interaction"""
        data = {
            'type': interaction_type,
            'content': content,
            'source': 'api_client',
            **kwargs
        }
        response = self.session.post(f'{self.base_url}/users/{user_id}/interactions', json=data)
        response.raise_for_status()
        return response.json()
    
    def get_interactions(self, user_id, limit=50, offset=0):
        """Get user interactions"""
        params = {'limit': limit, 'offset': offset}
        response = self.session.get(f'{self.base_url}/users/{user_id}/interactions', params=params)
        response.raise_for_status()
        return response.json()
    
    def trigger_learning(self, user_id):
        """Trigger learning process for a user"""
        response = self.session.post(f'{self.base_url}/users/{user_id}/learn')
        response.raise_for_status()
        return response.json()
    
    def get_learned_facts(self, user_id, category=None):
        """Get learned facts about a user"""
        params = {'category': category} if category else {}
        response = self.session.get(f'{self.base_url}/users/{user_id}/facts', params=params)
        response.raise_for_status()
        return response.json()
    
    def confirm_fact(self, user_id, fact_id, confirmed=True):
        """Confirm or reject a learned fact"""
        data = {'confirmed': confirmed}
        response = self.session.post(f'{self.base_url}/users/{user_id}/facts/{fact_id}/confirm', json=data)
        response.raise_for_status()
        return response.json()
    
    def get_analytics(self, user_id):
        """Get user analytics"""
        response = self.session.get(f'{self.base_url}/users/{user_id}/analytics')
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        """Check system health"""
        response = self.session.get(f'{self.base_url.replace("/api", "")}/health')
        response.raise_for_status()
        return response.json()


def example_1_basic_workflow():
    """Example 1: Basic workflow - create user, interact, learn"""
    print("🚀 Example 1: Basic Workflow")
    print("=" * 40)
    
    client = APIClient()
    
    # Check system health
    health = client.health_check()
    print(f"System Status: {health['status']}")
    
    # Create a user
    print("\n1. Creating user...")
    user = client.create_user(
        username=f"test_user_{int(time.time())}",
        email="test@example.com",
        data_sharing_consent=True,
        learning_enabled=True
    )
    user_id = user['user_id']
    print(f"   Created user: {user['username']} (ID: {user_id})")
    
    # Record some interactions
    print("\n2. Recording interactions...")
    interactions = [
        "Hi there! I'm new here and excited to learn.",
        "I really enjoy programming in Python and JavaScript.",
        "I prefer detailed explanations when learning new concepts.",
        "Thanks for helping me understand this better!",
        "I'm working on a machine learning project right now."
    ]
    
    for i, content in enumerate(interactions, 1):
        result = client.record_interaction(user_id, content)
        print(f"   {i}. Recorded: '{content[:50]}...'")
        time.sleep(0.5)  # Small delay between interactions
    
    # Trigger learning
    print("\n3. Triggering AI learning...")
    learning_result = client.trigger_learning(user_id)
    print(f"   Processed: {learning_result['processed_interactions']} interactions")
    print(f"   Learned: {learning_result['new_facts']} new facts")
    print(f"   Time: {learning_result['processing_time_ms']}ms")
    
    # Get learned facts
    print("\n4. Retrieved learned facts:")
    facts = client.get_learned_facts(user_id)
    for fact in facts['facts'][:5]:  # Show first 5 facts
        print(f"   • {fact['category']}: {fact['fact_value']} (Confidence: {fact['confidence_level']})")
    
    return user_id


def example_2_profile_management():
    """Example 2: Profile management and preferences"""
    print("\n🔧 Example 2: Profile Management")
    print("=" * 40)
    
    client = APIClient()
    
    # Create user
    user = client.create_user(
        username=f"profile_user_{int(time.time())}",
        email="profile@example.com"
    )
    user_id = user['user_id']
    print(f"Created user: {user['username']}")
    
    # Update profile
    print("\n1. Updating user profile...")
    profile_data = {
        'preferred_language': 'en',
        'communication_style': 'professional',
        'technical_level': 'advanced',
        'response_length_preference': 'detailed',
        'interests': ['artificial intelligence', 'data science', 'web development'],
        'hobbies': ['reading', 'coding', 'hiking']
    }
    
    client.update_user_profile(user_id, profile_data)
    print("   Profile updated successfully")
    
    # Get updated user info
    print("\n2. Retrieving updated user info...")
    user_info = client.get_user(user_id)
    profile = user_info.get('profile', {})
    print(f"   Language: {profile.get('preferred_language')}")
    print(f"   Style: {profile.get('communication_style')}")
    print(f"   Level: {profile.get('technical_level')}")
    print(f"   Interests: {', '.join(profile.get('interests', []))}")
    
    return user_id


def example_3_interaction_analysis():
    """Example 3: Different types of interactions and analysis"""
    print("\n📊 Example 3: Interaction Analysis")
    print("=" * 40)
    
    client = APIClient()
    
    # Create user
    user = client.create_user(username=f"analysis_user_{int(time.time())}")
    user_id = user['user_id']
    print(f"Created user for analysis")
    
    # Record different types of interactions
    interaction_scenarios = [
        # Preferences
        ('preference', "I love learning about machine learning algorithms"),
        ('preference', "I prefer visual explanations over text-heavy content"),
        ('preference', "I don't like overly technical jargon when starting to learn something"),
        
        # Feedback
        ('feedback', "That explanation was perfect - just the right level of detail!"),
        ('feedback', "Could you provide more examples next time?"),
        ('feedback', "I found that too advanced, please simplify"),
        
        # Behavior
        ('behavior', "I usually study best in the morning"),
        ('behavior', "I like to take breaks every 30 minutes when learning"),
        ('behavior', "I prefer interactive content over passive reading"),
        
        # Messages
        ('message', "How does gradient descent work in neural networks?"),
        ('message', "Can you explain the difference between supervised and unsupervised learning?"),
        ('message', "Thank you for the detailed explanation!")
    ]
    
    print(f"\n1. Recording {len(interaction_scenarios)} different interactions...")
    for interaction_type, content in interaction_scenarios:
        client.record_interaction(user_id, content, interaction_type)
        print(f"   {interaction_type}: '{content[:50]}...'")
        time.sleep(0.3)
    
    # Trigger learning
    print("\n2. Processing interactions with AI...")
    learning_result = client.trigger_learning(user_id)
    print(f"   Learning completed: {learning_result['new_facts']} facts learned")
    
    # Analyze learned facts by category
    print("\n3. Analyzing learned facts by category...")
    categories = ['preferences', 'behavior', 'communication', 'interests']
    
    for category in categories:
        facts = client.get_learned_facts(user_id, category)
        if facts['facts']:
            print(f"\n   {category.upper()}:")
            for fact in facts['facts']:
                print(f"     • {fact['fact_key']}: {fact['fact_value']}")
        else:
            print(f"\n   {category.upper()}: No facts learned yet")
    
    return user_id


def example_4_fact_confirmation():
    """Example 4: Fact confirmation and user feedback"""
    print("\n✅ Example 4: Fact Confirmation")
    print("=" * 40)
    
    client = APIClient()
    
    # Use user from previous example or create new one
    user = client.create_user(username=f"confirm_user_{int(time.time())}")
    user_id = user['user_id']
    
    # Record some interactions
    interactions = [
        "I absolutely love working with Python for data analysis",
        "I'm passionate about renewable energy and sustainability",
        "I prefer working alone rather than in teams",
        "I find mathematics fascinating, especially statistics"
    ]
    
    print("1. Recording interactions...")
    for content in interactions:
        client.record_interaction(user_id, content, 'preference')
        print(f"   Recorded: '{content[:50]}...'")
    
    # Trigger learning
    client.trigger_learning(user_id)
    
    # Get facts and demonstrate confirmation
    print("\n2. Reviewing and confirming learned facts...")
    facts = client.get_learned_facts(user_id)
    
    for i, fact in enumerate(facts['facts'][:3]):  # Confirm first 3 facts
        print(f"\n   Fact {i+1}: {fact['fact_value']}")
        print(f"   Confidence: {fact['confidence_level']}")
        
        # Simulate user confirmation (in real app, this would be user input)
        confirmed = i < 2  # Confirm first 2, reject the 3rd
        result = client.confirm_fact(user_id, fact['id'], confirmed)
        
        status = "✅ CONFIRMED" if confirmed else "❌ REJECTED"
        print(f"   User feedback: {status}")
    
    return user_id


def example_5_analytics_dashboard():
    """Example 5: Analytics and insights"""
    print("\n📈 Example 5: Analytics Dashboard")
    print("=" * 40)
    
    client = APIClient()
    
    # Create user with substantial interaction history
    user = client.create_user(username=f"analytics_user_{int(time.time())}")
    user_id = user['user_id']
    
    # Simulate a week of interactions
    daily_interactions = [
        # Day 1
        ["Good morning! Ready to learn something new today.", "I'm interested in machine learning basics."],
        # Day 2
        ["Can you explain neural networks in simple terms?", "That was helpful, thank you!"],
        # Day 3
        ["I prefer step-by-step explanations.", "Visual aids really help me understand better."],
        # Day 4
        ["I'm working on a Python project now.", "Could you recommend some good resources?"],
        # Day 5
        ["I love how patient you are with my questions.", "This learning approach really works for me."]
    ]
    
    print("1. Simulating interaction history...")
    for day, interactions in enumerate(daily_interactions, 1):
        print(f"   Day {day}: {len(interactions)} interactions")
        for content in interactions:
            client.record_interaction(user_id, content)
        time.sleep(0.5)
    
    # Trigger learning
    print("\n2. Processing all interactions...")
    client.trigger_learning(user_id)
    
    # Get analytics
    print("\n3. Generating analytics report...")
    analytics = client.get_analytics(user_id)
    
    print(f"\n📊 USER ANALYTICS REPORT")
    print(f"   Total Interactions: {analytics['user_summary']['total_interactions']}")
    print(f"   Facts Learned: {analytics['user_summary']['total_facts_learned']}")
    print(f"   Average Sentiment: {analytics['interaction_stats']['average_sentiment']:.2f}")
    print(f"   Member Since: {analytics['user_summary']['member_since'][:10]}")
    
    print(f"\n🧠 LEARNING PROGRESS:")
    for category, count in analytics['learning_progress']['facts_by_category'].items():
        print(f"   {category.title()}: {count} facts")
    
    return user_id


def run_all_examples():
    """Run all API examples"""
    print("🔥 AI User Learning System - API Examples")
    print("=" * 60)
    print("This demonstrates the complete API functionality\n")
    
    try:
        # Run all examples
        user1 = example_1_basic_workflow()
        user2 = example_2_profile_management()
        user3 = example_3_interaction_analysis()
        user4 = example_4_fact_confirmation()
        user5 = example_5_analytics_dashboard()
        
        print(f"\n🎉 All Examples Completed Successfully!")
        print(f"=" * 60)
        print(f"Created {5} demo users with various interaction patterns")
        print(f"Demonstrated: User creation, interactions, learning, facts, analytics")
        print(f"Check the web interface at: http://localhost:5000")
        
        return [user1, user2, user3, user4, user5]
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the server is running: python app.py")
        return []
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        return []


if __name__ == "__main__":
    run_all_examples()