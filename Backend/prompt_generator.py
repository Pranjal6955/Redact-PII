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
        "ssn": "[REDACTED_SSN]",
        "drivers_license": "[REDACTED_DRIVERS_LICENSE]",
        "passport": "[REDACTED_PASSPORT]", 
        "bank_account": "[REDACTED_BANK_ACCOUNT]",
        "ip_address": "[REDACTED_IP_ADDRESS]",
        "medical_record": "[REDACTED_MEDICAL_RECORD]",
        "employee_id": "[REDACTED_EMPLOYEE_ID]",
        "license_plate": "[REDACTED_LICENSE_PLATE]",
        "vin": "[REDACTED_VIN]",
        "insurance_policy": "[REDACTED_INSURANCE_POLICY]",
        "tax_id": "[REDACTED_TAX_ID]",
        "credit_score": "[REDACTED_CREDIT_SCORE]",
        "biometric": "[REDACTED_BIOMETRIC]",
        "personal_url": "[REDACTED_PERSONAL_URL]",
        "mac_address": "[REDACTED_MAC_ADDRESS]",
        "guid": "[REDACTED_GUID]"
    }
    
    # Enhanced PII type descriptions for the prompt
    PII_DESCRIPTIONS = {
        "name": "personal names (first names, last names, full names, nicknames, aliases, maiden names, middle names, middle initials). Look for people's names in contexts like 'Name:', 'Patient:', 'Customer:', 'Employee:', 'Client:', 'Dr.', 'Mr.', 'Mrs.', 'Ms.', etc. Do NOT redact company names, organization names, or brand names",
        "email": "email addresses in any format (user@domain.com, user.name@domain.co.uk, user+tag@domain.org, etc.). Look for the @ symbol followed by a domain name. Include partial emails if domain is visible",
        "phone": "phone numbers in any format (555-123-4567, (555) 123-4567, +1-555-123-4567, 555.123.4567, 5551234567, international formats)",
        "address": "complete physical addresses including street numbers, street names, cities, states/provinces, zip/postal codes, and countries. Look for full address blocks",
        "credit_card": "credit card numbers, debit card numbers in any format (4111-1111-1111-1111, 4111 1111 1111 1111, 4111111111111111, etc.)",
        "date": "personal dates especially dates of birth (DOB), birth dates, anniversary dates, personal milestones. Look for patterns like 'Date of Birth:', 'DOB:', 'Born:', etc. Do NOT redact general calendar dates or holidays",
        "ssn": "Social Security Numbers in any format (123-45-6789, 123 45 6789, 123456789, etc.). Look for patterns like 'SSN:', 'Social Security:', etc.",
        "drivers_license": "driver's license numbers in various US state formats (A1234567, 123456789, AB-123-456, etc.). Look for patterns like 'Driver's License:', 'DL:', 'License #:', etc.",
        "passport": "passport numbers in various formats (A12345678, 123456789, etc.). Look for patterns like 'Passport:', 'Passport Number:', etc.",
        "bank_account": "bank account numbers, routing numbers (12345678901, 1234-5678-9012, etc.). Look for patterns like 'Account Number:', 'Account #:', 'Routing:', etc.",
        "ip_address": "IP addresses both IPv4 and IPv6 formats (192.168.1.1, 2001:0db8:85a3:0000:0000:8a2e:0370:7334, etc.)",
        "medical_record": "medical record numbers, patient IDs (MRN123456, P-123456789, etc.). Look for patterns like 'Medical Record:', 'MRN:', 'Patient ID:', etc.",
        "employee_id": "employee identification numbers (EMP123456, E-123456, etc.). Look for patterns like 'Employee ID:', 'EMP:', 'Staff ID:', etc.",
        "license_plate": "vehicle license plate numbers (ABC-1234, 123-ABC, etc.)",
        "vin": "Vehicle Identification Numbers (1HGCM82633A123456, etc.). 17-character alphanumeric codes",
        "insurance_policy": "insurance policy numbers (POL123456789, INS-123-456-789, etc.). Look for patterns like 'Policy:', 'Policy Number:', etc.",
        "tax_id": "Tax Identification Numbers, EIN numbers (12-3456789, etc.). Look for patterns like 'Tax ID:', 'EIN:', etc.",
        "credit_score": "credit scores and ratings (750, 680, FICO 720, etc.). Typically 3-digit numbers between 300-850",
        "biometric": "biometric identifiers, fingerprint IDs, DNA sample IDs (FP123456, DNA-ABC123, etc.)",
        "personal_url": "personal social media URLs and profiles (facebook.com/username, linkedin.com/in/profile, github.com/user, etc.)",
        "mac_address": "MAC addresses (00:1B:44:11:3A:B7, 00-1B-44-11-3A-B7, etc.)",
        "guid": "GUIDs and UUIDs (550e8400-e29b-41d4-a716-446655440000, etc.)"
    }

    @classmethod
    def get_all_pii_types(cls) -> List[str]:
        """Get all supported PII types"""
        return list(cls.PII_DESCRIPTIONS.keys())
    
    @classmethod
    def get_auto_detect_types(cls) -> List[str]:
        """Get PII types for automatic detection"""
        return [
            "name", "email", "phone", "address", "credit_card", "date", "ssn",
            "drivers_license", "passport", "bank_account", "ip_address", 
            "medical_record", "employee_id", "tax_id", "credit_score", 
            "personal_url", "mac_address", "guid"
        ]

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

