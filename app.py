"""
Main Flask application for the AI User Learning System
"""

import os
import logging
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
from flask import Flask, request, jsonify, render_template, Response, stream_template
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

# Import our modules
from database import db_manager, UserRepository, InteractionRepository, LearnedFactRepository
from ai.learning_engine import LearningEngine
from models import InteractionType, LearningConfidence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Webhook configuration
WEBHOOK_API_KEY = os.getenv('WEBHOOK_API_KEY', 'dev-webhook-key-change-in-production')
RATE_LIMIT_WINDOW = 300  # 5 minutes
RATE_LIMIT_MAX_REQUESTS = 100  # requests per window

# Rate limiting storage (in production, use Redis)
rate_limit_store = defaultdict(list)

# Enable CORS for cross-origin requests
CORS(app)

# Initialize learning engine
learning_engine = LearningEngine()


# =============================================================================
# AUTHENTICATION AND RATE LIMITING MIDDLEWARE
# =============================================================================

def webhook_auth_required(f):
    """Decorator for webhook authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        api_key = request.headers.get('X-API-Key')
        
        # Check Bearer token
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if token == WEBHOOK_API_KEY:
                return f(*args, **kwargs)
        
        # Check API key header
        if api_key == WEBHOOK_API_KEY:
            return f(*args, **kwargs)
        
        # Allow development mode without auth
        if WEBHOOK_API_KEY == 'dev-webhook-key-change-in-production':
            logger.warning("Using development webhook key - set WEBHOOK_API_KEY in production!")
            return f(*args, **kwargs)
        
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated_function


def rate_limit(max_requests=None, window=None):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            api_key = request.headers.get('X-API-Key', 'anonymous')
            client_id = f"{client_ip}:{api_key}"
            
            # Use provided limits or defaults
            limit = max_requests or RATE_LIMIT_MAX_REQUESTS
            time_window = window or RATE_LIMIT_WINDOW
            
            current_time = time.time()
            client_requests = rate_limit_store[client_id]
            
            # Clean old requests outside the window
            client_requests[:] = [req_time for req_time in client_requests 
                                if current_time - req_time < time_window]
            
            # Check if limit exceeded
            if len(client_requests) >= limit:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': limit,
                    'window': time_window,
                    'retry_after': time_window
                }), 429
            
            # Add current request
            client_requests.append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Analytics not found'}), 404


# =============================================================================
# WEBHOOK/SDK ENDPOINTS FOR CHATBOT INTEGRATION
# =============================================================================

@app.route('/webhook/chat/message', methods=['POST'])
@webhook_auth_required
@rate_limit(max_requests=50, window=300)  # 50 requests per 5 minutes
def webhook_chat_message():
    """
    Webhook endpoint for chatbots to log interactions and get instant insights
    
    Expected payload:
    {
        "user_id": "user123",
        "message": "I love playing guitar",
        "response": "That's great! What type of music do you like?",
        "session_id": "optional_session_id",
        "metadata": {"source": "gradio", "model": "llama-2"}
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data or 'user_id' not in data or 'message' not in data:
            return jsonify({
                'error': 'Missing required fields: user_id, message'
            }), 400
        
        user_identifier = data['user_id']
        user_message = data['message']
        bot_response = data.get('response', '')
        session_id = data.get('session_id')
        metadata = data.get('metadata', {})
        
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            interaction_repo = InteractionRepository(session)
            
            # Find or create user
            user = user_repo.get_user_by_username(user_identifier)
            if not user:
                user = user_repo.create_user(
                    username=user_identifier,
                    email=f"{user_identifier}@chatbot.local"
                )
                session.commit()
            
            # Log user message
            user_interaction = interaction_repo.create_interaction(
                user_id=user.id,
                content=user_message,
                interaction_type=InteractionType.MESSAGE,
                metadata=metadata,
                session_id=session_id
            )
            
            # Log bot response if provided
            if bot_response:
                bot_interaction = interaction_repo.create_interaction(
                    user_id=user.id,
                    content=bot_response,
                    interaction_type=InteractionType.BOT_RESPONSE,
                    metadata=metadata,
                    session_id=session_id
                )
            
            session.commit()
            
            # Trigger AI learning
            try:
                recent_interactions = interaction_repo.get_user_interactions(
                    user.id, limit=20
                )
                learning_result = learning_engine.process_user_interactions(
                    user.id, recent_interactions
                )
                
                # Store any new facts
                fact_repo = LearnedFactRepository(session)
                for fact_data in learning_result.new_facts:
                    fact_repo.create_fact(
                        user_id=user.id,
                        category=fact_data.get('category'),
                        fact_type=fact_data.get('fact_type'),
                        fact_key=fact_data.get('fact_key'),
                        fact_value=fact_data.get('fact_value'),
                        confidence_level=fact_data.get('confidence_level'),
                        evidence_count=fact_data.get('evidence_count', 1),
                        learning_method=fact_data.get('learning_method')
                    )
                session.commit()
                
            except Exception as e:
                logger.error(f"Learning error: {e}")
                # Continue even if learning fails
            
            return jsonify({
                'success': True,
                'user_id': user.id,
                'interaction_id': user_interaction.id,
                'learned_facts_count': len(learning_result.new_facts) if 'learning_result' in locals() else 0,
                'message': 'Interaction logged and processed'
            })
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/chat/insights/<user_identifier>', methods=['GET'])
@webhook_auth_required
@rate_limit(max_requests=100, window=300)  # 100 requests per 5 minutes
def webhook_get_insights(user_identifier):
    """
    Get user insights and facts for chatbot personalization
    
    Query parameters:
    - categories: comma-separated list (e.g., "interests,behavior")
    - limit: max number of facts to return
    - confidence: minimum confidence level (high, medium, low)
    """
    try:
        # Query parameters
        categories = request.args.get('categories', '').split(',') if request.args.get('categories') else None
        limit = int(request.args.get('limit', 10))
        min_confidence = request.args.get('confidence', 'low')
        
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            fact_repo = LearnedFactRepository(session)
            interaction_repo = InteractionRepository(session)
            
            # Find user
            user = user_repo.get_user_by_username(user_identifier)
            if not user:
                return jsonify({
                    'error': f'User {user_identifier} not found'
                }), 404
            
            # Get user facts
            facts = fact_repo.get_user_facts(
                user.id,
                categories=categories,
                min_confidence=min_confidence,
                limit=limit
            )
            
            # Get recent interactions for context
            recent_interactions = interaction_repo.get_user_interactions(
                user.id, limit=5
            )
            
            # Get user analytics
            analytics = user_repo.get_user_analytics(user.id)
            
            return jsonify({
                'user_id': user.id,
                'username': user.username,
                'facts': [
                    {
                        'category': fact.category,
                        'type': fact.fact_type,
                        'key': fact.fact_key,
                        'value': fact.fact_value,
                        'confidence': fact.confidence_level,
                        'evidence_count': fact.evidence_count,
                        'last_updated': fact.updated_at.isoformat() if fact.updated_at else None
                    }
                    for fact in facts
                ],
                'recent_interactions': [
                    {
                        'content': interaction.content,
                        'type': interaction.interaction_type,
                        'sentiment': interaction.sentiment,
                        'topics': interaction.topics,
                        'timestamp': interaction.timestamp.isoformat()
                    }
                    for interaction in recent_interactions
                ],
                'analytics': analytics,
                'suggestions': [
                    f"User shows interest in {fact.fact_value}" 
                    for fact in facts 
                    if fact.category == 'interests'
                ][:3]
            })
            
    except Exception as e:
        logger.error(f"Insights webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/chat/bulk', methods=['POST'])
@webhook_auth_required
@rate_limit(max_requests=10, window=300)  # 10 bulk uploads per 5 minutes
def webhook_bulk_interactions():
    """
    Bulk upload interactions for batch processing
    
    Expected payload:
    {
        "user_id": "user123",
        "interactions": [
            {"message": "Hello", "timestamp": "2025-01-01T12:00:00Z"},
            {"message": "I like music", "timestamp": "2025-01-01T12:01:00Z"}
        ]
    }
    """
    try:
        data = request.json
        
        if not data or 'user_id' not in data or 'interactions' not in data:
            return jsonify({
                'error': 'Missing required fields: user_id, interactions'
            }), 400
        
        user_identifier = data['user_id']
        interactions_data = data['interactions']
        
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            interaction_repo = InteractionRepository(session)
            
            # Find or create user
            user = user_repo.get_user_by_username(user_identifier)
            if not user:
                user = user_repo.create_user(
                    username=user_identifier,
                    email=f"{user_identifier}@chatbot.local"
                )
                session.commit()
            
            # Create interactions
            created_interactions = []
            for interaction_data in interactions_data:
                interaction = interaction_repo.create_interaction(
                    user_id=user.id,
                    content=interaction_data['message'],
                    interaction_type=InteractionType.MESSAGE,
                    metadata=interaction_data.get('metadata', {}),
                    session_id=interaction_data.get('session_id')
                )
                created_interactions.append(interaction)
            
            session.commit()
            
            # Trigger learning on all interactions
            all_interactions = interaction_repo.get_user_interactions(user.id)
            learning_result = learning_engine.process_user_interactions(
                user.id, all_interactions
            )
            
            # Store new facts
            fact_repo = LearnedFactRepository(session)
            for fact_data in learning_result.new_facts:
                fact_repo.create_fact(
                    user_id=user.id,
                    category=fact_data.get('category'),
                    fact_type=fact_data.get('fact_type'),
                    fact_key=fact_data.get('fact_key'),
                    fact_value=fact_data.get('fact_value'),
                    confidence_level=fact_data.get('confidence_level'),
                    evidence_count=fact_data.get('evidence_count', 1),
                    learning_method=fact_data.get('learning_method')
                )
            session.commit()
            
            return jsonify({
                'success': True,
                'user_id': user.id,
                'interactions_created': len(created_interactions),
                'facts_learned': len(learning_result.new_facts),
                'processing_time_ms': learning_result.processing_time_ms
            })
            
    except Exception as e:
        logger.error(f"Bulk webhook error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/stream/insights/<user_identifier>')
@webhook_auth_required
@rate_limit(max_requests=10, window=300)  # 10 stream connections per 5 minutes
def stream_user_insights(user_identifier):
    """
    Server-Sent Events stream for real-time user insights
    
    Usage:
        EventSource('/webhook/stream/insights/user123')
    """
    def generate_insights():
        """Generate real-time insights stream"""
        last_fact_count = 0
        last_interaction_count = 0
        
        while True:
            try:
                with db_manager.get_session() as session:
                    user_repo = UserRepository(session)
                    fact_repo = LearnedFactRepository(session)
                    interaction_repo = InteractionRepository(session)
                    
                    # Find user
                    user = user_repo.get_user_by_username(user_identifier)
                    if not user:
                        yield f"data: {json.dumps({'error': 'User not found'})}\n\n"
                        break
                    
                    # Get current counts
                    current_facts = fact_repo.get_user_facts(user.id, limit=100)
                    current_interactions = interaction_repo.get_user_interactions(user.id, limit=1)
                    
                    fact_count = len(current_facts)
                    interaction_count = len(current_interactions)
                    
                    # Check if there are updates
                    if fact_count != last_fact_count or interaction_count != last_interaction_count:
                        # Get latest insights
                        recent_facts = current_facts[:5]  # Latest 5 facts
                        analytics = user_repo.get_user_analytics(user.id)
                        
                        update_data = {
                            'timestamp': datetime.utcnow().isoformat(),
                            'user_id': user.id,
                            'username': user.username,
                            'updates': {
                                'new_facts': fact_count - last_fact_count,
                                'new_interactions': interaction_count - last_interaction_count
                            },
                            'latest_facts': [
                                {
                                    'category': fact.category,
                                    'value': fact.fact_value,
                                    'confidence': fact.confidence_level,
                                    'created_at': fact.created_at.isoformat() if fact.created_at else None
                                }
                                for fact in recent_facts
                            ],
                            'analytics': analytics
                        }
                        
                        yield f"data: {json.dumps(update_data)}\n\n"
                        
                        last_fact_count = fact_count
                        last_interaction_count = interaction_count
                    
                    # Wait before next check
                    time.sleep(2)
                    
            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
    
    return Response(
        generate_insights(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )


@app.route('/webhook/stream/learning/<user_identifier>')
@webhook_auth_required
@rate_limit(max_requests=5, window=300)  # 5 learning streams per 5 minutes
def stream_learning_process(user_identifier):
    """
    Server-Sent Events stream for real-time learning process updates
    
    This endpoint streams live updates during the AI learning process
    """
    def generate_learning_updates():
        """Generate real-time learning process updates"""
        try:
            with db_manager.get_session() as session:
                user_repo = UserRepository(session)
                interaction_repo = InteractionRepository(session)
                
                # Find user
                user = user_repo.get_user_by_username(user_identifier)
                if not user:
                    yield f"data: {json.dumps({'error': 'User not found'})}\n\n"
                    return
                
                # Start learning process
                yield f"data: {json.dumps({'status': 'starting', 'message': 'Initializing learning process...'})}\n\n"
                
                # Get user interactions
                interactions = interaction_repo.get_user_interactions(user.id)
                
                yield f"data: {json.dumps({'status': 'analyzing', 'message': f'Analyzing {len(interactions)} interactions...'})}\n\n"
                
                # Process interactions with the learning engine
                learning_result = learning_engine.process_user_interactions(user.id, interactions)
                
                yield f"data: {json.dumps({'status': 'learning', 'message': f'Extracted {len(learning_result.new_facts)} new insights...'})}\n\n"
                
                # Store new facts
                if learning_result.new_facts:
                    fact_repo = LearnedFactRepository(session)
                    stored_facts = []
                    
                    for i, fact_data in enumerate(learning_result.new_facts):
                        fact = fact_repo.create_fact(
                            user_id=user.id,
                            category=fact_data.get('category'),
                            fact_type=fact_data.get('fact_type'),
                            fact_key=fact_data.get('fact_key'),
                            fact_value=fact_data.get('fact_value'),
                            confidence_level=fact_data.get('confidence_level'),
                            evidence_count=fact_data.get('evidence_count', 1),
                            learning_method=fact_data.get('learning_method')
                        )
                        stored_facts.append(fact)
                        
                        # Stream each fact as it's stored
                        yield f"data: {json.dumps({'status': 'storing', 'message': f'Stored fact: {fact.fact_value}', 'fact': {'category': fact.category, 'value': fact.fact_value, 'confidence': fact.confidence_level}})}\n\n"
                    
                    session.commit()
                
                # Final summary
                final_result = {
                    'status': 'completed',
                    'message': 'Learning process completed successfully',
                    'summary': {
                        'interactions_processed': learning_result.processing_time_ms,
                        'facts_learned': len(learning_result.new_facts),
                        'processing_time_ms': learning_result.processing_time_ms,
                        'errors': learning_result.errors
                    }
                }
                
                yield f"data: {json.dumps(final_result)}\n\n"
                
        except Exception as e:
            logger.error(f"Learning stream error: {e}")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
    
    return Response(
        generate_learning_updates(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )


# Frontend routes

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db_healthy = db_manager.health_check()
        return jsonify({
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if db_healthy else 503
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# User management endpoints
@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        if not data or 'username' not in data:
            raise BadRequest('Username is required')
        
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            
            # Check if user already exists
            existing_user = user_repo.get_user_by_username(data['username'])
            if existing_user:
                return jsonify({'error': 'User already exists'}), 409
            
            # Create new user
            user = user_repo.create_user(
                username=data['username'],
                email=data.get('email'),
                data_sharing_consent=data.get('data_sharing_consent', False),
                learning_enabled=data.get('learning_enabled', True)
            )
            
            return jsonify({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            }), 201
    
    except Exception as e:
        logger.error(f"Create user error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information"""
    try:
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_user_by_id(user_id)
            
            if not user:
                raise NotFound('User not found')
            
            # Update last activity
            user_repo.update_user_activity(user_id)
            
            return jsonify({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'last_active': user.last_active.isoformat(),
                'learning_enabled': user.learning_enabled,
                'profile': {
                    'preferred_language': user.profile.preferred_language,
                    'communication_style': user.profile.communication_style,
                    'technical_level': user.profile.technical_level,
                    'interests': user.profile.interests,
                    'hobbies': user.profile.hobbies
                } if user.profile else None
            }), 200
    
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:user_id>/profile', methods=['PUT'])
def update_user_profile(user_id):
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Profile data is required')
        
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_user_by_id(user_id)
            
            if not user:
                raise NotFound('User not found')
            
            # Update profile fields
            profile = user.profile
            if profile:
                for field in ['preferred_language', 'communication_style', 'response_length_preference',
                             'technical_level', 'interests', 'hobbies', 'explanation_detail_level']:
                    if field in data:
                        setattr(profile, field, data[field])
                
                profile.updated_at = datetime.utcnow()
            
            return jsonify({'message': 'Profile updated successfully'}), 200
    
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({'error': str(e)}), 500


# Interaction endpoints
@app.route('/api/users/<int:user_id>/interactions', methods=['POST'])
def create_interaction(user_id):
    """Record a new user interaction"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            raise BadRequest('Interaction content is required')
        
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            interaction_repo = InteractionRepository(session)
            
            # Verify user exists
            user = user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFound('User not found')
            
            # Create interaction
            interaction = interaction_repo.create_interaction(
                user_id=user_id,
                interaction_type=data.get('type', InteractionType.MESSAGE.value),
                content=data['content'],
                context=data.get('context'),
                session_id=data.get('session_id'),
                source=data.get('source', 'api')
            )
            
            # Trigger learning if enabled
            if user.learning_enabled:
                # Process this interaction immediately for real-time learning
                learning_result = learning_engine.process_user_interactions(user_id, [interaction])
                
                # Store any new learned facts
                if learning_result.new_facts:
                    fact_repo = LearnedFactRepository(session)
                    for fact_data in learning_result.new_facts:
                        fact_repo.create_or_update_fact(**fact_data)
                
                # Mark interaction as processed
                interaction_repo.mark_interaction_processed(interaction.id)
            
            return jsonify({
                'interaction_id': interaction.id,
                'timestamp': interaction.timestamp.isoformat(),
                'learning_enabled': user.learning_enabled
            }), 201
    
    except Exception as e:
        logger.error(f"Create interaction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:user_id>/interactions', methods=['GET'])
def get_user_interactions(user_id):
    """Get user interactions"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        with db_manager.get_session() as session:
            interaction_repo = InteractionRepository(session)
            interactions = interaction_repo.get_user_interactions(user_id, limit, offset)
            
            return jsonify({
                'interactions': [{
                    'id': i.id,
                    'type': i.interaction_type,
                    'content': i.content,
                    'timestamp': i.timestamp.isoformat(),
                    'sentiment': i.sentiment,
                    'topics': i.topics,
                    'intent': i.intent
                } for i in interactions],
                'count': len(interactions)
            }), 200
    
    except Exception as e:
        logger.error(f"Get interactions error: {e}")
        return jsonify({'error': str(e)}), 500


# Learning endpoints
@app.route('/api/users/<int:user_id>/learn', methods=['POST'])
def trigger_learning(user_id):
    """Trigger learning process for a user"""
    try:
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            interaction_repo = InteractionRepository(session)
            fact_repo = LearnedFactRepository(session)
            
            # Get user
            user = user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFound('User not found')
            
            if not user.learning_enabled:
                return jsonify({'message': 'Learning is disabled for this user'}), 400
            
            # Get unprocessed interactions
            unprocessed = interaction_repo.get_unprocessed_interactions(user_id)
            
            if not unprocessed:
                return jsonify({'message': 'No new interactions to process'}), 200
            
            # Run learning engine
            result = learning_engine.process_user_interactions(user_id, unprocessed)
            
            # Store new facts
            for fact_data in result.new_facts:
                fact_repo.create_or_update_fact(**fact_data)
            
            # Mark interactions as processed
            for interaction in unprocessed:
                interaction_repo.mark_interaction_processed(interaction.id)
            
            return jsonify({
                'message': 'Learning completed',
                'processed_interactions': len(unprocessed),
                'new_facts': len(result.new_facts),
                'insights': len(result.insights),
                'processing_time_ms': result.processing_time_ms
            }), 200
    
    except Exception as e:
        logger.error(f"Learning trigger error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:user_id>/facts', methods=['GET'])
def get_learned_facts(user_id):
    """Get learned facts about a user"""
    try:
        category = request.args.get('category')
        
        with db_manager.get_session() as session:
            fact_repo = LearnedFactRepository(session)
            facts = fact_repo.get_user_facts(user_id, category)
            
            return jsonify({
                'facts': [{
                    'id': f.id,
                    'category': f.category,
                    'fact_type': f.fact_type,
                    'fact_key': f.fact_key,
                    'fact_value': f.fact_value,
                    'confidence_level': f.confidence_level,
                    'evidence_count': f.evidence_count,
                    'first_observed': f.first_observed.isoformat(),
                    'last_updated': f.last_updated.isoformat(),
                    'user_confirmed': f.user_confirmed,
                    'learning_method': f.learning_method
                } for f in facts],
                'count': len(facts)
            }), 200
    
    except Exception as e:
        logger.error(f"Get facts error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<int:user_id>/facts/<int:fact_id>/confirm', methods=['POST'])
def confirm_fact(user_id, fact_id):
    """Confirm or reject a learned fact"""
    try:
        data = request.get_json()
        confirmed = data.get('confirmed', True) if data else True
        
        with db_manager.get_session() as session:
            fact_repo = LearnedFactRepository(session)
            fact_repo.confirm_fact(fact_id, confirmed)
            
            return jsonify({
                'message': f'Fact {"confirmed" if confirmed else "rejected"}',
                'fact_id': fact_id
            }), 200
    
    except Exception as e:
        logger.error(f"Confirm fact error: {e}")
        return jsonify({'error': str(e)}), 500


# Analytics endpoints
@app.route('/api/users/<int:user_id>/analytics', methods=['GET'])
def get_user_analytics(user_id):
    """Get analytics and insights about a user"""
    try:
        with db_manager.get_session() as session:
            user_repo = UserRepository(session)
            interaction_repo = InteractionRepository(session)
            fact_repo = LearnedFactRepository(session)
            
            # Get user
            user = user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFound('User not found')
            
            # Get recent interactions for analysis
            recent_interactions = interaction_repo.get_user_interactions(user_id, limit=100)
            all_facts = fact_repo.get_user_facts(user_id)
            
            # Generate analytics
            analytics = {
                'user_summary': {
                    'total_interactions': len(recent_interactions),
                    'total_facts_learned': len(all_facts),
                    'member_since': user.created_at.isoformat(),
                    'last_active': user.last_active.isoformat()
                },
                'interaction_stats': {
                    'average_sentiment': sum(i.sentiment or 0 for i in recent_interactions) / max(len(recent_interactions), 1),
                    'most_common_intent': None,  # Would calculate this
                    'top_topics': []  # Would extract from interactions
                },
                'learning_progress': {
                    'facts_by_category': {},
                    'confidence_distribution': {},
                    'recent_learnings': []
                }
            }
            
            # Calculate facts by category
            for fact in all_facts:
                category = fact.category
                if category not in analytics['learning_progress']['facts_by_category']:
                    analytics['learning_progress']['facts_by_category'][category] = 0
                analytics['learning_progress']['facts_by_category'][category] += 1
            
            return jsonify(analytics), 200
    
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({'error': str(e)}), 500


# Frontend routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/user/<int:user_id>')
def user_dashboard(user_id):
    """User-specific dashboard"""
    return render_template('user_dashboard.html', user_id=user_id)


if __name__ == '__main__':
    # Initialize database if it doesn't exist
    try:
        if not db_manager.health_check():
            logger.info("Database not found, initializing...")
            from database import init_database
            init_database()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AI User Learning System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)