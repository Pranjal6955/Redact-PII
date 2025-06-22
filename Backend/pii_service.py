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
        use_hybrid: bool = True,
        auto_detect_all: bool = True
    ) -> Tuple[bool, RedactResponse, Optional[str]]:
        """
        Redact PII from text using hybrid approach with automatic detection
        
        Args:
            request: RedactRequest object with text and configuration
            use_hybrid: Whether to use hybrid approach (LLM + regex fallback)
            auto_detect_all: Whether to automatically detect all supported PII types
            
        Returns:
            Tuple of (success, RedactResponse, error_message)
        """
        try:
            # If auto_detect_all is enabled, expand redact_types to include all supported types
            if auto_detect_all:
                all_types = self.get_all_supported_pii_types()
                # Combine requested types with all supported types, removing duplicates
                expanded_types = list(set(request.redact_types + all_types))
                # Create new request with expanded types
                enhanced_request = RedactRequest(
                    text=request.text,
                    redact_types=expanded_types,
                    custom_tags=request.custom_tags
                )
            else:
                enhanced_request = request
            
            if use_hybrid:
                return await self._hybrid_redact(enhanced_request)
            else:
                return await self._llm_only_redact(enhanced_request)
                
        except Exception as e:
            logger.error(f"Error in PII redaction: {str(e)}")
            return False, None, f"Internal error: {str(e)}"
    
    async def _hybrid_redact(self, request: RedactRequest) -> Tuple[bool, RedactResponse, Optional[str]]:
        """
        Enhanced hybrid redaction with comprehensive PII detection
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
        
        logger.info(f"Regex types: {len(regex_types)}, LLM types: {len(llm_types)}")
        
        # Step 1: Use regex for supported types
        regex_redacted = text
        regex_summary = {}
        
        if regex_types:
            regex_redacted, regex_summary = self.regex_redactor.redact_text(
                text, regex_types, custom_tags
            )
            logger.info(f"Regex redaction found: {sum(regex_summary.values())} items")
        
        # Step 2: Use LLM for remaining types or as enhancement
        llm_summary = {}
        final_redacted = regex_redacted
        
        # Always use LLM if available, even for regex-supported types for better accuracy
        all_types_for_llm = redact_types if llm_types or len(regex_types) > 0 else []
        
        if all_types_for_llm:
            # Check if Ollama is available
            is_connected, status = await self.ollama_client.check_connection()
            
            if is_connected:
                success, llm_redacted, error = await self.ollama_client.redact_pii(
                    regex_redacted, all_types_for_llm, custom_tags
                )
                
                if success:
                    final_redacted = llm_redacted
                    # Get analysis for summary
                    _, llm_summary, _ = await self.ollama_client.analyze_pii(
                        text, all_types_for_llm
                    )
                    logger.info(f"LLM redaction enhanced with: {sum(llm_summary.values())} items")
                else:
                    logger.warning(f"LLM redaction failed: {error}")
                    # Continue with regex-only result
            else:
                logger.warning(f"Ollama not available: {status}")
        
        # Combine summaries, prioritizing LLM results for accuracy
        combined_summary = {**regex_summary}
        for pii_type, count in llm_summary.items():
            combined_summary[pii_type] = max(combined_summary.get(pii_type, 0), count)
        
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
        Get comprehensive information about supported PII types
        
        Returns:
            Dictionary with detailed PII type information
        """
        return {
            "regex_supported": self.regex_redactor.get_supported_types(),
            "all_supported": self.get_all_supported_pii_types(),
            "critical_types": self.regex_redactor.get_critical_pii_types(),
            "common_types": self.regex_redactor.get_common_pii_types(),
            "auto_detect_types": PromptGenerator.get_auto_detect_types(),
            "total_types": len(self.get_all_supported_pii_types())
        }
    
    def get_all_supported_pii_types(self) -> List[str]:
        """Get all supported PII types from all sources"""
        regex_types = set(self.regex_redactor.get_supported_types())
        prompt_types = set(PromptGenerator.get_all_pii_types())
        return sorted(list(regex_types.union(prompt_types)))
    
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