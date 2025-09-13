"""
Gradio Chatbot Integration Example

This example shows how to create a Gradio chatbot that learns about users
through the AI User Learning System.

Requirements:
    pip install gradio openai

Usage:
    python gradio_example.py
"""

import gradio as gr
import sys
import os

# Add the parent directory to the path to import the SDK
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from sdk import quick_gradio_setup, AIUserLearningSDK, ChatMessage


class LearningChatbot:
    def __init__(self, learning_url="http://localhost:5000"):
        """Initialize the learning chatbot"""
        self.sdk = AIUserLearningSDK(learning_url)
        self.gradio_integration = quick_gradio_setup(learning_url)
        
        # Simple response templates based on user insights
        self.response_templates = {
            'interests': "That's interesting! I remember you mentioned {interest} before.",
            'greeting': "Hello! Nice to chat with you again.",
            'learning': "I'm learning more about your preferences. Thanks for sharing!",
            'default': "I understand. Tell me more about that."
        }
    
    def generate_response(self, message: str, context: str = "") -> str:
        """
        Generate a response based on message and user context
        
        In a real implementation, you would:
        1. Use an LLM (OpenAI, local model, etc.)
        2. Inject the context into the prompt
        3. Generate a personalized response
        """
        message_lower = message.lower()
        
        # Simple rule-based responses for demo
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            if 'interests' in context.lower():
                return "Hello! Good to see you again. How are your interests going?"
            return "Hello! Nice to meet you. What would you like to talk about?"
        
        elif any(word in message_lower for word in ['like', 'love', 'enjoy']):
            return "That sounds great! I'll remember that you enjoy this. What specifically do you like about it?"
        
        elif any(word in message_lower for word in ['help', 'how', 'what']):
            return "I'd be happy to help! Based on what I know about you, let me provide some relevant information."
        
        elif 'music' in message_lower:
            if 'music' in context.lower():
                return "I see you're still interested in music! What genre are you listening to lately?"
            return "Music is wonderful! What type of music do you enjoy?"
        
        else:
            return f"That's interesting! I'm learning more about you with each conversation. {message}"
    
    def chat_interface(self, message, history, user_id="gradio_user"):
        """Main chat interface for Gradio"""
        if not message.strip():
            return "", history
        
        # Get user context for personalization
        context = self.sdk.get_personalization_context(user_id)
        
        # Generate response
        bot_response = self.generate_response(message, context)
        
        # Log the interaction
        chat_msg = ChatMessage(
            user_id=user_id,
            message=message,
            response=bot_response,
            metadata={'source': 'gradio', 'context_used': bool(context)}
        )
        
        try:
            result = self.sdk.log_message(chat_msg)
            print(f"Logged interaction for user {user_id}: {result}")
        except Exception as e:
            print(f"Failed to log interaction: {e}")
        
        # Update history
        history.append([message, bot_response])
        
        return "", history
    
    def get_user_insights_display(self, user_id="gradio_user"):
        """Get formatted user insights for display"""
        try:
            insights = self.sdk.get_user_insights(user_id, limit=5)
            
            if not insights.get('facts'):
                return "No insights learned yet. Start chatting to build your profile!"
            
            output = []
            output.append("## 🧠 What I've Learned About You:")
            
            # Facts by category
            categories = {}
            for fact in insights['facts']:
                cat = fact['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(fact)
            
            for category, facts in categories.items():
                output.append(f"\n### {category.title()}:")
                for fact in facts:
                    confidence_emoji = {"high": "🔥", "medium": "👍", "low": "🤔"}.get(fact['confidence'], "")
                    output.append(f"- {fact['value']} {confidence_emoji}")
            
            # Recent topics
            if insights.get('recent_interactions'):
                topics = set()
                for interaction in insights['recent_interactions']:
                    if interaction.get('topics'):
                        topics.update(interaction['topics'][:2])
                
                if topics:
                    output.append(f"\n### Recent Topics:")
                    for topic in list(topics)[:5]:
                        output.append(f"- {topic}")
            
            # Analytics
            if insights.get('analytics'):
                analytics = insights['analytics']
                output.append(f"\n### Analytics:")
                output.append(f"- Total interactions: {analytics.get('total_interactions', 0)}")
                if analytics.get('avg_sentiment') is not None:
                    sentiment = analytics['avg_sentiment']
                    sentiment_text = "😊 Positive" if sentiment > 0.1 else "😐 Neutral" if sentiment > -0.1 else "😔 Negative"
                    output.append(f"- Average sentiment: {sentiment_text}")
            
            return "\n".join(output)
        
        except Exception as e:
            return f"Error retrieving insights: {e}"


def create_gradio_interface():
    """Create and launch the Gradio interface"""
    
    # Check if learning system is available
    sdk = AIUserLearningSDK()
    if not sdk.health_check():
        print("⚠️ Warning: AI User Learning System not available at http://localhost:5000")
        print("Please start the learning system first with: python app.py")
    
    chatbot = LearningChatbot()
    
    with gr.Blocks(title="AI Learning Chatbot", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🤖 AI Learning Chatbot
        
        This chatbot learns about you as you chat and personalizes responses based on your interests and preferences.
        
        **Features:**
        - Remembers your interests and preferences
        - Adapts responses based on conversation history
        - Provides insights about what it has learned
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                chatbot_ui = gr.Chatbot(label="Chat", height=400, type="messages")
                with gr.Row():
                    msg = gr.Textbox(
                        label="Message",
                        placeholder="Type your message here...",
                        container=False,
                        scale=4
                    )
                    user_id_input = gr.Textbox(
                        label="User ID",
                        value="gradio_user",
                        container=False,
                        scale=1
                    )
                
                with gr.Row():
                    submit_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear")
            
            with gr.Column(scale=1):
                insights_display = gr.Markdown(label="User Insights")
                refresh_insights_btn = gr.Button("Refresh Insights")
        
        # Event handlers
        def submit_and_refresh(message, history, user_id):
            # Process chat
            _, updated_history = chatbot.chat_interface(message, history, user_id)
            
            # Get updated insights
            insights = chatbot.get_user_insights_display(user_id)
            
            return "", updated_history, insights
        
        submit_btn.click(
            submit_and_refresh,
            inputs=[msg, chatbot_ui, user_id_input],
            outputs=[msg, chatbot_ui, insights_display]
        )
        
        msg.submit(
            submit_and_refresh,
            inputs=[msg, chatbot_ui, user_id_input],
            outputs=[msg, chatbot_ui, insights_display]
        )
        
        clear_btn.click(
            lambda: ([], ""),
            outputs=[chatbot_ui, insights_display]
        )
        
        refresh_insights_btn.click(
            chatbot.get_user_insights_display,
            inputs=[user_id_input],
            outputs=[insights_display]
        )
        
        # Load initial insights
        demo.load(
            chatbot.get_user_insights_display,
            inputs=[user_id_input],
            outputs=[insights_display]
        )
    
    return demo


if __name__ == "__main__":
    print("🚀 Starting AI Learning Chatbot with Gradio...")
    print("💡 Make sure the AI User Learning System is running at http://localhost:5000")
    
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )