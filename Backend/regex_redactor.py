import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

from config import Config


@dataclass
class RedactionMatch:
    """Represents a PII match found by regex"""
    start: int
    end: int
    text: str
    pii_type: str
    replacement: str


class RegexRedactor:
    """Regex-based PII redactor for fallback/hybrid mode"""
    
    # Regex patterns for different PII types
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
        "ip_address": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        "url": r'\bhttps?://[^\s<>"{}|\\^`\[\]]+\b'
    }
    
    # Default replacement tags
    DEFAULT_TAGS = {
        "email": "[REDACTED_EMAIL]",
        "phone": "[REDACTED_PHONE]",
        "ssn": "[REDACTED_SSN]",
        "credit_card": "[REDACTED_CREDIT_CARD]",
        "ip_address": "[REDACTED_IP]",
        "url": "[REDACTED_URL]"
    }

    @classmethod
    def find_pii_matches(
        cls, 
        text: str, 
        pii_types: List[str], 
        custom_tags: Dict[str, str] = None
    ) -> List[RedactionMatch]:
        """
        Find all PII matches in the text using regex patterns
        
        Args:
            text: Input text to scan
            pii_types: Types of PII to look for
            custom_tags: Custom replacement tags
            
        Returns:
            List of RedactionMatch objects
        """
        matches = []
        tags = {**cls.DEFAULT_TAGS}
        if custom_tags:
            tags.update(custom_tags)
        
        for pii_type in pii_types:
            if pii_type in cls.PATTERNS:
                pattern = cls.PATTERNS[pii_type]
                replacement = tags.get(pii_type, f"[REDACTED_{pii_type.upper()}]")
                
                for match in re.finditer(pattern, text):
                    matches.append(RedactionMatch(
                        start=match.start(),
                        end=match.end(),
                        text=match.group(),
                        pii_type=pii_type,
                        replacement=replacement
                    ))
        
        # Sort matches by start position to process in order
        matches.sort(key=lambda x: x.start)
        return matches

    @classmethod
    def redact_text(
        cls, 
        text: str, 
        pii_types: List[str], 
        custom_tags: Dict[str, str] = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Redact PII from text using regex patterns
        
        Args:
            text: Input text to redact
            pii_types: Types of PII to redact
            custom_tags: Custom replacement tags
            
        Returns:
            Tuple of (redacted_text, summary_counts)
        """
        matches = cls.find_pii_matches(text, pii_types, custom_tags)
        
        # Create summary counts
        summary = {}
        for pii_type in pii_types:
            summary[pii_type] = len([m for m in matches if m.pii_type == pii_type])
        
        # Apply redactions in reverse order to maintain positions
        redacted_text = text
        for match in reversed(matches):
            redacted_text = (
                redacted_text[:match.start] + 
                match.replacement + 
                redacted_text[match.end:]
            )
        
        return redacted_text, summary

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of PII types supported by regex patterns"""
        return list(cls.PATTERNS.keys())

    @classmethod
    def is_type_supported(cls, pii_type: str) -> bool:
        """Check if a PII type is supported by regex patterns"""
        return pii_type in cls.PATTERNS 