For DRIVER'S LICENSE:
- Redact driver's license numbers in various US state formats
- Look for patterns like "Driver's License:", "DL:", "License #:", etc.
- Examples: "A1234567", "123456789", "AB-123-456"

For PASSPORTS:
- Redact passport numbers in various formats
- Look for patterns like "Passport:", "Passport Number:", etc.
- Examples: "A12345678", "123456789"

For BANK ACCOUNTS:
- Redact bank account numbers, routing numbers
- Look for patterns like "Account Number:", "Account #:", "Routing:", etc.
- Examples: "12345678901", "1234-5678-9012"

For IP ADDRESSES:
- Redact IP addresses both IPv4 and IPv6 formats
- Examples: "192.168.1.1", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

For MEDICAL RECORDS:
- Redact medical record numbers, patient IDs
- Look for patterns like "Medical Record:", "MRN:", "Patient ID:", etc.
- Examples: "MRN123456", "P-123456789"

For EMPLOYEE IDS:
- Redact employee identification numbers
- Look for patterns like "Employee ID:", "EMP:", "Staff ID:", etc.
- Examples: "EMP123456", "E-123456"

For LICENSE PLATES:
- Redact vehicle license plate numbers
- Examples: "ABC-1234", "123-ABC"

For VIN:
- Redact Vehicle Identification Numbers
- 17-character alphanumeric codes
- Examples: "1HGCM82633A123456"

For INSURANCE POLICIES:
- Redact insurance policy numbers
- Look for patterns like "Policy:", "Policy Number:", etc.
- Examples: "POL123456789", "INS-123-456-789"

For TAX IDs:
- Redact Tax Identification Numbers, EIN numbers
- Look for patterns like "Tax ID:", "EIN:", etc.
- Examples: "12-3456789"

For CREDIT SCORES:
- Redact credit scores and ratings
- Typically 3-digit numbers between 300-850
- Examples: "750", "680", "FICO 720"

For BIOMETRIC DATA:
- Redact biometric identifiers, fingerprint IDs, DNA sample IDs
- Examples: "FP123456", "DNA-ABC123"

For PERSONAL URLS:
- Redact personal social media URLs and profiles
- Examples: "facebook.com/username", "linkedin.com/in/profile"

For MAC ADDRESSES:
- Redact MAC addresses
- Examples: "00:1B:44:11:3A:B7", "00-1B-44-11-3A-B7"

For GUIDS:
- Redact GUIDs and UUIDs
- Examples: "550e8400-e29b-41d4-a716-446655440000"

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
- For DRIVER'S LICENSE: Count each driver's license number as 1 instance
- For PASSPORTS: Count each passport number as 1 instance
- For BANK ACCOUNTS: Count each bank account number as 1 instance
- For IP ADDRESSES: Count each IP address as 1 instance
- For MEDICAL RECORDS: Count each medical record number as 1 instance
- For EMPLOYEE IDS: Count each employee ID as 1 instance
- For LICENSE PLATES: Count each license plate number as 1 instance
- For VIN: Count each VIN as 1 instance
- For INSURANCE POLICIES: Count each insurance policy number as 1 instance
- For TAX IDs: Count each tax ID as 1 instance
- For CREDIT SCORES: Count each credit score as 1 instance
- For BIOMETRIC DATA: Count each biometric data instance as 1 instance
- For PERSONAL URLS: Count each personal URL as 1 instance
- For MAC ADDRESSES: Count each MAC address as 1 instance
- For GUIDS: Count each GUID as 1 instance

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
  "ssn": 0,
  "drivers_license": 0,
  "passport": 0,
  "bank_account": 0,
  "ip_address": 0,
  "medical_record": 0,
  "employee_id": 0,
  "license_plate": 0,
  "vin": 0,
  "insurance_policy": 0,
  "tax_id": 0,
  "credit_score": 0,
  "biometric": 0,
  "personal_url": 0,
  "mac_address": 0,
  "guid": 0
}}

Only include the PII types that were requested in the analysis. Return ONLY the JSON response, no additional text."""

        return prompt