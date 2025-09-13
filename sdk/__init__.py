"""
AI User Learning System SDK

A Python client library for integrating chatbots with the AI User Learning System.
Provides easy-to-use methods for logging interactions and retrieving user insights.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Represents a chat message"""
    user_id: str
    message: str
    response: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UserInsight:
    """Represents a user insight/fact"""
    category: str
    type: str
    key: str
    value: str
    confidence: str
    evidence_count: int
    last_updated: Optional[str] = None


@dataclass
class UserAnalytics:
    """User analytics data"""
    total_interactions: int
    avg_sentiment: float
    most_active_hour: Optional[int]
    top_topics: List[str]
    communication_style: str


class AIUserLearningSDK:
    """
    SDK client for the AI User Learning System
    
    Provides methods to:
    - Log chat interactions
    - Retrieve user insights and facts
    - Get personalization data for chatbots
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        """
        Initialize the SDK client
        
        Args:
            base_url: Base URL of the AI User Learning System API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AIUserLearningSDK/1.0'
        })
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def log_message(self, chat_message: ChatMessage) -> Dict[str, Any]:
        """
        Log a chat message and bot response
        
        Args:
            chat_message: ChatMessage object containing the interaction data
            
        Returns:
            Response data from the API
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/webhook/chat/message"
        
        payload = {
            'user_id': chat_message.user_id,
            'message': chat_message.message,
            'response': chat_message.response,
            'session_id': chat_message.session_id,
            'metadata': chat_message.metadata
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Failed to log message: {e}")
            raise
    
    def get_user_insights(self, user_id: str, 
                         categories: Optional[List[str]] = None,
                         limit: int = 10,
                         min_confidence: str = 'low') -> Dict[str, Any]:
        """
        Get user insights and facts for personalization
        
        Args:
            user_id: User identifier
            categories: List of fact categories to filter by
            limit: Maximum number of facts to return
            min_confidence: Minimum confidence level (low, medium, high)
            
        Returns:
            User insights data including facts, recent interactions, and analytics
        """
        url = f"{self.base_url}/webhook/chat/insights/{user_id}"
        
        params = {
            'limit': limit,
            'confidence': min_confidence
        }
        
        if categories:
            params['categories'] = ','.join(categories)
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Failed to get user insights: {e}")
            raise
    
    def bulk_upload(self, user_id: str, messages: List[str]) -> Dict[str, Any]:
        """
        Upload multiple messages in bulk for batch processing
        
        Args:
            user_id: User identifier
            messages: List of message strings
            
        Returns:
            Bulk upload response with processing statistics
        """
        url = f"{self.base_url}/webhook/chat/bulk"
        
        interactions = [
            {
                'message': msg,
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            for msg in messages
        ]
        
        payload = {
            'user_id': user_id,
            'interactions': interactions
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Failed to bulk upload: {e}")
            raise
    
    def get_personalization_context(self, user_id: str) -> str:
        """
        Get a formatted string of user context for chatbot personalization
        
        Args:
            user_id: User identifier
            
        Returns:
            Formatted string containing user insights for prompt injection
        """
        try:
            insights = self.get_user_insights(user_id, limit=5)
            
            context_parts = []
            
            # Add user facts
            if insights.get('facts'):
                facts_text = []
                for fact in insights['facts']:
                    if fact['confidence'] in ['high', 'medium']:
                        facts_text.append(f"- {fact['value']}")
                
                if facts_text:
                    context_parts.append("User Profile:\n" + "\n".join(facts_text))
            
            # Add recent context
            if insights.get('recent_interactions'):
                recent = insights['recent_interactions'][:2]  # Last 2 interactions
                if recent:
                    recent_text = []
                    for interaction in recent:
                        if interaction.get('topics'):
                            topics = ', '.join(interaction['topics'][:3])
                            recent_text.append(f"- Recently discussed: {topics}")
                    
                    if recent_text:
                        context_parts.append("Recent Context:\n" + "\n".join(recent_text))
            
            # Add suggestions
            if insights.get('suggestions'):
                suggestions = insights['suggestions'][:2]
                if suggestions:
                    context_parts.append("Conversation Tips:\n" + "\n".join(f"- {s}" for s in suggestions))
            
            return "\n\n".join(context_parts) if context_parts else ""
        
        except Exception as e:
            logger.error(f"Failed to get personalization context: {e}")
            return ""
    
    def health_check(self) -> bool:
        """
        Check if the API is accessible
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}/health"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        
        except Exception:
            return False


