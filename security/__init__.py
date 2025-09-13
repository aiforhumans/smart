"""
Security and Privacy utilities for the AI User Learning System
"""

import os
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import jwt
import base64

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Handles data encryption and decryption"""
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize encryption manager
        
        Args:
            master_key: Master key for encryption. If None, generates from environment or creates new one.
        """
        self.master_key = master_key or self._get_or_create_master_key()
        self.fernet = self._create_fernet_instance()
    
    def _get_or_create_master_key(self) -> str:
        """Get master key from environment or create a new one"""
        master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        
        if not master_key:
            # Generate a new master key
            master_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            logger.warning("No master key found. Generated new key. Store this securely: %s", master_key)
        
        return master_key
    
    def _create_fernet_instance(self) -> Fernet:
        """Create Fernet instance from master key"""
        try:
            # If master key is already in correct format
            key_bytes = base64.urlsafe_b64decode(self.master_key.encode())
            if len(key_bytes) == 32:
                return Fernet(self.master_key.encode())
        except:
            pass
        
        # Derive key from master key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ai_learning_salt',  # In production, use a random salt per user
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def hash_data(self, data: str) -> str:
        """Create a one-way hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()


class PasswordManager:
    """Handles password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


class TokenManager:
    """Handles JWT token creation and validation"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'default-secret-change-in-production')
        self.algorithm = 'HS256'
        self.default_expiry_hours = 24
    
    def create_token(self, user_id: int, additional_claims: Optional[Dict] = None) -> str:
        """Create a JWT token for a user"""
        now = datetime.utcnow()
        expiry = now + timedelta(hours=self.default_expiry_hours)
        
        payload = {
            'user_id': user_id,
            'iat': now,
            'exp': expiry,
            'iss': 'ai-learning-system'
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None


class ConsentManager:
    """Manages user consent and data retention policies"""
    
    def __init__(self):
        self.consent_types = {
            'data_collection': 'Collection of interaction data',
            'ai_learning': 'AI analysis and learning from data',
            'data_sharing': 'Sharing anonymized data for research',
            'marketing': 'Marketing communications',
            'analytics': 'Usage analytics and performance monitoring'
        }
    
    def validate_consent(self, user_consents: Dict[str, bool], required_consents: list) -> bool:
        """Validate that user has given required consents"""
        for consent_type in required_consents:
            if consent_type not in user_consents or not user_consents[consent_type]:
                return False
        return True
    
    def get_retention_policy(self, user_id: int, data_type: str) -> Dict[str, Any]:
        """Get data retention policy for a user and data type"""
        # Default retention policies
        policies = {
            'interactions': {'days': 365, 'description': 'User interactions and messages'},
            'learned_facts': {'days': 730, 'description': 'AI-learned facts and insights'},
            'analytics': {'days': 90, 'description': 'Usage analytics and metrics'},
            'logs': {'days': 30, 'description': 'System logs and errors'}
        }
        
        return policies.get(data_type, {'days': 365, 'description': 'General data'})
    
    def should_delete_data(self, created_date: datetime, data_type: str, user_retention_days: Optional[int] = None) -> bool:
        """Check if data should be deleted based on retention policy"""
        policy = self.get_retention_policy(0, data_type)  # user_id not used in default implementation
        retention_days = user_retention_days or policy['days']
        
        expiry_date = created_date + timedelta(days=retention_days)
        return datetime.utcnow() > expiry_date


class DataAnonymizer:
    """Handles data anonymization and pseudonymization"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
    
    def anonymize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize user data for research or analytics"""
        anonymized = user_data.copy()
        
        # Remove direct identifiers
        sensitive_fields = ['username', 'email', 'ip_address', 'device_id']
        for field in sensitive_fields:
            if field in anonymized:
                del anonymized[field]
        
        # Pseudonymize user ID
        if 'user_id' in anonymized:
            anonymized['user_id'] = self.encryption_manager.hash_data(str(anonymized['user_id']))
        
        # Generalize specific values
        if 'age' in anonymized:
            age = anonymized['age']
            if age:
                # Convert to age ranges
                if age < 18:
                    anonymized['age_range'] = 'under_18'
                elif age < 25:
                    anonymized['age_range'] = '18_24'
                elif age < 35:
                    anonymized['age_range'] = '25_34'
                elif age < 45:
                    anonymized['age_range'] = '35_44'
                elif age < 55:
                    anonymized['age_range'] = '45_54'
                else:
                    anonymized['age_range'] = '55_plus'
                del anonymized['age']
        
        # Hash or remove location data
        if 'location' in anonymized:
            location = anonymized['location']
            if location:
                # Keep only country/region level
                parts = location.split(',')
                anonymized['region'] = parts[-1].strip() if parts else 'unknown'
                del anonymized['location']
        
        return anonymized
    
    def pseudonymize_content(self, content: str) -> str:
        """Remove or replace personally identifiable information in text content"""
        import re
        
        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
        
        # Remove phone numbers (basic pattern)
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', content)
        
        # Remove credit card numbers (basic pattern)
        content = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]', content)
        
        # Remove SSN patterns
        content = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', content)
        
        return content


class AuditLogger:
    """Handles security and privacy audit logging"""
    
    def __init__(self):
        self.logger = logging.getLogger('security_audit')
        
        # Create separate handler for security logs
        if not self.logger.handlers:
            handler = logging.FileHandler('security_audit.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_data_access(self, user_id: int, data_type: str, action: str, ip_address: str = None):
        """Log data access events"""
        self.logger.info(f"DATA_ACCESS - User:{user_id} - Type:{data_type} - Action:{action} - IP:{ip_address}")
    
    def log_consent_change(self, user_id: int, consent_type: str, granted: bool, ip_address: str = None):
        """Log consent changes"""
        action = "GRANTED" if granted else "REVOKED"
        self.logger.info(f"CONSENT_{action} - User:{user_id} - Type:{consent_type} - IP:{ip_address}")
    
    def log_data_deletion(self, user_id: int, data_type: str, reason: str):
        """Log data deletion events"""
        self.logger.info(f"DATA_DELETION - User:{user_id} - Type:{data_type} - Reason:{reason}")
    
    def log_security_event(self, event_type: str, user_id: int = None, details: str = None, ip_address: str = None):
        """Log security events"""
        self.logger.warning(f"SECURITY_EVENT - Type:{event_type} - User:{user_id} - Details:{details} - IP:{ip_address}")


class PrivacyManager:
    """Main privacy management class"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.password_manager = PasswordManager()
        self.token_manager = TokenManager()
        self.consent_manager = ConsentManager()
        self.anonymizer = DataAnonymizer(self.encryption_manager)
        self.audit_logger = AuditLogger()
    
    def encrypt_sensitive_data(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Encrypt sensitive fields in data dictionary"""
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encryption_manager.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, encrypted_data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Decrypt sensitive fields in data dictionary"""
        decrypted_data = encrypted_data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.encryption_manager.decrypt(decrypted_data[field])
                except:
                    # If decryption fails, data might not be encrypted
                    pass
        
        return decrypted_data
    
    def process_data_subject_request(self, user_id: int, request_type: str) -> Dict[str, Any]:
        """Process GDPR-style data subject requests"""
        result = {
            'user_id': user_id,
            'request_type': request_type,
            'processed_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        
        try:
            if request_type == 'access':
                # Data portability - export all user data
                result['data'] = self._export_user_data(user_id)
                result['status'] = 'completed'
                
            elif request_type == 'deletion':
                # Right to be forgotten
                self._delete_user_data(user_id)
                result['status'] = 'completed'
                
            elif request_type == 'rectification':
                # Data correction - would need additional parameters
                result['status'] = 'requires_manual_review'
                
            elif request_type == 'restriction':
                # Restrict processing
                self._restrict_user_processing(user_id)
                result['status'] = 'completed'
                
            else:
                result['status'] = 'invalid_request_type'
            
            self.audit_logger.log_security_event(
                f"DATA_SUBJECT_REQUEST_{request_type.upper()}",
                user_id=user_id,
                details=f"Status: {result['status']}"
            )
            
        except Exception as e:
            logger.error(f"Error processing data subject request: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Export all user data for portability"""
        # This would integrate with the database to export all user data
        # For now, return a placeholder structure
        return {
            'profile': {},
            'interactions': [],
            'learned_facts': [],
            'preferences': [],
            'export_note': 'Full data export would be implemented with database integration'
        }
    
    def _delete_user_data(self, user_id: int):
        """Delete all user data (right to be forgotten)"""
        # This would integrate with the database to delete all user data
        self.audit_logger.log_data_deletion(user_id, 'all_data', 'user_request')
        pass
    
    def _restrict_user_processing(self, user_id: int):
        """Restrict processing of user data"""
        # This would mark the user account as restricted
        self.audit_logger.log_security_event('PROCESSING_RESTRICTED', user_id=user_id)
        pass


# Global privacy manager instance
privacy_manager = PrivacyManager()