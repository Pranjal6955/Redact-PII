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
        "date": "[REDACTED_DATE]",
        "ssn": "[REDACTED_SSN]"
    }
    
    # PII type descriptions for the prompt
    PII_DESCRIPTIONS = {
        "name": "personal names (first names, last names, full names, nicknames, aliases, maiden names). Look for people's names in contexts like 'Name:', 'Patient:', 'Customer:', 'Employee:', etc. Do NOT redact company names, organization names, or brand names",
        "email": "email addresses in any format (user@domain.com, user.name@domain.co.uk, user+tag@domain.org, etc.)",
        "phone": "phone numbers in any format (555-123-4567, (555) 123-4567, +1-555-123-4567, 555.123.4567, 5551234567, international formats)",
        "address": "complete physical addresses including street numbers, street names, cities, states/provinces, zip/postal codes, and countries. Look for full address blocks",
        "credit_card": "credit card numbers, debit card numbers in any format (4111-1111-1111-1111, 4111 1111 1111 1111, 4111111111111111, etc.)",
        "date": "personal dates especially dates of birth (DOB), birth dates, anniversary dates, personal milestones. Look for patterns like 'Date of Birth:', 'DOB:', 'Born:', etc. Do NOT redact general calendar dates or holidays",
        "ssn": "Social Security Numbers in any format (123-45-6789, 123 45 6789, 123456789, etc.). Look for patterns like 'SSN:', 'Social Security:', etc."
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

CRITICAL INSTRUCTIONS:
1. CAREFULLY analyze the text and identify ALL instances of the specified PII types
2. Replace each identified PII with the corresponding replacement tag EXACTLY as shown
3. Maintain the original text structure, formatting, and punctuation
4. Be THOROUGH - it's better to redact something that might be PII than to miss it

SPECIFIC GUIDELINES:
For NAMES:
- Look for personal names in contexts like "Name:", "Patient:", "Customer:", "Employee:", "Client:", etc.
- Redact first names, last names, full names, nicknames, aliases, and middle names/initials
- Consider titles like Dr., Mr., Mrs., Ms. as part of the name
- DO NOT redact company names, organization names, hospital names, or brand names
- Examples: "John Smith", "Dr. Sarah Johnson", "Michael R. Davis"

For ADDRESSES:
- Redact complete addresses including street number, street name, city, state, zip code
- Look for address patterns like "123 Main St, Springfield, IL 62701"
- Include apartment numbers, suite numbers, and unit numbers as part of the address
- Examples: "123 Main Street, Springfield, IL 62701", "456 Oak Ave Apt 2B, Portland, OR 97201"

For DATES:
- Focus on personal dates, especially dates of birth (DOB)
- Look for contexts like "Date of Birth:", "DOB:", "Born:", "Birth Date:"
- Redact dates in formats like MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD
- DO NOT redact general calendar dates, holidays, or business dates unless clearly personal
- Examples: "08/10/1973", "05/28/2007", "Birth Date: 12/15/1985"

For EMAILS:
- Redact all email addresses regardless of format
- Examples: "john@email.com", "sarah.johnson@gmail.com", "user+tag@domain.org"

For PHONES:
- Redact phone numbers in any format
- Examples: "(555) 123-4567", "555-123-4567", "+1-555-123-4567", "555.123.4567"

For CREDIT CARDS:
- Redact credit/debit card numbers in any format
- Examples: "4532-1234-5678-9012", "4532 1234 5678 9012", "4532123456789012"

For SSN:
- Redact Social Security Numbers in any format
- Look for contexts like "SSN:", "Social Security:", "Social Security Number:"
- Examples: "123-45-6789", "123 45 6789", "123456789"

INPUT TEXT:
{text}

REDACTED TEXT:"""

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
1. CAREFULLY analyze the text and identify ALL instances of the specified PII types
2. Count how many instances of each PII type you find
3. Be THOROUGH - it's better to count something that might be PII than to miss it
4. Consider context when identifying names vs common words

SPECIFIC GUIDELINES:
- For NAMES: Look for personal names in contexts like "Name:", "Patient:", "Customer:", etc. Count each full name as 1 instance
- For ADDRESSES: Count complete address blocks as 1 instance each  
- For DATES: Focus on personal dates like birth dates, count each date as 1 instance
- For EMAILS: Count each email address as 1 instance
- For PHONES: Count each phone number as 1 instance
- For CREDIT CARDS: Count each card number as 1 instance
- For SSN: Count each Social Security Number as 1 instance

INPUT TEXT:
{text}

Please provide a JSON response with the count of each PII type found, in this exact format:
{{
  "name": 0,
  "email": 0,
  "phone": 0,
  "address": 0,
  "credit_card": 0,
  "date": 0,
  "ssn": 0
}}

Only include the PII types that were requested in the analysis. Return ONLY the JSON response, no additional text."""

        return prompt 