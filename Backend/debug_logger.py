"""
Debug logger to help diagnose issues with the PII redaction API
"""

import logging
import sys
import traceback
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

# Configure the logger
logger = logging.getLogger("debug_logger")
logger.setLevel(logging.DEBUG)

# Create log directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Create a file handler that logs debug and higher level messages
log_file = os.path.join(log_dir, f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create a console handler with a higher log level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class DebugLogger:
    """Debug logger to help diagnose issues with the PII redaction API"""
    
    @staticmethod
    def log_request(endpoint: str, payload: Any, method: str = "POST"):
        """Log API request details"""
        try:
            logger.info(f"REQUEST: {method} {endpoint}")
            if isinstance(payload, dict) or isinstance(payload, list):
                logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            else:
                logger.debug(f"Payload: {payload}")
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")
    
    @staticmethod
    def log_file_upload(filename: str, size: int, content_type: str):
        """Log file upload details"""
        logger.info(f"FILE UPLOAD: {filename} ({size} bytes, {content_type})")
    
    @staticmethod
    def log_error(error: Exception, context: Optional[str] = None):
        """Log error details with stack trace"""
        if context:
            logger.error(f"ERROR in {context}: {str(error)}")
        else:
            logger.error(f"ERROR: {str(error)}")
        
        logger.debug(f"Stack trace: {traceback.format_exc()}")
    
    @staticmethod
    def log_response(status_code: int, response: Any, endpoint: str = "unknown"):
        """Log API response details"""
        try:
            logger.info(f"RESPONSE: {status_code} from {endpoint}")
            if isinstance(response, dict) or isinstance(response, list):
                logger.debug(f"Response data: {json.dumps(response, indent=2)}")
            else:
                logger.debug(f"Response data: {response}")
        except Exception as e:
            logger.error(f"Error logging response: {str(e)}")
    
    @staticmethod
    def log_process_info(message: str, data: Optional[Dict] = None):
        """Log processing information"""
        logger.info(f"PROCESS: {message}")
        if data:
            try:
                logger.debug(f"Process data: {json.dumps(data, indent=2)}")
            except Exception:
                logger.debug(f"Process data: {data}")
