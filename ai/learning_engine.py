"""
AI Learning Engine for analyzing user interactions and extracting insights
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import Counter, defaultdict
import string

from models import UserInteraction, LearnedFact, UserInsight, LearningResult, InteractionType, LearningConfidence

# Configure logging
logger = logging.getLogger(__name__)


"""
AI Learning Engine for analyzing user interactions and extracting insights
Simplified version without heavy ML dependencies
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import Counter, defaultdict
import string

from models import UserInteraction, LearnedFact, UserInsight, LearningResult, InteractionType, LearningConfidence

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Statistics from processing user interactions"""
    interactions_processed: int = 0
    facts_learned: int = 0
    facts_updated: int = 0
    insights_generated: int = 0
    processing_time_ms: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class SimpleTextAnalyzer:
    """Simplified text analysis without external dependencies"""
    
    def __init__(self):
        # Basic stop words (simplified list)
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'i', 'you', 'me', 'we', 'they',
            'this', 'that', 'these', 'those', 'am', 'can', 'could', 'should',
            'would', 'have', 'had', 'has'
        }
        
        # Sentiment words (basic positive/negative indicators)
        self.positive_words = {
            'love', 'like', 'enjoy', 'amazing', 'awesome', 'great', 'fantastic',
            'wonderful', 'excellent', 'perfect', 'good', 'best', 'beautiful',
            'happy', 'pleased', 'excited', 'thrilled', 'appreciate', 'thanks'
        }
        
        self.negative_words = {
            'hate', 'dislike', 'awful', 'terrible', 'horrible', 'bad', 'worst',
            'annoying', 'frustrated', 'angry', 'disappointed', 'confused',
            'difficult', 'problem', 'issue', 'wrong', 'error', 'fail'
        }
        
        # Common patterns for preference extraction
        self.preference_patterns = {
            'likes': [
                r"i (really |absolutely |totally )?like ([^.!?]+)",
                r"i (love|enjoy|prefer|am into) ([^.!?]+)",
                r"([^.!?]+) (is|are) (great|awesome|amazing|wonderful|fantastic)",
                r"i'm (really )?interested in ([^.!?]+)",
                r"i'm a (big )?fan of ([^.!?]+)"
            ],
            'dislikes': [
                r"i (really |absolutely |totally )?(hate|dislike|don't like) ([^.!?]+)",
                r"i'm not (really |a big )?fan of ([^.!?]+)",
                r"([^.!?]+) (is|are) (terrible|awful|bad|horrible|annoying)",
                r"i can't stand ([^.!?]+)"
            ],
            'needs': [
                r"i need (help with |to learn about |to understand )?([^.!?]+)",
                r"i want to (learn|understand|know about) ([^.!?]+)",
                r"can you (help me with|teach me about|explain) ([^.!?]+)",
                r"i'm looking for ([^.!?]+)"
            ],
            'skills': [
                r"i (know|understand|am good at|can) ([^.!?]+)",
                r"i'm (an expert in|experienced with|familiar with) ([^.!?]+)",
                r"i have experience (with|in) ([^.!?]+)",
                r"i've been (working with|using|doing) ([^.!?]+)"
            ]
        }
        
        # Communication style indicators
        self.style_indicators = {
            'formal': ['please', 'thank you', 'could you', 'would you', 'sir', 'madam', 'kindly'],
            'casual': ['hey', 'hi', 'cool', 'awesome', 'yeah', 'nah', 'gonna', 'wanna', 'sup'],
            'technical': ['algorithm', 'function', 'variable', 'database', 'api', 'framework', 'code'],
            'friendly': ['thanks', 'appreciate', 'great', 'wonderful', 'excited', '!', 'amazing']
        }
    
    def simple_tokenize(self, text: str) -> List[str]:
        """Simple word tokenization"""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Split on whitespace and filter empty strings
        return [token for token in text.split() if token]
    
    def analyze_sentiment(self, text: str) -> float:
        """Simple sentiment analysis (-1 to 1)"""
        try:
            tokens = self.simple_tokenize(text)
            positive_count = sum(1 for token in tokens if token in self.positive_words)
            negative_count = sum(1 for token in tokens if token in self.negative_words)
            
            total_sentiment_words = positive_count + negative_count
            if total_sentiment_words == 0:
                return 0.0
            
            # Simple sentiment score
            sentiment = (positive_count - negative_count) / max(len(tokens), 1)
            return max(-1.0, min(1.0, sentiment * 2))  # Scale and clamp
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return 0.0
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract key topics/keywords from text"""
        try:
            tokens = self.simple_tokenize(text)
            
            # Remove stop words and short tokens
            filtered_tokens = [
                token for token in tokens 
                if token not in self.stop_words and len(token) > 2
            ]
            
            # Get word frequencies
            word_freq = Counter(filtered_tokens)
            
            # Return top topics
            return [word for word, freq in word_freq.most_common(10)]
        
        except Exception as e:
            logger.error(f"Topic extraction error: {e}")
            return []
    
    def extract_preferences(self, text: str) -> Dict[str, List[str]]:
        """Extract preferences from text using pattern matching"""
        preferences = defaultdict(list)
        text = text.lower()
        
        try:
            for pref_type, patterns in self.preference_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        groups = match.groups()
                        if groups:
                            preference = groups[-1].strip()
                            if preference and len(preference) > 2:
                                preferences[pref_type].append(preference)
        
        except Exception as e:
            logger.error(f"Preference extraction error: {e}")
        
        return dict(preferences)
    
    def analyze_communication_style(self, text: str) -> Dict[str, float]:
        """Analyze communication style from text"""
        text = text.lower()
        style_scores = {}
        
        try:
            total_words = len(self.simple_tokenize(text))
            if total_words == 0:
                return style_scores
            
            for style, indicators in self.style_indicators.items():
                score = sum(1 for indicator in indicators if indicator in text)
                style_scores[style] = score / total_words
        
        except Exception as e:
            logger.error(f"Communication style analysis error: {e}")
        
        return style_scores
    
    def classify_intent(self, text: str) -> str:
        """Classify the intent of user message"""
        text = text.lower()
        
        # Simple rule-based intent classification
        if any(word in text for word in ['help', 'how', 'what', 'explain', 'tell me']):
            return 'help_request'
        elif any(word in text for word in ['like', 'love', 'prefer', 'enjoy']):
            return 'preference_expression'
        elif any(word in text for word in ['thank', 'thanks', 'appreciate']):
            return 'gratitude'
        elif any(word in text for word in ['hello', 'hi', 'hey', 'good morning']):
            return 'greeting'
        elif '?' in text:
            return 'question'
        else:
            return 'statement'


