import logging
from typing import Dict, List, Optional

from config import Config


class PromptGenerator:
    """Generates dynamic prompts for PII redaction based on configuration"""
    
    # Default replacement tags for each PII type
    DEFAULT_TAGS = {
        "name": "[REDACTED_NAME]",
        "email": "[REDACTED_EMAIL]",
        "phone": "[REDACTED_PHONE]",
        "address": "[REDACTED_ADDRESS]",
        "credit_card": "[REDACTED_CREDIT_CARD]",
        "date": "[REDACTED_DATE]"
    }
    
    # PII type descriptions for the prompt
    PII_DESCRIPTIONS = {
        "name": "personal names (first names, last names, full names, nicknames)",
        "email": "email addresses",
        "phone": "phone numbers (including international formats)",
        "address": "physical addresses, street addresses, postal addresses",
        "credit_card": "credit card numbers, debit card numbers",
        "date": "dates of birth, personal dates"
    }

    @classmethod
    def generate_redaction_prompt(
        cls, 
        text: str, 
        redact_types: List[str], 
        custom_tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a comprehensive prompt for PII redaction
        
        Args:
            text: Input text to redact
            redact_types: List of PII types to detect and redact
            custom_tags: Optional custom replacement tags
            
        Returns:
            Formatted prompt string for the LLM
        """
        # Use custom tags or defaults
        tags = {**cls.DEFAULT_TAGS}
        if custom_tags:
            tags.update(custom_tags)
        
        # Build the PII types description
        pii_descriptions = []
        for pii_type in redact_types:
            if pii_type in cls.PII_DESCRIPTIONS:
                pii_descriptions.append(f"- {pii_type}: {cls.PII_DESCRIPTIONS[pii_type]}")
        
        # Build the replacement mapping
        replacement_mapping = []
        for pii_type in redact_types:
            if pii_type in tags:
                replacement_mapping.append(f"- {pii_type} → {tags[pii_type]}")
        
        prompt = f"""You are a PII (Personally Identifiable Information) redaction expert. Your task is to identify and replace specific types of PII in the given text.

TYPES OF PII TO DETECT AND REDACT:
{chr(10).join(pii_descriptions)}

REPLACEMENT MAPPING:
{chr(10).join(replacement_mapping)}

INSTRUCTIONS:
1. Carefully analyze the text and identify all instances of the specified PII types
2. Replace each identified PII with the corresponding replacement tag
3. Maintain the original text structure and formatting
4. Be thorough but avoid false positives
5. For names, consider context to avoid redacting common words that happen to be names
6. For addresses, redact complete addresses including street, city, state, zip
7. For dates, focus on personal dates like birth dates, not general dates

INPUT TEXT:
{text}

Please provide the redacted text with all specified PII types replaced with their corresponding tags. Return ONLY the redacted text, no explanations or additional text."""

        return prompt

    @classmethod
    def generate_analysis_prompt(
        cls, 
        text: str, 
        redact_types: List[str]
    ) -> str:
        """
        Generate a prompt for analyzing PII without redacting
        
        Args:
            text: Input text to analyze
            redact_types: List of PII types to detect
            
        Returns:
            Formatted prompt string for PII analysis
        """
        pii_descriptions = []
        for pii_type in redact_types:
            if pii_type in cls.PII_DESCRIPTIONS:
                pii_descriptions.append(f"- {pii_type}: {cls.PII_DESCRIPTIONS[pii_type]}")
        
        prompt = f"""You are a PII (Personally Identifiable Information) detection expert. Analyze the given text and identify all instances of the specified PII types.

TYPES OF PII TO DETECT:
{chr(10).join(pii_descriptions)}

INSTRUCTIONS:
1. Carefully analyze the text and identify all instances of the specified PII types
2. Count how many instances of each PII type you find
3. Be thorough but avoid false positives
4. Consider context when identifying names vs common words

INPUT TEXT:
{text}

Please provide a JSON response with the count of each PII type found, in this exact format:
{{
  "name": 0,
  "email": 0,
  "phone": 0,
  "address": 0,
  "credit_card": 0,
  "date": 0
}}

Only include the PII types that were requested in the analysis. Return ONLY the JSON response, no additional text."""

        return prompt 