"""
Quick Demo: Webhook/SDK Integration

This script demonstrates how easy it is to integrate any chatbot 
with the AI User Learning System.

Run this after starting the main system (python app.py)
"""

import sys
import os
import time

# Add SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sdk import AIUserLearningSDK, ChatMessage


def demo_basic_integration():
    """Demo basic SDK integration"""
    print("🚀 AI User Learning System - SDK Demo")
    print("=" * 50)
    
    # Initialize SDK
    sdk = AIUserLearningSDK("http://localhost:5000")
    
    # Check if system is running
    if not sdk.health_check():
        print("❌ Learning system not available at http://localhost:5000")
        print("Please start the system first: python app.py")
        return
    
    print("✅ Connected to AI User Learning System")
    
    user_id = "demo_user"
    
    # Simulate a conversation
    conversation = [
        ("Hello! I'm new here", "Welcome! Tell me about yourself."),
        ("I love playing guitar and jazz music", "That's wonderful! How long have you been playing?"),
        ("About 5 years. I also enjoy hiking", "Great hobbies! What's your favorite hiking spot?"),
        ("I prefer mountain trails. I work as a software developer too", "Interesting! What programming languages do you use?"),
        ("Mainly Python and JavaScript for web apps", "Nice! I'll remember your interests for future conversations."),
    ]
    
    print(f"\n💬 Simulating conversation for user: {user_id}")
    print("-" * 50)
    
    # Log each interaction
    for i, (user_msg, bot_response) in enumerate(conversation, 1):
        print(f"\nStep {i}/5: Logging interaction...")
        print(f"User: {user_msg}")
        print(f"Bot: {bot_response}")
        
        # Log with SDK
        chat_msg = ChatMessage(
            user_id=user_id,
            message=user_msg,
            response=bot_response,
            metadata={'source': 'demo', 'step': i}
        )
        
        try:
            result = sdk.log_message(chat_msg)
            print(f"✅ Logged (interaction_id: {result.get('interaction_id')})")
            
            if result.get('learned_facts_count', 0) > 0:
                print(f"🧠 Learned {result['learned_facts_count']} new facts!")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Small delay for demo effect
    
    print(f"\n📊 Getting insights for {user_id}...")
    
    # Get user insights
    try:
        insights = sdk.get_user_insights(user_id, limit=10)
        
        print(f"\n🎯 User Profile Summary:")
        print(f"  Total interactions: {insights.get('analytics', {}).get('total_interactions', 0)}")
        print(f"  Facts learned: {len(insights.get('facts', []))}")
        
        if insights.get('facts'):
            print(f"\n🧠 Learned Facts:")
            for fact in insights['facts'][:5]:
                confidence_emoji = {"high": "🔥", "medium": "👍", "low": "🤔"}.get(fact['confidence'], "")
                print(f"  • {fact['value']} {confidence_emoji}")
        
        if insights.get('suggestions'):
            print(f"\n💡 Personalization Suggestions:")
            for suggestion in insights['suggestions'][:3]:
                print(f"  • {suggestion}")
        
        # Show context for next conversation
        context = sdk.get_personalization_context(user_id)
        if context:
            print(f"\n📝 Context for next conversation:")
            print(f"  {context[:200]}..." if len(context) > 200 else context)
    
    except Exception as e:
        print(f"❌ Error getting insights: {e}")
    
    print(f"\n🎉 Demo completed! User {user_id} now has a personalized profile.")
    print("Try asking questions about their interests in your chatbot!")


def demo_context_injection():
    """Demo how to use context for personalization"""
    print("\n" + "=" * 50)
    print("🧠 Context Injection Demo")
    print("=" * 50)
    
    sdk = AIUserLearningSDK("http://localhost:5000")
    
    user_id = "demo_user"
    
    # Get user context
    context = sdk.get_personalization_context(user_id)
    
    print(f"📝 User context for {user_id}:")
    print(context if context else "No context available yet")
    
    # Simulate using context in a chatbot prompt
    user_message = "What should I do this weekend?"
    
    # This is how you'd inject context into your LLM prompt
    enhanced_prompt = f"""
You are a helpful AI assistant. Use the following user context to personalize your response:

User Context:
{context}

User Message: {user_message}

Provide a personalized response based on what you know about the user:
"""
    
    print(f"\n🚀 Enhanced prompt for LLM:")
    print(enhanced_prompt)
    
    # Simulate LLM response (in real usage, you'd call your LLM here)
    simulated_response = "Based on your interests, I'd suggest going on a mountain hike this weekend! You could also bring your guitar and practice some jazz pieces in nature. If you want to code, maybe work on a music-related web app project?"
    
    print(f"\n🤖 Personalized response:")
    print(simulated_response)
    
    # Log this interaction too
    chat_msg = ChatMessage(
        user_id=user_id,
        message=user_message,
        response=simulated_response,
        metadata={'source': 'demo', 'context_used': True}
    )
    
    try:
        result = sdk.log_message(chat_msg)
        print(f"\n✅ Interaction logged with context usage")
    except Exception as e:
        print(f"❌ Error logging: {e}")


if __name__ == "__main__":
    try:
        demo_basic_integration()
        demo_context_injection()
        
        print(f"\n🔗 Next Steps:")
        print(f"  1. Check the web dashboard: http://localhost:5000")
        print(f"  2. Try the Gradio example: python examples/integrations/gradio_example.py")
        print(f"  3. Integrate with your own chatbot using the SDK!")
        print(f"  4. Read the docs: docs/WEBHOOK_SDK_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Make sure the AI User Learning System is running!")