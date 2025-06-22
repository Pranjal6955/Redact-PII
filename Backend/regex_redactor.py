import re
from typing import Dict, List, Tuple, Set
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
    confidence: float = 1.0  # Add confidence score to each match
    
    def to_dict(self):
        """Convert match to dictionary"""
        return {
            'start': self.start,
            'end': self.end,
            'text': self.text,
            'pii_type': self.pii_type,
            'replacement': self.replacement,
            'confidence': self.confidence
        }


class RegexRedactor:
    """Regex-based PII redactor for fallback/hybrid mode"""
    
    # Common first names and last names for validation
    COMMON_FIRST_NAMES = {
        'john', 'jane', 'michael', 'sarah', 'david', 'emily', 'robert', 'lisa', 'james', 'mary',
        'william', 'patricia', 'richard', 'jennifer', 'charles', 'linda', 'joseph', 'elizabeth',
        'thomas', 'barbara', 'christopher', 'susan', 'daniel', 'jessica', 'paul', 'karen',
        'mark', 'nancy', 'donald', 'betty', 'george', 'helen', 'kenneth', 'sandra', 'steven',
        'donna', 'edward', 'carol', 'brian', 'ruth', 'ronald', 'sharon', 'anthony', 'michelle',
        'kevin', 'laura', 'jason', 'sarah', 'matthew', 'kimberly', 'gary', 'deborah', 'timothy',
        'dorothy', 'jose', 'lisa', 'larry', 'nancy', 'jeffrey', 'karen', 'frank', 'betty',
        'scott', 'helen', 'eric', 'sandra', 'stephen', 'donna', 'andrew', 'carol', 'raymond',
        'ruth', 'joshua', 'sharon', 'jerry', 'michelle', 'dennis', 'laura', 'walter', 'sarah',
        'patrick', 'kimberly', 'peter', 'deborah', 'harold', 'dorothy', 'douglas', 'amy',
        'henry', 'angela', 'carl', 'ashley', 'arthur', 'brenda', 'ryan', 'pamela', 'roger',
        'nicole', 'joe', 'samantha', 'juan', 'katherine', 'jack', 'emma', 'albert', 'anna',
        'jonathan', 'marie', 'wayne', 'julie', 'roy', 'joyce', 'noah', 'grace', 'eugene',
        'christina', 'ralph', 'evelyn', 'louis', 'rachel', 'philip', 'frances', 'austin',
        'martha', 'alan', 'olivia', 'sean', 'sophia', 'sean', 'rose', 'mason', 'irene',
        'ethan', 'alice', 'owen', 'jean', 'liam', 'barbara', 'elijah', 'catherine', 'lucas',
        'margaret', 'jacob', 'elizabeth', 'benjamin', 'debra', 'alexander', 'rebecca',
        'nicholas', 'maria', 'nathan', 'gloria', 'aaron', 'teresa', 'isaac', 'diane',
        'edward', 'julie', 'jordan', 'joyce', 'cooper', 'virginia', 'evan', 'victoria',
        'andrew', 'kelly', 'ian', 'christina', 'adam', 'joan', 'parker', 'evelyn',
        'blake', 'judith', 'xavier', 'megan', 'dean', 'cheryl', 'chase', 'andrea',
        'cole', 'hannah', 'tyler', 'jacqueline', 'marcus', 'martha', 'miles', 'frances'
    }
    
    # Common last names for validation
    COMMON_LAST_NAMES = {
        'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
        'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson',
        'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'perez', 'thompson',
        'white', 'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker',
        'young', 'allen', 'king', 'wright', 'scott', 'torres', 'nguyen', 'hill',
        'flores', 'green', 'adams', 'nelson', 'baker', 'hall', 'rivera', 'campbell',
        'mitchell', 'carter', 'roberts', 'gomez', 'phillips', 'evans', 'turner',
        'diaz', 'parker', 'cruz', 'edwards', 'collins', 'reyes', 'stewart', 'morris',
        'morales', 'murphy', 'cook', 'rogers', 'gutierrez', 'ortiz', 'morgan',
        'cooper', 'peterson', 'bailey', 'reed', 'kelly', 'howard', 'ramos', 'kim',
        'cox', 'ward', 'richardson', 'watson', 'brooks', 'chavez', 'wood', 'james',
        'bennett', 'gray', 'mendoza', 'ruiz', 'hughes', 'price', 'alvarez', 'castillo',
        'sanders', 'patel', 'myers', 'long', 'ross', 'foster', 'jimenez', 'powell',
        'jenkins', 'perry', 'russell', 'sullivan', 'bell', 'coleman', 'butler',
        'henderson', 'barnes', 'gonzales', 'fisher', 'vasquez', 'simmons', 'romero',
        'jordan', 'patterson', 'alexander', 'hamilton', 'graham', 'reynolds', 'griffin',
        'wallace', 'moreno', 'west', 'cole', 'hayes', 'bryant', 'herrera', 'gibson',
        'ellis', 'tran', 'medina', 'aguilar', 'stevens', 'murray', 'ford', 'castro',
        'marshall', 'owen', 'harrison', 'fernandez', 'mcdonald', 'woods', 'washington',
        'kennedy', 'wells', 'vargas', 'henry', 'chen', 'freeman', 'webb', 'tucker',
        'guzman', 'burns', 'crawford', 'olson', 'simpson', 'porter', 'hunter',
        'gordon', 'mendez', 'silva', 'shaw', 'snyder', 'mason', 'dixon', 'munoz',
        'hunt', 'hicks', 'holmes', 'palmer', 'wagner', 'black', 'robertson', 'boyd',
        'rose', 'stone', 'salazar', 'fox', 'warren', 'mills', 'meyer', 'rice',
        'schmidt', 'garza', 'daniels', 'ferguson', 'nichols', 'stephens', 'soto',
        'weaver', 'ryan', 'gardner', 'payne', 'grant', 'dunn', 'kelley', 'spencer',
        'hawkins', 'arnold', 'pierce', 'vazquez', 'hansen', 'peters', 'santos',
        'hart', 'bradley', 'knight', 'elliott', 'cunningham', 'duncan', 'armstrong',
        'hudson', 'carroll', 'lane', 'riley', 'andrews', 'alonso', 'gilbert',
        'reynolds', 'burke', 'hanson', 'day', 'robertson', 'hicks', 'medina'
    }
    
    # Regex patterns for different PII types
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        "credit_card": r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
        # Simplified name patterns - will use validation to improve accuracy
        "name": r'\b[A-Z][a-z\'-]+(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z\'-]+){1,2}(?:\s+(?:Jr\.?|Sr\.?|III|IV|V))?\b',
        # Address patterns - comprehensive US address matching
        "address": r'\b\d+(?:\s+[NSEW]\.?)?\s+[A-Za-z0-9\s,.-]+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Drive|Dr\.?|Lane|Ln\.?|Boulevard|Blvd\.?|Way|Place|Pl\.?|Court|Ct\.?|Circle|Cir\.?|Parkway|Pkwy\.?|Trail|Trl\.?|Commons?|Square|Sq\.?)(?:\s+(?:Apt|Apartment|Suite|Ste|Unit|#)\s*[A-Za-z0-9]+)?\s*,?\s*[A-Za-z\s]+,?\s*(?:[A-Z]{2}|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New\s+Hampshire|New\s+Jersey|New\s+Mexico|New\s+York|North\s+Carolina|North\s+Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode\s+Island|South\s+Carolina|South\s+Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West\s+Virginia|Wisconsin|Wyoming)\s+\d{5}(?:-\d{4})?\b',
        # Date patterns - multiple formats for birth dates and personal dates
        "date": r'(?i:(?:Date\s+of\s+Birth|DOB|Birth\s+Date|Born)[\s:]*)?(?:\b(?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12][0-9]|3[01])[-/.](?:19|20)\d{2}\b|\b(?:0?[1-9]|[12][0-9]|3[01])[-/.](?:0?[1-9]|1[0-2])[-/.](?:19|20)\d{2}\b|\b(?:19|20)\d{2}[-/.](?:0?[1-9]|1[0-2])[-/.](?:0?[1-9]|[12][0-9]|3[01])\b)',
        # SSN patterns
        "ssn": r'(?i:(?:Social\s+Security|SSN)(?:\s+Number)?[\s:]*)?(?:\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b)',
        # Driver's License patterns (US format)
        "drivers_license": r'(?i:(?:Driver\'?s?\s+License|DL|License)[\s#:]*)?(?:\b[A-Z]{1,2}\d{6,8}\b|\b\d{8,9}\b|\b[A-Z]\d{7,8}\b|\b\d{2,3}-\d{2,3}-\d{4,6}\b)',
        # Passport number patterns
        "passport": r'(?i:(?:Passport|Pass\.?)(?:\s+(?:Number|No\.?|#))?[\s:]*)?(?:\b[A-Z]{1,2}\d{6,9}\b|\b\d{8,9}\b)',
        # Bank account numbers
        "bank_account": r'(?i:(?:Account|Acct)(?:\s+(?:Number|No\.?|#))?[\s:]*)?(?:\b\d{8,17}\b)',
        # IP addresses (IPv4 and IPv6)
        "ip_address": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',
        # Medical record numbers
        "medical_record": r'(?i:(?:Medical\s+Record|MRN|Patient\s+ID)[\s#:]*)?(?:\b[A-Z]{2,3}\d{6,10}\b|\b\d{7,12}\b)',
        # Employee ID
        "employee_id": r'(?i:(?:Employee|EMP|Staff)\s+(?:ID|Number)[\s#:]*)?(?:\b[A-Z]{2,4}\d{4,8}\b|\b\d{6,10}\b)',
        # License plate numbers
        "license_plate": r'(?i:(?:License\s+Plate|Plate)[\s#:]*)?(?:\b[A-Z]{1,3}[-\s]?\d{1,4}[-\s]?[A-Z]{0,3}\b|\b\d{1,3}[-\s]?[A-Z]{2,3}[-\s]?\d{1,4}\b)',
        # Vehicle VIN
        "vin": r'(?i:(?:VIN|Vehicle\s+Identification)[\s#:]*)?(?:\b[A-HJ-NPR-Z0-9]{17}\b)',
        # Insurance policy numbers
        "insurance_policy": r'(?i:(?:Policy|Insurance)(?:\s+(?:Number|No\.?|#))?[\s:]*)?(?:\b[A-Z]{2,4}\d{6,12}\b|\b\d{8,15}\b)',
        # Tax ID / EIN
        "tax_id": r'(?i:(?:Tax\s+ID|EIN|Employer\s+Identification)[\s#:]*)?(?:\b\d{2}-\d{7}\b)',
        # Credit score
        "credit_score": r'(?i:(?:Credit\s+Score|FICO|Score)[\s:]*)?(?:\b[3-8]\d{2}\b)',
        # Biometric data references
        "biometric": r'(?i:(?:Fingerprint|Biometric|Retina|DNA)(?:\s+(?:ID|Data))?[\s#:]*)?(?:\b[A-Z0-9]{8,20}\b)',
        # URLs with personal information
        "personal_url": r'https?://(?:www\.)?(?:facebook|linkedin|twitter|instagram|github)\.com/[A-Za-z0-9._-]+',
        # MAC addresses
        "mac_address": r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b',
        # GUID/UUID
        "guid": r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
    }
    
    # Default replacement tags
    DEFAULT_TAGS = {
        "email": "[REDACTED_EMAIL]",
        "phone": "[REDACTED_PHONE]",
        "credit_card": "[REDACTED_CREDIT_CARD]",
        "name": "[REDACTED_NAME]",
        "address": "[REDACTED_ADDRESS]",
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
    
    @classmethod
    def _is_likely_name(cls, text: str) -> bool:
        """
        Validate if a text match is likely to be a person's name
        
        Args:
            text: The matched text to validate
            
        Returns:
            Boolean indicating if text is likely a name
        """
        # Split the text into parts
        parts = text.split()
        if len(parts) < 2 or len(parts) > 4:
            return False
        
        # Check first and last names against common names
        first_name = parts[0].lower()
        last_name = parts[-1].lower()
        
        # If both first and last names are in our common lists, it's likely a name
        if first_name in cls.COMMON_FIRST_NAMES and last_name in cls.COMMON_LAST_NAMES:
            return True
        
        # If at least one name matches and follows typical name patterns
        if (first_name in cls.COMMON_FIRST_NAMES or last_name in cls.COMMON_LAST_NAMES):
            # Check if all parts are properly capitalized
            for part in parts:
                if not part[0].isupper() or not part[1:].islower():
                    # Allow for middle initials
                    if len(part) == 2 and part.endswith('.'):
                        continue
                    return False
            return True
        
        # Check for common name patterns even if not in our lists
        # All parts should be 2+ chars, properly capitalized, and alphabetic (with apostrophes/hyphens)
        for part in parts:
            if len(part) < 2:
                if not (len(part) == 2 and part.endswith('.')):  # Allow middle initials
                    return False
            if not part[0].isupper():
                return False
            # Allow letters, apostrophes, and hyphens in names
            if not all(c.isalpha() or c in "'-." for c in part):
                return False
        
        return True
    
    @classmethod
    def _is_likely_organization(cls, text: str) -> bool:
        """
        Check if text is likely an organization name (to avoid false positives)
        
        Args:
            text: The matched text to validate
            
        Returns:
            Boolean indicating if text is likely an organization
        """
        org_indicators = {
            'company', 'corp', 'corporation', 'inc', 'llc', 'ltd', 'limited',
            'hospital', 'medical', 'center', 'clinic', 'university', 'college',
            'school', 'bank', 'insurance', 'service', 'services', 'solutions',
            'group', 'associates', 'partners', 'firm', 'office', 'department',
            'division', 'team', 'organization', 'foundation', 'institute',
            'authority', 'agency', 'commission', 'board', 'council', 'committee'
        }
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in org_indicators)

    @classmethod
    def _validate_pii_match(cls, text: str, pii_type: str) -> bool:
        """
        Enhanced validation for PII matches to reduce false positives
        
        Args:
            text: The matched text to validate
            pii_type: The type of PII being validated
            
        Returns:
            Boolean indicating if match is valid
        """
        text_lower = text.lower().strip()
        
        # Apply specific validations based on PII type
        if pii_type == "name":
            return cls._is_likely_name(text) and not cls._is_likely_organization(text)
        
        elif pii_type == "credit_score":
            # Credit scores are typically 300-850
            try:
                score = int(text)
                return 300 <= score <= 850
            except ValueError:
                return False
        
        elif pii_type == "ip_address":
            # Basic validation for private/public IP ranges
            parts = text.split('.')
            if len(parts) == 4:
                try:
                    # Skip obviously invalid IPs like 0.0.0.0, 255.255.255.255
                    return not (all(p == '0' for p in parts) or all(p == '255' for p in parts))
                except:
                    return False
            return True  # IPv6 addresses
        
        elif pii_type == "phone":
            # Remove formatting and check if it's a valid phone number length
            digits_only = ''.join(filter(str.isdigit, text))
            return 10 <= len(digits_only) <= 15
        
        elif pii_type == "drivers_license":
            # Skip common false positives
            false_positives = {'test', 'example', 'sample', 'dummy'}
            return text_lower not in false_positives
        
        elif pii_type == "bank_account":
            # Skip obviously invalid account numbers
            if text.isdigit() and (len(set(text)) == 1 or text in ['12345678', '87654321']):
                return False
            return True
        
        return True

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
                    match_text = match.group()
                    
                    # Apply enhanced validation to reduce false positives
                    if not cls._validate_pii_match(match_text, pii_type):
                        continue
                    
                    matches.append(RedactionMatch(
                        start=match.start(),
                        end=match.end(),
                        text=match_text,
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
    def clean_overlapping_redactions(cls, text: str) -> str:
        """
        Clean up overlapping or duplicate redaction tags
        
        Args:
            text: Text with potentially overlapping redaction tags
            
        Returns:
            Cleaned text with non-overlapping redaction tags
        """
        # Pattern to match consecutive redaction tags
        pattern = r'\[REDACTED_[A-Z_]+\](\s*\[REDACTED_[A-Z_]+\])+'
        
        def replace_consecutive(match):
            # Replace consecutive tags with a single generic tag
            return '[REDACTED]'
        
        # Replace consecutive redaction tags
        cleaned_text = re.sub(pattern, replace_consecutive, text)
        
        # Remove extra spaces around redaction tags
        cleaned_text = re.sub(r'\s+\[REDACTED', ' [REDACTED', cleaned_text)
        cleaned_text = re.sub(r'\]\s+', '] ', cleaned_text)
        
        return cleaned_text

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of PII types supported by regex patterns"""
        return list(cls.PATTERNS.keys())

    @classmethod
    def is_type_supported(cls, pii_type: str) -> bool:
        """Check if a PII type is supported by regex patterns"""
        return pii_type in cls.PATTERNS

    @classmethod  
    def get_critical_pii_types(cls) -> List[str]:
        """Get list of critical PII types that should always be checked"""
        return [
            "ssn", "credit_card", "bank_account", "passport", "drivers_license",
            "medical_record", "tax_id", "biometric"
        ]
    
    @classmethod
    def get_common_pii_types(cls) -> List[str]:
        """Get list of commonly found PII types"""
        return [
            "name", "email", "phone", "address", "date", "ssn", 
            "credit_card", "drivers_license", "ip_address"
        ]