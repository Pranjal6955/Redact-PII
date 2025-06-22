"""
PII Validator - Post-processing validation system for PII detection
Helps catch PII that might have been missed in the first pass
"""

import re
import logging
from typing import Dict, List, Tuple, Set, Optional

logger = logging.getLogger(__name__)

class PIIValidator:
    """Post-processing validation to catch any missed PII"""
    
    # Common words that might be mistakenly identified as PII
    NON_PII_WORDS = {
        'january', 'february', 'march', 'april', 'may', 'june', 'july',
        'august', 'september', 'october', 'november', 'december',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
        'please', 'thank', 'thanks', 'sincerely', 'regards', 'dear',
        'subject', 'reference', 'regarding', 'hello', 'hi', 'hey',
        'company', 'corporation', 'inc', 'incorporated', 'llc', 'ltd',
        'department', 'university', 'college', 'school', 'hospital',
        'building', 'street', 'avenue', 'road', 'boulevard', 'lane',
        'product', 'service', 'model', 'device', 'system'
    }
    
    # Contextual clues that indicate PII might be present
    PII_CONTEXTUAL_CLUES = {
        'name': ['name:', 'full name:', 'first name:', 'last name:', 'patient:', 'customer:'],
        'ssn': ['ssn:', 'social security:', 'social security number:', 'ss#:'],
        'phone': ['phone:', 'telephone:', 'cell:', 'mobile:', 'contact:'],
        'email': ['email:', 'e-mail:', 'mail:', 'contact:'],
        'address': ['address:', 'residence:', 'location:', 'lives at:', 'lives in:'],
        'dob': ['dob:', 'date of birth:', 'born on:', 'birth date:'],
        'credit_card': ['cc:', 'credit card:', 'card number:', 'cc#:', 'card:'],
        'account': ['account:', 'acct:', 'account number:', 'acct#:'],
        'license': ['license:', 'dl#:', 'driver\'s license:', 'license number:'],
        'passport': ['passport:', 'passport number:', 'passport#:'],
    }
    
    # Additional high-precision regex patterns for second-pass validation
    VALIDATION_PATTERNS = {
        'email': r'\b[A-Za-z0-9._-]{2,}@[A-Za-z0-9.-]{2,}\.[A-Za-z]{2,}\b',
        'phone': r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'ssn': r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'zip_code': r'\b\d{5}(?:-\d{4})?\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'date': r'\b(?:0?[1-9]|1[0-2])[/-](?:0?[1-9]|[12]\d|3[01])[/-](?:19|20)?\d{2}\b'
    }
    
    @classmethod
    def validate_text(cls, text: str, already_redacted: Optional[List[Tuple[int, int]]] = None) -> List[Dict]:
        """
        Perform a second-pass validation to catch any missed PII
        
        Args:
            text: Text to validate, possibly already partially redacted
            already_redacted: List of (start, end) tuples for already redacted portions
            
        Returns:
            List of potential PII that might have been missed
        """
        if already_redacted is None:
            already_redacted = []
            
        potential_pii = []
        
        # 1. Check for contextual clues
        for pii_type, clues in cls.PII_CONTEXTUAL_CLUES.items():
            for clue in clues:
                clue_pos = text.lower().find(clue)
                if clue_pos >= 0:
                    # Look for potential PII after the clue
                    end_of_clue = clue_pos + len(clue)
                    end_of_line = text.find('\n', end_of_clue)
                    if end_of_line == -1:
                        end_of_line = len(text)
                    
                    # Get the text after the clue to the end of line
                    after_clue = text[end_of_clue:end_of_line].strip()
                    
                    # Skip if this is already redacted or empty
                    if after_clue and not cls._is_already_redacted(end_of_clue, end_of_line, already_redacted):
                        potential_pii.append({
                            'type': pii_type,
                            'text': after_clue,
                            'position': (end_of_clue, end_of_line),
                            'confidence': 0.8,
                            'reason': f"Found after contextual clue '{clue}'"
                        })
        
        # 2. Check for high-precision regex patterns
        for pii_type, pattern in cls.VALIDATION_PATTERNS.items():
            for match in re.finditer(pattern, text):
                start, end = match.span()
                
                # Skip if this position is already redacted
                if cls._is_already_redacted(start, end, already_redacted):
                    continue
                
                # Skip common non-PII words
                if match.group().lower() in cls.NON_PII_WORDS:
                    continue
                
                potential_pii.append({
                    'type': pii_type,
                    'text': match.group(),
                    'position': (start, end),
                    'confidence': 0.9,
                    'reason': f"Matched validation pattern for {pii_type}"
                })
        
        # 3. Look for alphanumeric tokens of a certain length (potential IDs)
        for match in re.finditer(r'\b[A-Z0-9]{6,12}\b', text):
            start, end = match.span()
            
            # Skip if this position is already redacted
            if cls._is_already_redacted(start, end, already_redacted):
                continue
            
            # Skip common non-PII words
            if match.group().lower() in cls.NON_PII_WORDS:
                continue
            
            potential_pii.append({
                'type': 'possible_id',
                'text': match.group(),
                'position': (start, end),
                'confidence': 0.6,
                'reason': "Alphanumeric token of suspicious length"
            })
        
        return potential_pii
    
    @staticmethod
    def _is_already_redacted(start: int, end: int, already_redacted: List[Tuple[int, int]]) -> bool:
        """Check if a position range overlaps with already redacted portions"""
        for redacted_start, redacted_end in already_redacted:
            # Check for any overlap
            if not (end <= redacted_start or start >= redacted_end):
                return True
        return False
    
    @classmethod
    def enhance_redaction(cls, original_text: str, redacted_text: str) -> str:
        """
        Enhance redaction by catching potentially missed PII
        
        Args:
            original_text: Original text before redaction
            redacted_text: Text after first-pass redaction
            
        Returns:
            Enhanced redacted text with additional PII redacted
        """
        # Find already redacted portions by comparing original and redacted texts
        already_redacted = []
        i, j = 0, 0
        while i < len(original_text) and j < len(redacted_text):
            if original_text[i] != redacted_text[j]:
                # Found difference - likely a redaction
                redaction_start = j
                
                # Find end of redaction tag
                while j < len(redacted_text) and redacted_text[j] != ']':
                    j += 1
                
                if j < len(redacted_text):
                    j += 1  # Include the closing bracket
                
                redaction_end = j
                already_redacted.append((redaction_start, redaction_end))
                
                # Skip corresponding original text
                while i < len(original_text) and (j >= len(redacted_text) or original_text[i] != redacted_text[j]):
                    i += 1
            else:
                i += 1
                j += 1
        
        # Validate the redacted text to find any missed PII
        potential_missed_pii = cls.validate_text(redacted_text, already_redacted)
        
        # Sort by position in reverse order to redact from end to beginning
        potential_missed_pii.sort(key=lambda x: x['position'][0], reverse=True)
        
        # Apply additional redactions for high-confidence matches
        enhanced_text = redacted_text
        for pii in potential_missed_pii:
            if pii['confidence'] >= 0.8:  # Only use high-confidence matches
                start, end = pii['position']
                replacement = f"[REDACTED_{pii['type'].upper()}]"
                enhanced_text = enhanced_text[:start] + replacement + enhanced_text[end:]
                logger.info(f"Enhanced redaction: {pii['text']} -> {replacement} ({pii['reason']})")
        
        return enhanced_text
