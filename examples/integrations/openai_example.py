"""
OpenAI Integration Example

This example shows how to integrate OpenAI's API with the AI User Learning System
to create a chatbot that learns and remembers user preferences.

Requirements:
    pip install openai

Usage:
    export OPENAI_API_KEY="your-api-key"
    python openai_example.py
"""

import sys
import os
import json
from typing import List, Dict

# Add the parent directory to the path to import the SDK
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sdk import AIUserLearningSDK, ChatMessage

try:
    import openai
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)


class PersonalizedOpenAIChat:
    def __init__(self, learning_url="http://localhost:5000", model="gpt-3.5-turbo"):
        """Initialize the personalized OpenAI chat"""
        self.sdk = AIUserLearningSDK(learning_url)
        self.model = model
        self.conversation_history = {}
        
        # Set up OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Please set OPENAI_API_KEY environment variable")
        
        openai.api_key = api_key
    
    def chat(self, user_id: str, message: str) -> str:
        """
        Chat with OpenAI using personalized context
        
        Args:
            user_id: User identifier
            message: User message
            
        Returns:
            Bot response
        """
        # Get or create conversation history for user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Get user context for personalization
        context = self.sdk.get_personalization_context(user_id)
        
        # Prepare system message with user context
        system_message = {
            "role": "system",
            "content": (
                "You are a helpful AI assistant that remembers user preferences "
                "and personalizes responses. Use the provided user context to "
                "make your responses more relevant and personalized.\n\n"
                f"User Context:\n{context}" if context else 
                "You are a helpful AI assistant. This is a new user with no prior context."
            )
        }
        
        # Prepare messages
        messages = [system_message] + self.conversation_history[user_id] + [
            {"role": "user", "content": message}
        ]
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=512
            )
            
            # Extract response
            bot_response = response.choices[0].message.content
            
            # Log the interaction in the learning system
            chat_msg = ChatMessage(
                user_id=user_id,
                message=message,
                response=bot_response,
                metadata={
                    'source': 'openai',
                    'model': self.model,
                    'context_used': bool(context)
                }
            )
            
            try:
                self.sdk.log_message(chat_msg)
            except Exception as e:
                print(f"Warning: Failed to log interaction: {e}")
            
            # Update conversation history
            self.conversation_history[user_id].extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": bot_response}
            ])
            
            # Keep conversation history manageable
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            return bot_response
            
        except Exception as e:
            print(f"Error communicating with OpenAI: {e}")
            return f"Sorry, I encountered an error: {e}"
    
    def get_user_summary(self, user_id: str) -> str:
        """Get a summary of what the system has learned about the user"""
        try:
            insights = self.sdk.get_user_insights(user_id, limit=10)
            
            if not insights.get('facts'):
                return f"No information learned about user {user_id} yet."
            
            summary = [f"User Profile for {user_id}:"]
            
            # Group facts by category
            categories = {}
            for fact in insights['facts']:
                cat = fact['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(fact)
            
            for category, facts in categories.items():
                summary.append(f"\n{category.title()}:")
                for fact in facts:
                    confidence = fact['confidence']
                    summary.append(f"  - {fact['value']} (confidence: {confidence})")
            
            return "\n".join(summary)
        
        except Exception as e:
            return f"Error retrieving user insights: {e}"


def interactive_chat():
    """Run an interactive chat session"""
    
    print("🚀 Initializing OpenAI + AI Learning integration...")
    
    # Check if learning system is available
    sdk = AIUserLearningSDK()
    if not sdk.health_check():
        print("⚠️ Warning: AI User Learning System not available at http://localhost:5000")
        print("Please start the learning system first with: python app.py")
        return
    
    try:
        chat_system = PersonalizedOpenAIChat()
    except ValueError as e:
        print(f"❌ {e}")
        return
    except Exception as e:
        print(f"❌ Error initializing OpenAI: {e}")
        return
    
    print("\n🤖 AI Learning Chatbot with OpenAI")
    print("Type 'quit' to exit, '/insights' to see user insights, '/summary' for user summary")
    print("=" * 60)
    
    user_id = input("Enter your user ID (or press Enter for 'demo_user'): ").strip()
    if not user_id:
        user_id = "demo_user"
    
    print(f"\nChatting as user: {user_id}")
    print("Getting your profile...")
    
    # Show initial user insights
    summary = chat_system.get_user_summary(user_id)
    print(f"\n📊 {summary}")
    print("\n" + "=" * 60)
    
    while True:
        try:
            message = input(f"\n{user_id}: ").strip()
            
            if message.lower() == 'quit':
                break
            elif message.lower() == '/insights':
                insights = chat_system.sdk.get_user_insights(user_id)
                print(json.dumps(insights, indent=2))
                continue
            elif message.lower() == '/summary':
                summary = chat_system.get_user_summary(user_id)
                print(f"\n📊 {summary}")
                continue
            elif not message:
                continue
            
            print("🤔 Thinking...")
            
            # Get personalized response
            response = chat_system.chat(user_id, message)
            
            print(f"\n🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    interactive_chat()