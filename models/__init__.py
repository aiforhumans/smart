"""
Data models for the AI User Learning System
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json

Base = declarative_base()


class InteractionType(Enum):
    """Types of user interactions"""
    MESSAGE = "message"
    PREFERENCE = "preference"
    FEEDBACK = "feedback"
    BEHAVIOR = "behavior"
    EXPLICIT = "explicit"  # User explicitly tells us something
    IMPLICIT = "implicit"  # We infer from behavior


class LearningConfidence(Enum):
    """Confidence levels for learned information"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"  # User confirmed


class User(Base):
    """User model storing basic user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Privacy settings
    data_sharing_consent = Column(Boolean, default=False)
    learning_enabled = Column(Boolean, default=True)
    retention_days = Column(Integer, default=365)  # How long to keep data
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    interactions = relationship("UserInteraction", back_populates="user")
    learned_facts = relationship("LearnedFact", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")


class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Basic demographics (optional)
    age_range = Column(String(20))  # e.g., "25-35"
    location = Column(String(100))
    occupation = Column(String(100))
    education_level = Column(String(50))
    
    # Communication preferences
    preferred_language = Column(String(10), default="en")
    communication_style = Column(String(50))  # formal, casual, technical, etc.
    response_length_preference = Column(String(20))  # brief, detailed, comprehensive
    
    # Interests and hobbies (stored as JSON)
    interests = Column(JSON)
    hobbies = Column(JSON)
    
    # AI interaction preferences
    explanation_detail_level = Column(String(20), default="medium")  # low, medium, high
    prefers_examples = Column(Boolean, default=True)
    technical_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced, expert
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")


class UserInteraction(Base):
    """Store all user interactions for learning"""
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    interaction_type = Column(String(20), nullable=False)  # InteractionType enum
    content = Column(Text)  # The actual interaction content
    context = Column(JSON)  # Additional context data
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String(100))  # Group related interactions
    source = Column(String(50))  # web, api, mobile, etc.
    
    # Analysis results
    sentiment = Column(Float)  # -1 to 1
    topics = Column(JSON)  # Extracted topics/keywords
    intent = Column(String(100))  # Classified intent
    processed = Column(Boolean, default=False)  # Has this been analyzed?
    
    # Relationships
    user = relationship("User", back_populates="interactions")


class LearnedFact(Base):
    """Facts learned about the user"""
    __tablename__ = 'learned_facts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    category = Column(String(50), nullable=False)  # preference, skill, interest, behavior, etc.
    fact_type = Column(String(50), nullable=False)  # specific type within category
    fact_key = Column(String(100), nullable=False)  # unique identifier for this fact
    fact_value = Column(Text)  # the actual learned information
    
    # Learning metadata
    confidence_level = Column(String(20), default="medium")  # LearningConfidence enum
    evidence_count = Column(Integer, default=1)  # How many interactions support this
    first_observed = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Source tracking
    source_interactions = Column(JSON)  # List of interaction IDs that led to this fact
    learning_method = Column(String(50))  # explicit, pattern_analysis, nlp_extraction, etc.
    
    # Validation
    user_confirmed = Column(Boolean, default=False)
    user_rejected = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="learned_facts")


class UserPreference(Base):
    """Specific user preferences and settings"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    category = Column(String(50), nullable=False)  # ui, content, behavior, etc.
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text)
    
    # Metadata
    is_explicit = Column(Boolean, default=False)  # User explicitly set this
    confidence = Column(Float, default=1.0)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class LearningSession(Base):
    """Track learning sessions and their outcomes"""
    __tablename__ = 'learning_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    
    # What was learned
    facts_learned = Column(Integer, default=0)
    facts_updated = Column(Integer, default=0)
    facts_confirmed = Column(Integer, default=0)
    facts_rejected = Column(Integer, default=0)
    
    # Processing details
    interactions_processed = Column(Integer, default=0)
    processing_time_ms = Column(Integer)
    
    # Results
    learning_summary = Column(JSON)  # Summary of what was learned
    errors = Column(JSON)  # Any errors encountered


@dataclass
class UserInsight:
    """Data class for representing insights about a user"""
    category: str
    insight: str
    confidence: float
    evidence: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'insight': self.insight,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class LearningResult:
    """Result of a learning operation"""
    user_id: int
    new_facts: List[Dict[str, Any]]
    updated_facts: List[Dict[str, Any]]
    insights: List[UserInsight]
    processing_time_ms: int
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'new_facts': self.new_facts,
            'updated_facts': self.updated_facts,
            'insights': [insight.to_dict() for insight in self.insights],
            'processing_time_ms': self.processing_time_ms,
            'errors': self.errors
        }