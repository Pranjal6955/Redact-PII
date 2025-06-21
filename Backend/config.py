import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("config.env")


class Config:
    """Application configuration"""
    
    # Ollama Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "mistral")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000", "http://127.0.0.1:3000"]')
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Parse allowed origins from environment variable"""
        try:
            import json
            return json.loads(cls.ALLOWED_ORIGINS_STR)
        except (json.JSONDecodeError, TypeError):
            # Fallback to default origins
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Service Configuration
    HYBRID_MODE_ENABLED = os.getenv("HYBRID_MODE_ENABLED", "True").lower() == "true"
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # File Upload Configuration
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")
    ALLOWED_FILE_TYPES = ["application/pdf", "text/plain"]
    MAX_FILES_PER_REQUEST = int(os.getenv("MAX_FILES_PER_REQUEST", "1"))
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        if not cls.MODEL_NAME:
            issues.append("MODEL_NAME is required")
        
        if not cls.OLLAMA_BASE_URL:
            issues.append("OLLAMA_BASE_URL is required")
        
        try:
            cls.get_allowed_origins()
        except Exception as e:
            issues.append(f"Invalid ALLOWED_ORIGINS format: {str(e)}")
        
        # Validate file size limit
        if cls.MAX_FILE_SIZE <= 0:
            issues.append("MAX_FILE_SIZE must be positive")
        
        if cls.MAX_FILE_SIZE > 52428800:  # 50MB max
            issues.append("MAX_FILE_SIZE cannot exceed 50MB")
        
        return issues 