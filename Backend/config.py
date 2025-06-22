"""
Configuration module for PII redaction API
"""

import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('config.env')

class Config:
    """Configuration class for the PII redaction API"""
    
    # Ollama configuration
    MODEL_NAME = os.getenv('MODEL_NAME', 'mistral')
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # API configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't', 'yes')
    
    # CORS configuration
    ALLOWED_ORIGINS_RAW = os.getenv('ALLOWED_ORIGINS', '["http://localhost:3000", "http://127.0.0.1:3000"]')
    
    # PII Detection configuration
    HYBRID_MODE_ENABLED = os.getenv('HYBRID_MODE_ENABLED', 'True').lower() in ('true', '1', 't', 'yes')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # File upload configuration
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '10485760'))  # 10MB default
    MAX_FILES_PER_REQUEST = int(os.getenv('MAX_FILES_PER_REQUEST', '5'))
    
    # Directory configuration
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'outputs')
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Parse allowed origins from environment variable"""
        try:
            return json.loads(cls.ALLOWED_ORIGINS_RAW)
        except json.JSONDecodeError:
            # Default to localhost if parsing fails
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @classmethod
    def validate(cls) -> Optional[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Validate directories
        for dir_name in [cls.UPLOAD_DIR, cls.OUTPUT_DIR]:
            if not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name, exist_ok=True)
                except Exception as e:
                    issues.append(f"Failed to create directory {dir_name}: {str(e)}")
        
        # Validate Ollama URL format
        if not cls.OLLAMA_BASE_URL.startswith(('http://', 'https://')):
            issues.append(f"Invalid OLLAMA_BASE_URL format: {cls.OLLAMA_BASE_URL}")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL not in valid_log_levels:
            issues.append(f"Invalid LOG_LEVEL: {cls.LOG_LEVEL}. Valid options: {', '.join(valid_log_levels)}")
        
        # Return issues or None if no issues
        return '; '.join(issues) if issues else None