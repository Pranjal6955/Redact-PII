import logging
from typing import Dict, List, Optional, Tuple
from ollama_client import OllamaClient
from regex_redactor import RegexRedactor
from models import RedactRequest, RedactResponse
from prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


class PIIService:
    """Main service for PII redaction with hybrid LLM + regex approach"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.regex_redactor = RegexRedactor()
        
    async def redact_text(
        self, 
        request: RedactRequest,
        use_hybrid: bool = True
    ) -> Tuple[bool, RedactResponse, Optional[str]]:
        """
        Redact PII from text using hybrid approach
        
        Args:
            request: RedactRequest object with text and configuration
            use_hybrid: Whether to use hybrid approach (LLM + regex fallback)
            
        Returns:
            Tuple of (success, RedactResponse, error_message)
        """
        try:
            if use_hybrid:
                return await self._hybrid_redact(request)
            else:
                return await self._llm_only_redact(request)
                
        except Exception as e:
            logger.error(f"Error in PII redaction: {str(e)}")
            return False, None, f"Internal error: {str(e)}"
    
    async def _hybrid_redact(self, request: RedactRequest) -> Tuple[bool, RedactResponse, Optional[str]]:
        """
        Hybrid redaction: Use regex for supported types, LLM for others
        """
        text = request.text
        redact_types = request.redact_types
        custom_tags = request.custom_tags or {}
        
        # Split PII types into regex-supported and LLM-only
        regex_types = []
        llm_types = []
        
        for pii_type in redact_types:
            if self.regex_redactor.is_type_supported(pii_type):
                regex_types.append(pii_type)
            else:
                llm_types.append(pii_type)
        
        # Step 1: Use regex for supported types
        regex_redacted = text
        regex_summary = {}
        
        if regex_types:
            regex_redacted, regex_summary = self.regex_redactor.redact_text(
                text, regex_types, custom_tags
            )
        
        # Step 2: Use LLM for remaining types
        llm_summary = {}
        final_redacted = regex_redacted
        
        if llm_types:
            # Check if Ollama is available
            is_connected, status = await self.ollama_client.check_connection()
            
            if is_connected:
                success, llm_redacted, error = await self.ollama_client.redact_pii(
                    regex_redacted, llm_types, custom_tags
                )
                
                if success:
                    final_redacted = llm_redacted
                    # Get analysis for summary
                    _, llm_summary, _ = await self.ollama_client.analyze_pii(
                        regex_redacted, llm_types
                    )
                else:
                    logger.warning(f"LLM redaction failed: {error}")
                    # Continue with regex-only result
            else:
                logger.warning(f"Ollama not available: {status}")
        
        # Combine summaries
        combined_summary = {**regex_summary, **llm_summary}
        
        # Ensure all requested types are in summary
        for pii_type in redact_types:
            if pii_type not in combined_summary:
                combined_summary[pii_type] = 0
        
        response = RedactResponse(
            original=text,
            redacted=final_redacted,
            summary=combined_summary,
            redact_types_used=redact_types
        )
        
        return True, response, None
    
    async def _llm_only_redact(self, request: RedactRequest) -> Tuple[bool, RedactResponse, Optional[str]]:
        """
        LLM-only redaction approach
        """
        # Check Ollama connection
        is_connected, status = await self.ollama_client.check_connection()
        
        if not is_connected:
            return False, None, f"Ollama not available: {status}"
        
        # Use LLM for redaction
        success, redacted_text, error = await self.ollama_client.redact_pii(
            request.text, request.redact_types, request.custom_tags
        )
        
        if not success:
            return False, None, error
        
        # Get analysis for summary
        _, summary, _ = await self.ollama_client.analyze_pii(
            request.text, request.redact_types
        )
        
        response = RedactResponse(
            original=request.text,
            redacted=redacted_text,
            summary=summary,
            redact_types_used=request.redact_types
        )
        
        return True, response, None
    
    async def analyze_text(
        self, 
        text: str, 
        redact_types: List[str]
    ) -> Tuple[bool, Dict[str, int], Optional[str]]:
        """
        Analyze text for PII without redacting
        
        Args:
            text: Input text to analyze
            redact_types: Types of PII to detect
            
        Returns:
            Tuple of (success, summary_counts, error_message)
        """
        try:
            # Check Ollama connection
            is_connected, status = await self.ollama_client.check_connection()
            
            if not is_connected:
                return False, {}, f"Ollama not available: {status}"
            
            # Use LLM for analysis
            success, summary, error = await self.ollama_client.analyze_pii(text, redact_types)
            
            if not success:
                return False, {}, error
            
            return True, summary, None
            
        except Exception as e:
            logger.error(f"Error in PII analysis: {str(e)}")
            return False, {}, f"Internal error: {str(e)}"
    
    def get_supported_types(self) -> Dict[str, List[str]]:
        """
        Get information about supported PII types
        
        Returns:
            Dictionary with regex and llm supported types
        """
        return {
            "regex_supported": self.regex_redactor.get_supported_types(),
            "all_supported": [
                "name", "email", "phone", "address", 
                "credit_card", "date"
            ]
        }
    
    async def get_service_status(self) -> Dict[str, str]:
        """
        Get service status information
        
        Returns:
            Dictionary with service status details
        """
        is_connected, status = await self.ollama_client.check_connection()
        
        return {
            "service_status": "healthy",
            "ollama_status": "connected" if is_connected else "disconnected",
            "ollama_message": status,
            "model_name": self.ollama_client.model_name,
            "hybrid_mode": "enabled"
        } 