class GradioIntegration:
    """Helper class for Gradio chatbot integration"""
    
    def __init__(self, sdk: AIUserLearningSDK, default_user_id: str = "gradio_user"):
        self.sdk = sdk
        self.default_user_id = default_user_id
        self.conversation_history = []
    
    def chat_with_learning(self, message: str, user_id: Optional[str] = None, 
                          chatbot_response_fn=None) -> tuple:
        """
        Process a chat message with learning integration
        
        Args:
            message: User message
            user_id: Optional user identifier (defaults to default_user_id)
            chatbot_response_fn: Function that generates bot response
            
        Returns:
            Tuple of (bot_response, updated_history)
        """
        user_id = user_id or self.default_user_id
        
        # Get user context for personalization
        context = self.sdk.get_personalization_context(user_id)
        
        # Generate bot response (you can inject context here)
        if chatbot_response_fn:
            bot_response = chatbot_response_fn(message, context)
        else:
            bot_response = f"I received: {message}"
        
        # Log the interaction
        chat_msg = ChatMessage(
            user_id=user_id,
            message=message,
            response=bot_response,
            metadata={'source': 'gradio', 'context_used': bool(context)}
        )
        
        try:
            self.sdk.log_message(chat_msg)
        except Exception as e:
            logger.error(f"Failed to log interaction: {e}")
        
        # Update conversation history
        self.conversation_history.append([message, bot_response])
        
        return bot_response, self.conversation_history


class LMStudioIntegration:
    """Helper class for LM Studio integration"""
    
    def __init__(self, sdk: AIUserLearningSDK, lm_studio_url: str = "http://localhost:1234/v1"):
        self.sdk = sdk
        self.lm_studio_url = lm_studio_url.rstrip('/')
        self.lm_session = requests.Session()
    
    def enhanced_chat_completion(self, messages: List[Dict], user_id: str, **kwargs) -> Dict:
        """
        Send chat completion request to LM Studio with user learning enhancement
        
        Args:
            messages: OpenAI-format message list
            user_id: User identifier for learning
            **kwargs: Additional parameters for LM Studio
            
        Returns:
            Enhanced response with learning integration
        """
        # Get user context
        context = self.sdk.get_personalization_context(user_id)
        
        # Inject context into system message
        enhanced_messages = messages.copy()
        if context and enhanced_messages:
            if enhanced_messages[0].get('role') == 'system':
                # Append to existing system message
                enhanced_messages[0]['content'] += f"\n\nUser Context:\n{context}"
            else:
                # Insert new system message
                enhanced_messages.insert(0, {
                    'role': 'system',
                    'content': f"User Context:\n{context}"
                })
        
        # Send to LM Studio
        try:
            url = f"{self.lm_studio_url}/chat/completions"
            payload = {
                'messages': enhanced_messages,
                **kwargs
            }
            
            response = self.lm_session.post(url, json=payload)
            response.raise_for_status()
            lm_response = response.json()
            
            # Extract user message and bot response
            if messages and len(messages) > 0:
                user_message = messages[-1].get('content', '')
                bot_response = lm_response.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Log the interaction
                chat_msg = ChatMessage(
                    user_id=user_id,
                    message=user_message,
                    response=bot_response,
                    metadata={
                        'source': 'lm_studio',
                        'model': kwargs.get('model', 'unknown'),
                        'context_enhanced': bool(context)
                    }
                )
                
                try:
                    self.sdk.log_message(chat_msg)
                except Exception as e:
                    logger.error(f"Failed to log LM Studio interaction: {e}")
            
            return lm_response
        
        except Exception as e:
            logger.error(f"LM Studio enhanced chat error: {e}")
            raise


# Convenience functions for quick integration
def quick_gradio_setup(base_url: str = "http://localhost:5000", 
                      user_id: str = "gradio_user") -> GradioIntegration:
    """Quick setup for Gradio integration"""
    sdk = AIUserLearningSDK(base_url)
    return GradioIntegration(sdk, user_id)


def quick_lm_studio_setup(learning_url: str = "http://localhost:5000",
                         lm_studio_url: str = "http://localhost:1234/v1") -> LMStudioIntegration:
    """Quick setup for LM Studio integration"""
    sdk = AIUserLearningSDK(learning_url)
    return LMStudioIntegration(sdk, lm_studio_url)