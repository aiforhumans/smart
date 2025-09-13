"""
Utility functions for the AI User Learning System
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from functools import wraps
import hashlib
import secrets


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup application logging"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler (optional)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def safe_json_serialize(obj: Any) -> str:
    """Safely serialize objects to JSON"""
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    try:
        return json.dumps(obj, default=json_serializer, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Serialization failed: {str(e)}"})


def validate_user_input(input_data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
    """Validate user input data"""
    errors = []
    
    # Check required fields
    for field in required_fields:
        if field not in input_data or input_data[field] is None:
            errors.append(f"Missing required field: {field}")
        elif isinstance(input_data[field], str) and not input_data[field].strip():
            errors.append(f"Field '{field}' cannot be empty")
    
    # Additional validation
    if 'email' in input_data and input_data['email']:
        email = input_data['email']
        if '@' not in email or '.' not in email.split('@')[-1]:
            errors.append("Invalid email format")
    
    if 'username' in input_data and input_data['username']:
        username = input_data['username']
        if len(username) < 3:
            errors.append("Username must be at least 3 characters")
        if not username.replace('_', '').replace('-', '').isalnum():
            errors.append("Username can only contain letters, numbers, hyphens, and underscores")
    
    return len(errors) == 0, errors


def generate_session_id() -> str:
    """Generate a secure session ID"""
    return secrets.token_urlsafe(32)


def hash_text(text: str, salt: Optional[str] = None) -> str:
    """Hash text with optional salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    combined = f"{text}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()


def chunks(lst: List, chunk_size: int):
    """Split list into chunks of specified size"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_len = 255 - len(ext)
        filename = name[:max_name_len] + ext
    
    return filename or 'unnamed_file'


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on exception"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    if current_delay > 0:
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            return None
        return wrapper
    return decorator


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logging.info(f"{self.name} completed in {format_duration(duration)}")
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None