class SimplePatternAnalyzer:
    """Simplified pattern analyzer without pandas dependency"""
    
    def __init__(self):
        self.min_pattern_count = 3
    
    def analyze_interaction_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze patterns in user interactions"""
        patterns = {}
        
        if not interactions:
            return patterns
        
        try:
            # Analyze time patterns
            patterns['active_hours'] = self._analyze_time_patterns(interactions)
            patterns['interaction_frequency'] = self._analyze_frequency_patterns(interactions)
            patterns['content_patterns'] = self._analyze_content_patterns(interactions)
            patterns['sentiment_trends'] = self._analyze_sentiment_trends(interactions)
            patterns['topic_preferences'] = self._analyze_topic_patterns(interactions)
        
        except Exception as e:
            logger.error(f"Pattern analysis error: {e}")
        
        return patterns
    
    def _analyze_time_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze when user is most active"""
        hours = [interaction.timestamp.hour for interaction in interactions]
        days = [interaction.timestamp.weekday() for interaction in interactions]
        
        hour_counts = Counter(hours)
        day_counts = Counter(days)
        
        return {
            'most_active_hour': hour_counts.most_common(1)[0][0] if hour_counts else None,
            'most_active_day': day_counts.most_common(1)[0][0] if day_counts else None,
            'activity_distribution': dict(hour_counts)
        }
    
    def _analyze_frequency_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze interaction frequency patterns"""
        if len(interactions) < 2:
            return {'interaction_count': len(interactions)}
        
        # Sort by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)
        
        # Calculate time differences
        time_diffs = []
        for i in range(1, len(sorted_interactions)):
            diff = sorted_interactions[i].timestamp - sorted_interactions[i-1].timestamp
            time_diffs.append(diff.total_seconds() / 3600)  # Convert to hours
        
        avg_time_between = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        
        date_range = (sorted_interactions[-1].timestamp - sorted_interactions[0].timestamp).days
        
        return {
            'average_time_between_interactions_hours': avg_time_between,
            'interaction_count': len(interactions),
            'date_range_days': date_range
        }
    
    def _analyze_content_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze content patterns"""
        content_lengths = [len(interaction.content or '') for interaction in interactions]
        interaction_types = [interaction.interaction_type for interaction in interactions]
        
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        type_counts = Counter(interaction_types)
        
        # Simple trend analysis
        if len(content_lengths) > 5:
            first_half = content_lengths[:len(content_lengths)//2]
            second_half = content_lengths[len(content_lengths)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            trend = 'increasing' if second_avg > first_avg * 1.1 else 'decreasing' if second_avg < first_avg * 0.9 else 'stable'
        else:
            trend = 'stable'
        
        return {
            'average_content_length': avg_length,
            'content_length_trend': trend,
            'interaction_types': dict(type_counts)
        }
    
    def _analyze_sentiment_trends(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze sentiment trends"""
        sentiments = [interaction.sentiment or 0 for interaction in interactions]
        
        if not sentiments:
            return {'average_sentiment': 0, 'sentiment_trend': 'stable'}
        
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Simple trend analysis
        if len(sentiments) > 5:
            first_half = sentiments[:len(sentiments)//2]
            second_half = sentiments[len(sentiments)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg + 0.1:
                trend = 'improving'
            elif second_avg < first_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'average_sentiment': avg_sentiment,
            'sentiment_trend': trend
        }
    
    def _analyze_topic_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze topic patterns"""
        all_topics = []
        for interaction in interactions:
            if interaction.topics:
                all_topics.extend(interaction.topics)
        
        topic_counts = Counter(all_topics)
        
        return {
            'top_topics': dict(topic_counts.most_common(10)),
            'topic_diversity': len(set(all_topics))
        }


class LearningEngine:
    """Main learning engine that coordinates all analysis components"""
    
    def __init__(self):
        self.text_analyzer = SimpleTextAnalyzer()
        self.pattern_analyzer = SimplePatternAnalyzer()
    
    def process_user_interactions(self, user_id: int, interactions: List[UserInteraction]) -> LearningResult:
        """Process user interactions and extract learning insights"""
        start_time = datetime.utcnow()
        stats = ProcessingStats()
        new_facts = []
        updated_facts = []
        insights = []
        
        try:
            # Analyze each interaction
            for interaction in interactions:
                if not interaction.processed:
                    self._analyze_single_interaction(interaction, stats)
            
            # Analyze patterns across all interactions
            patterns = self.pattern_analyzer.analyze_interaction_patterns(interactions)
            
            # Generate facts from patterns
            pattern_facts = self._generate_facts_from_patterns(user_id, patterns)
            new_facts.extend(pattern_facts)
            
            # Generate insights
            insights = self._generate_insights(user_id, interactions, patterns)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            stats.processing_time_ms = int(processing_time)
            stats.interactions_processed = len(interactions)
            stats.facts_learned = len(new_facts)
            stats.insights_generated = len(insights)
        
        except Exception as e:
            logger.error(f"Learning engine error: {e}")
            stats.errors.append(str(e))
        
        return LearningResult(
            user_id=user_id,
            new_facts=[fact.__dict__ if hasattr(fact, '__dict__') else fact for fact in new_facts],
            updated_facts=updated_facts,
            insights=insights,
            processing_time_ms=stats.processing_time_ms,
            errors=stats.errors
        )
    
    def _analyze_single_interaction(self, interaction: UserInteraction, stats: ProcessingStats):
        """Analyze a single interaction and update its metadata"""
        try:
            content = interaction.content or ''
            
            # Sentiment analysis
            if not interaction.sentiment:
                interaction.sentiment = self.text_analyzer.analyze_sentiment(content)
            
            # Topic extraction
            if not interaction.topics:
                interaction.topics = self.text_analyzer.extract_topics(content)
            
            # Intent classification
            if not interaction.intent:
                interaction.intent = self.text_analyzer.classify_intent(content)
        
        except Exception as e:
            logger.error(f"Single interaction analysis error: {e}")
            stats.errors.append(f"Interaction {interaction.id}: {str(e)}")
    
    def _generate_facts_from_patterns(self, user_id: int, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate learned facts from identified patterns"""
        facts = []
        
        try:
            # Time preference facts
            if 'active_hours' in patterns and patterns['active_hours'].get('most_active_hour') is not None:
                facts.append({
                    'user_id': user_id,
                    'category': 'behavior',
                    'fact_type': 'time_preference',
                    'fact_key': 'most_active_hour',
                    'fact_value': str(patterns['active_hours']['most_active_hour']),
                    'confidence_level': LearningConfidence.MEDIUM.value,
                    'learning_method': 'pattern_analysis'
                })
            
            # Communication style facts
            if 'content_patterns' in patterns:
                avg_length = patterns['content_patterns'].get('average_content_length', 0)
                if avg_length > 0:
                    length_preference = 'detailed' if avg_length > 100 else 'brief' if avg_length < 50 else 'moderate'
                    facts.append({
                        'user_id': user_id,
                        'category': 'communication',
                        'fact_type': 'message_length_preference',
                        'fact_key': 'preferred_response_length',
                        'fact_value': length_preference,
                        'confidence_level': LearningConfidence.MEDIUM.value,
                        'learning_method': 'pattern_analysis'
                    })
            
            # Topic interest facts
            if 'topic_preferences' in patterns and patterns['topic_preferences'].get('top_topics'):
                top_topics = patterns['topic_preferences']['top_topics']
                for topic, count in list(top_topics.items())[:5]:  # Top 5 topics
                    if count >= 3:  # Minimum threshold
                        facts.append({
                            'user_id': user_id,
                            'category': 'interests',
                            'fact_type': 'topic_interest',
                            'fact_key': f'interest_{topic}',
                            'fact_value': f'Shows strong interest in {topic}',
                            'confidence_level': LearningConfidence.HIGH.value if count > 5 else LearningConfidence.MEDIUM.value,
                            'evidence_count': count,
                            'learning_method': 'topic_analysis'
                        })
        
        except Exception as e:
            logger.error(f"Fact generation error: {e}")
        
        return facts
    
    def _generate_insights(self, user_id: int, interactions: List[UserInteraction], 
                          patterns: Dict[str, Any]) -> List[UserInsight]:
        """Generate insights about the user"""
        insights = []
        
        try:
            # Engagement insight
            if patterns.get('interaction_frequency', {}).get('interaction_count', 0) > 10:
                insights.append(UserInsight(
                    category='engagement',
                    insight='User is highly engaged with frequent interactions',
                    confidence=0.8,
                    evidence=[f"Had {patterns['interaction_frequency']['interaction_count']} interactions"]
                ))
            
            # Communication style insight
            recent_interactions = interactions[-10:] if len(interactions) > 10 else interactions
            if recent_interactions:
                avg_sentiment = sum(i.sentiment or 0 for i in recent_interactions) / len(recent_interactions)
                if avg_sentiment > 0.1:
                    insights.append(UserInsight(
                        category='communication',
                        insight='User generally communicates with positive sentiment',
                        confidence=0.7,
                        evidence=[f"Average sentiment: {avg_sentiment:.2f}"]
                    ))
            
            # Learning preference insight
            help_requests = [i for i in interactions if i.intent == 'help_request']
            if len(help_requests) > 3:
                insights.append(UserInsight(
                    category='learning',
                    insight='User prefers learning through asking questions',
                    confidence=0.6,
                    evidence=[f"Made {len(help_requests)} help requests"]
                ))
        
        except Exception as e:
            logger.error(f"Insight generation error: {e}")
        
        return insights


# For backwards compatibility
TextAnalyzer = SimpleTextAnalyzer
PatternAnalyzer = SimplePatternAnalyzer