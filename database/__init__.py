"""
Database configuration and utilities for the AI User Learning System
"""

import os
import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator, Optional
from models import Base, User, UserProfile, UserInteraction, LearnedFact, UserPreference, LearningSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///user_learning.db')
        self.echo = os.getenv('DATABASE_ECHO', 'False').lower() == 'true'
        self.pool_size = int(os.getenv('DATABASE_POOL_SIZE', '5'))
        self.max_overflow = int(os.getenv('DATABASE_MAX_OVERFLOW', '10'))


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database engine and session factory"""
        try:
            # Create engine
            if self.config.database_url.startswith('sqlite'):
                # SQLite specific configuration
                self.engine = create_engine(
                    self.config.database_url,
                    echo=self.config.echo,
                    poolclass=StaticPool,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 30
                    }
                )
                
                # Enable foreign keys for SQLite
                @event.listens_for(self.engine, "connect")
                def set_sqlite_pragma(dbapi_connection, connection_record):
                    cursor = dbapi_connection.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()
                    
            else:
                # PostgreSQL or other databases
                self.engine = create_engine(
                    self.config.database_url,
                    echo=self.config.echo,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database initialized: {self.config.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """Get a database session without context manager (manual cleanup required)"""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check if database is accessible"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


def get_db_session() -> Generator[Session, None, None]:
    """Dependency injection for database sessions"""
    with db_manager.get_session() as session:
        yield session


def init_database():
    """Initialize the database with tables"""
    db_manager.create_tables()


def reset_database():
    """Reset the database (drop and recreate tables)"""
    db_manager.drop_tables()
    db_manager.create_tables()


class UserRepository:
    """Repository pattern for User operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_user(self, username: str, email: Optional[str] = None, **kwargs) -> User:
        """Create a new user"""
        user = User(username=username, email=email, **kwargs)
        self.session.add(user)
        self.session.flush()  # Get the ID without committing
        
        # Create default profile
        profile = UserProfile(user_id=user.id)
        self.session.add(profile)
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.session.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.session.query(User).filter(User.email == email).first()
    
    def update_user_activity(self, user_id: int):
        """Update user's last activity timestamp"""
        from datetime import datetime
        user = self.get_user_by_id(user_id)
        if user:
            user.last_active = datetime.utcnow()
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user and all associated data"""
        user = self.get_user_by_id(user_id)
        if user:
            self.session.delete(user)
            return True
        return False


class InteractionRepository:
    """Repository pattern for UserInteraction operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_interaction(self, user_id: int, interaction_type: str, content: str, **kwargs) -> UserInteraction:
        """Create a new user interaction"""
        interaction = UserInteraction(
            user_id=user_id,
            interaction_type=interaction_type,
            content=content,
            **kwargs
        )
        self.session.add(interaction)
        return interaction
    
    def get_user_interactions(self, user_id: int, limit: int = 100, offset: int = 0) -> list[UserInteraction]:
        """Get user interactions with pagination"""
        return (self.session.query(UserInteraction)
                .filter(UserInteraction.user_id == user_id)
                .order_by(UserInteraction.timestamp.desc())
                .limit(limit)
                .offset(offset)
                .all())
    
    def get_unprocessed_interactions(self, user_id: Optional[int] = None) -> list[UserInteraction]:
        """Get interactions that haven't been processed for learning"""
        query = self.session.query(UserInteraction).filter(UserInteraction.processed == False)
        if user_id:
            query = query.filter(UserInteraction.user_id == user_id)
        return query.all()
    
    def mark_interaction_processed(self, interaction_id: int):
        """Mark an interaction as processed"""
        interaction = self.session.query(UserInteraction).filter(UserInteraction.id == interaction_id).first()
        if interaction:
            interaction.processed = True


class LearnedFactRepository:
    """Repository pattern for LearnedFact operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_or_update_fact(self, user_id: int, category: str, fact_type: str, 
                             fact_key: str, fact_value: str, **kwargs) -> LearnedFact:
        """Create a new fact or update existing one"""
        existing_fact = (self.session.query(LearnedFact)
                        .filter(LearnedFact.user_id == user_id)
                        .filter(LearnedFact.category == category)
                        .filter(LearnedFact.fact_key == fact_key)
                        .first())
        
        if existing_fact:
            # Update existing fact
            existing_fact.fact_value = fact_value
            existing_fact.evidence_count += kwargs.get('evidence_count', 1)
            from datetime import datetime
            existing_fact.last_updated = datetime.utcnow()
            return existing_fact
        else:
            # Create new fact
            fact = LearnedFact(
                user_id=user_id,
                category=category,
                fact_type=fact_type,
                fact_key=fact_key,
                fact_value=fact_value,
                **kwargs
            )
            self.session.add(fact)
            return fact
    
    def get_user_facts(self, user_id: int, category: Optional[str] = None) -> list[LearnedFact]:
        """Get learned facts for a user"""
        query = self.session.query(LearnedFact).filter(LearnedFact.user_id == user_id)
        if category:
            query = query.filter(LearnedFact.category == category)
        return query.order_by(LearnedFact.confidence_level.desc(), LearnedFact.evidence_count.desc()).all()
    
    def confirm_fact(self, fact_id: int, confirmed: bool = True):
        """Mark a fact as confirmed or rejected by the user"""
        fact = self.session.query(LearnedFact).filter(LearnedFact.id == fact_id).first()
        if fact:
            fact.user_confirmed = confirmed
            fact.user_rejected = not confirmed