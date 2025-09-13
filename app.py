"""
Main Flask application for the AI User Learning System
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
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

# Enable CORS for cross-origin requests
CORS(app)

# Initialize learning engine
learning_engine = LearningEngine()


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

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