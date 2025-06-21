#!/usr/bin/env python3
"""
Run script for PII Redaction API
"""

import uvicorn
from config import Config

if __name__ == "__main__":
    print("🚀 Starting PII Redaction API...")
    print(f"📝 Model: {Config.MODEL_NAME}")
    print(f"🔗 Ollama URL: {Config.OLLAMA_BASE_URL}")
    print(f"🌐 Server: {Config.API_HOST}:{Config.API_PORT}")
    print(f"🔧 Hybrid Mode: {'enabled' if Config.HYBRID_MODE_ENABLED else 'disabled'}")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.DEBUG,
        log_level=Config.LOG_LEVEL.lower()
    ) 