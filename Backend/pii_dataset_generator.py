#!/usr/bin/env python3
"""
PII Dataset Generator for Fine-tuning Ollama Models
"""

import json
import random
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

class PIIDatasetGenerator:
    def __init__(self):
        self.first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
        self.email_domains = ["gmail.com", "yahoo.com", "hotmail.com", "company.com"]
        self.cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        self.states = ["CA", "NY", "TX", "FL", "IL"]

    def generate_random_name(self) -> str:
        return f"{random.choice(self.first_names)} {random.choice(self.last_names)}"

    def generate_random_email(self) -> str:
        name = random.choice(self.first_names).lower()
        domain = random.choice(self.email_domains)
        return f"{name}@{domain}"

    def generate_random_phone(self) -> str:
        return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

    def generate_random_address(self) -> str:
        street_num = random.randint(1, 9999)
        street_name = random.choice(["Main St", "Oak Ave", "Pine Rd", "Elm St"])
        city = random.choice(self.cities)
        state = random.choice(self.states)
        zip_code = f"{random.randint(10000, 99999)}"
        return f"{street_num} {street_name}, {city}, {state} {zip_code}"

    def generate_random_credit_card(self) -> str:
        return f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

    def generate_random_date(self) -> str:
        year = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{month}/{day}/{year}"

    def generate_random_ssn(self) -> str:
        return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    
    def generate_random_drivers_license(self) -> str:
        formats = [
            f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000000, 9999999)}",
            f"{random.randint(100000000, 999999999)}",
            f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100000, 999999)}"
        ]
        return random.choice(formats)
    
    def generate_random_ip_address(self) -> str:
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def generate_random_employee_id(self) -> str:
        return f"EMP{random.randint(100000, 999999)}"

    def generate_sentence_with_pii(self, pii_types: List[str]) -> Tuple[str, str]:
        templates = [
            "My name is {name} and you can contact me at {email}.",
            "Please call {name} at {phone} for more information.",
            "I live at {address} and my credit card is {credit_card}.",
            "Contact {name} via email at {email} or phone at {phone}.",
            "I was born on {date} and my name is {name}.",
            "My SSN is {ssn} and driver's license is {drivers_license}.",
            "Employee {name} (ID: {employee_id}) can be reached at {email}.",
            "Server IP {ip_address} hosts data for {name}.",
            "Medical record {medical_record} belongs to patient {name}."
        ]
        
        template = random.choice(templates)
        original_text = template
        redacted_text = template
        
        # Handle all PII types
        replacements = {
            "name": (self.generate_random_name, "[REDACTED_NAME]"),
            "email": (self.generate_random_email, "[REDACTED_EMAIL]"),
            "phone": (self.generate_random_phone, "[REDACTED_PHONE]"),
            "address": (self.generate_random_address, "[REDACTED_ADDRESS]"),
            "credit_card": (self.generate_random_credit_card, "[REDACTED_CREDIT_CARD]"),
            "date": (self.generate_random_date, "[REDACTED_DATE]"),
            "ssn": (self.generate_random_ssn, "[REDACTED_SSN]"),
            "drivers_license": (self.generate_random_drivers_license, "[REDACTED_DRIVERS_LICENSE]"),
            "ip_address": (self.generate_random_ip_address, "[REDACTED_IP_ADDRESS]"),
            "employee_id": (self.generate_random_employee_id, "[REDACTED_EMPLOYEE_ID]"),
            "medical_record": (lambda: f"MRN{random.randint(1000000, 9999999)}", "[REDACTED_MEDICAL_RECORD]")
        }
        
        for pii_type in pii_types:
            if pii_type in replacements and f"{{{pii_type}}}" in template:
                generator_func, redacted_tag = replacements[pii_type]
                value = generator_func()
                original_text = original_text.replace(f"{{{pii_type}}}", value)
                redacted_text = redacted_text.replace(f"{{{pii_type}}}", redacted_tag)
        
        return original_text, redacted_text

    def generate_dataset(self, num_samples: int = 1000) -> List[Dict]:
        dataset = []
        all_pii_types = [
            "name", "email", "phone", "address", "credit_card", "date", "ssn",
            "drivers_license", "ip_address", "employee_id", "medical_record"
        ]
        
        for i in range(num_samples):
            num_pii_types = random.randint(1, 4)
            selected_pii_types = random.sample(all_pii_types, num_pii_types)
            
            original_text, redacted_text = self.generate_sentence_with_pii(selected_pii_types)
            
            sample = {
                "id": i + 1,
                "original_text": original_text,
                "redacted_text": redacted_text,
                "pii_types": selected_pii_types
            }
            
            dataset.append(sample)
        
        return dataset

    def generate_training_prompts(self, dataset: List[Dict]) -> List[Dict]:
        training_data = []
        
        for sample in dataset:
            prompt = f"""You are a PII (Personally Identifiable Information) redaction expert. Your task is to identify and replace specific types of PII in the given text.

TYPES OF PII TO DETECT AND REDACT:
- name: personal names (first names, last names, full names, nicknames, aliases, maiden names)
- email: email addresses (any format: user@domain.com, user.name@domain.co.uk, etc.)
- phone: phone numbers (any format: 555-123-4567, (555) 123-4567, +1-555-123-4567, 555.123.4567, 5551234567)
- address: physical addresses (complete addresses including street, city, state/province, zip/postal code, country)
- credit_card: credit card numbers, debit card numbers (any format: 4111-1111-1111-1111, 4111 1111 1111 1111, 4111111111111111, etc.)
- date: personal dates (birth dates, anniversary dates, personal milestones, not general dates or holidays)
- ssn: Social Security Numbers (any format: 123-45-6789, 123-456-789, etc.)
- drivers_license: Driver's License numbers (various formats depending on the state or country)
- ip_address: IP addresses (any format: 192.168.1.1, 255.255.255.255, etc.)
- employee_id: Employee IDs (format: EMP123456)
- medical_record: Medical record numbers (format: MRN1234567)

REPLACEMENT MAPPING:
- name → [REDACTED_NAME]
- email → [REDACTED_EMAIL]
- phone → [REDACTED_PHONE]
- address → [REDACTED_ADDRESS]
- credit_card → [REDACTED_CREDIT_CARD]
- date → [REDACTED_DATE]
- ssn → [REDACTED_SSN]
- drivers_license → [REDACTED_DRIVERS_LICENSE]
- ip_address → [REDACTED_IP_ADDRESS]
- employee_id → [REDACTED_EMPLOYEE_ID]
- medical_record → [REDACTED_MEDICAL_RECORD]

CRITICAL INSTRUCTIONS:
1. CAREFULLY analyze the text and identify ALL instances of the specified PII types
2. Replace each identified PII with the corresponding replacement tag EXACTLY as shown
3. Maintain the original text structure, formatting, and punctuation
4. Be THOROUGH - it's better to redact something that might be PII than to miss it
5. For names: Redact first names, last names, full names, nicknames, aliases, maiden names, and middle names
6. For emails: Redact any email address format (user@domain.com, user.name@domain.co.uk, user+tag@domain.org, etc.)
7. For phones: Redact phone numbers in any format (555-123-4567, (555) 123-4567, +1-555-123-4567, 555.123.4567, 5551234567)
8. For addresses: Redact complete addresses including street, city, state/province, zip/postal code, country
9. For credit cards: Redact credit/debit card numbers (4111-1111-1111-1111, 4111 1111 1111 1111, 4111111111111111, etc.)
10. For dates: Focus on personal dates like birth dates, anniversary dates, personal milestones, not general dates or holidays
11. For SSNs: Redact Social Security Numbers in any format (123-45-6789, 123-456-789, etc.)
12. For driver's licenses: Redact Driver's License numbers in various formats
13. For IP addresses: Redact IP addresses in any format (192.168.1.1, 255.255.255.255, etc.)
14. For employee IDs: Redact Employee IDs (format: EMP123456)
15. For medical records: Redact Medical record numbers (format: MRN1234567)

IMPORTANT: Return ONLY the redacted text. Do not add any explanations, markdown formatting, or additional text.

INPUT TEXT:
{sample['original_text']}

REDACTED TEXT:"""

            training_example = {
                "prompt": prompt,
                "response": sample['redacted_text'],
                "metadata": {
                    "pii_types": sample['pii_types']
                }
            }
            
            training_data.append(training_example)
        
        return training_data

    def save_dataset(self, dataset: List[Dict], filename: str):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"Dataset saved to {filename}")

def main():
    generator = PIIDatasetGenerator()
    
    print("Generating PII dataset...")
    dataset = generator.generate_dataset(num_samples=2000)
    generator.save_dataset(dataset, "pii_dataset.json")
    
    print("Generating training prompts...")
    training_data = generator.generate_training_prompts(dataset)
    generator.save_dataset(training_data, "pii_training_data.json")
    
    # Create validation set
    validation_dataset = generator.generate_dataset(num_samples=200)
    validation_training_data = generator.generate_training_prompts(validation_dataset)
    generator.save_dataset(validation_training_data, "pii_validation_data.json")
    
    print("\nDataset generation complete!")
    print("Files created:")
    print("- pii_dataset.json: Raw dataset")
    print("- pii_training_data.json: Training prompts")
    print("- pii_validation_data.json: Validation set")

if __name__ == "__main__":
    main()