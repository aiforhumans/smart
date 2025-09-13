"""
LM Studio Integration Example

This example shows how to integrate LM Studio with the AI User Learning System
to create a personalized chatbot that remembers user preferences.

Requirements:
    - LM Studio running on http://localhost:1234
    - A model loaded in LM Studio
    - pip install openai requests

Usage:
    python lm_studio_example.py
"""

import sys
import os
import json
from typing import List, Dict

# Add the parent directory to the path to import the SDK
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sdk import AIUserLearningSDK, LMStudioIntegration, ChatMessage


class PersonalizedLMStudioChat:
    def __init__(self, learning_url="http://localhost:5000", lm_studio_url="http://localhost:1234/v1"):
        """Initialize the personalized LM Studio chat"""
        self.sdk = AIUserLearningSDK(learning_url)
        self.lm_integration = LMStudioIntegration(self.sdk, lm_studio_url)
        self.conversation_history = {}
    
    def chat(self, user_id: str, message: str, model: str = "llama-2-7b-chat") -> str:
        """
        Chat with LM Studio using personalized context
        
        Args:
            user_id: User identifier
            message: User message
            model: Model name in LM Studio
            
        Returns:
            Bot response
        """
        # Get or create conversation history for user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add user message to history
        self.conversation_history[user_id].append({
            "role": "user",
            "content": message
        })
        
        # Prepare messages for LM Studio
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant that remembers user preferences "
                    "and personalizes responses. Use the provided user context to "
                    "make your responses more relevant and personalized."
                )
            }
        ] + self.conversation_history[user_id]
        
        try:
            # Send enhanced request to LM Studio
            response = self.lm_integration.enhanced_chat_completion(
                messages=messages,
                user_id=user_id,
                model=model,
                temperature=0.7,
                max_tokens=512
            )
            
            # Extract response
            bot_response = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Add to conversation history
            if bot_response:
                self.conversation_history[user_id].append({
                    "role": "assistant",
                    "content": bot_response
                })
                
                # Keep conversation history manageable
                if len(self.conversation_history[user_id]) > 20:
                    self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            return bot_response
            
        except Exception as e:
            print(f"Error communicating with LM Studio: {e}")
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
            
            # Add analytics
            if insights.get('analytics'):
                analytics = insights['analytics']
                summary.append(f"\nInteraction Statistics:")
                summary.append(f"  - Total interactions: {analytics.get('total_interactions', 0)}")
                if analytics.get('avg_sentiment') is not None:
                    sentiment = analytics['avg_sentiment']
                    sentiment_desc = "positive" if sentiment > 0.1 else "neutral" if sentiment > -0.1 else "negative"
                    summary.append(f"  - Average sentiment: {sentiment:.2f} ({sentiment_desc})")
            
            return "\n".join(summary)
        
        except Exception as e:
            return f"Error retrieving user insights: {e}"
    
    def bulk_import_conversation(self, user_id: str, conversation_file: str):
        """Import a conversation from a file for bulk learning"""
        try:
            with open(conversation_file, 'r', encoding='utf-8') as f:
                conversation = json.load(f)
            
            messages = []
            for turn in conversation:
                if turn.get('role') == 'user':
                    messages.append(turn['content'])
            
            # Bulk upload to learning system
            result = self.sdk.bulk_upload(user_id, messages)
            print(f"Imported {result['interactions_created']} interactions")
            print(f"Learned {result['facts_learned']} new facts")
            
        except Exception as e:
            print(f"Error importing conversation: {e}")


def interactive_chat():
    """Run an interactive chat session"""
    
    print("🚀 Initializing LM Studio + AI Learning integration...")
    
    # Check if systems are available
    sdk = AIUserLearningSDK()
    if not sdk.health_check():
        print("⚠️ Warning: AI User Learning System not available at http://localhost:5000")
        print("Please start the learning system first with: python app.py")
        return
    
    # Test LM Studio connection
    try:
        import requests
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code != 200:
            print("⚠️ Warning: LM Studio not responding at http://localhost:1234")
            print("Please make sure LM Studio is running with a model loaded")
            return
        
        models = response.json().get('data', [])
        if not models:
            print("⚠️ Warning: No models loaded in LM Studio")
            print("Please load a model in LM Studio before proceeding")
            return
        
        print(f"✅ Connected to LM Studio. Available models: {[m['id'] for m in models]}")
        
    except Exception as e:
        print(f"⚠️ Error connecting to LM Studio: {e}")
        return
    
    chat_system = PersonalizedLMStudioChat()
    
    print("\n🤖 AI Learning Chatbot with LM Studio")
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


def batch_learning_example():
    """Example of batch learning from conversation history"""
    
    chat_system = PersonalizedLMStudioChat()
    
    # Example conversation for bulk import
    example_conversation = [
        {"role": "user", "content": "Hi, I'm new here"},
        {"role": "assistant", "content": "Hello! Welcome. Tell me about yourself."},
        {"role": "user", "content": "I love playing guitar and listening to jazz music"},
        {"role": "assistant", "content": "That's wonderful! How long have you been playing guitar?"},
        {"role": "user", "content": "About 5 years. I also enjoy hiking on weekends"},
        {"role": "assistant", "content": "Guitar and hiking - great hobbies! What's your favorite hiking spot?"},
        {"role": "user", "content": "I prefer mountain trails. I'm also a software developer"},
        {"role": "assistant", "content": "Interesting combination of interests! What programming languages do you use?"},
        {"role": "user", "content": "Mainly Python and JavaScript. I work on web applications"},
    ]
    
    # Save example conversation
    with open('example_conversation.json', 'w') as f:
        json.dump(example_conversation, f, indent=2)
    
    print("📁 Created example conversation file")
    
    # Import conversation for learning
    user_id = "batch_user"
    chat_system.bulk_import_conversation(user_id, 'example_conversation.json')
    
    # Show learned insights
    print(f"\n📊 Learned insights:")
    summary = chat_system.get_user_summary(user_id)
    print(summary)
    
    # Test personalized response
    print(f"\n🧪 Testing personalized response:")
    response = chat_system.chat(user_id, "What should I do this weekend?")
    print(f"Response: {response}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LM Studio + AI Learning Integration")
    parser.add_argument("--mode", choices=["chat", "batch"], default="chat",
                       help="Run mode: 'chat' for interactive chat, 'batch' for batch learning example")
    
    args = parser.parse_args()
    
    if args.mode == "chat":
        interactive_chat()
    else:
        batch_learning_example()