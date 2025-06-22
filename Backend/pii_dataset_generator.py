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

    def generate_sentence_with_pii(self, pii_types: List[str]) -> Tuple[str, str]:
        templates = [
            "My name is {name} and you can contact me at {email}.",
            "Please call {name} at {phone} for more information.",
            "I live at {address} and my credit card is {credit_card}.",
            "Contact {name} via email at {email} or phone at {phone}.",
            "I was born on {date} and my name is {name}."
        ]
        
        template = random.choice(templates)
        original_text = template
        redacted_text = template
        
        if "name" in pii_types:
            name = self.generate_random_name()
            original_text = original_text.replace("{name}", name)
            redacted_text = redacted_text.replace("{name}", "[REDACTED_NAME]")
        
        if "email" in pii_types:
            email = self.generate_random_email()
            original_text = original_text.replace("{email}", email)
            redacted_text = redacted_text.replace("{email}", "[REDACTED_EMAIL]")
        
        if "phone" in pii_types:
            phone = self.generate_random_phone()
            original_text = original_text.replace("{phone}", phone)
            redacted_text = redacted_text.replace("{phone}", "[REDACTED_PHONE]")
        
        if "address" in pii_types:
            address = self.generate_random_address()
            original_text = original_text.replace("{address}", address)
            redacted_text = redacted_text.replace("{address}", "[REDACTED_ADDRESS]")
        
        if "credit_card" in pii_types:
            credit_card = self.generate_random_credit_card()
            original_text = original_text.replace("{credit_card}", credit_card)
            redacted_text = redacted_text.replace("{credit_card}", "[REDACTED_CREDIT_CARD]")
        
        if "date" in pii_types:
            date = self.generate_random_date()
            original_text = original_text.replace("{date}", date)
            redacted_text = redacted_text.replace("{date}", "[REDACTED_DATE]")
        
        return original_text, redacted_text

    def generate_dataset(self, num_samples: int = 1000) -> List[Dict]:
        dataset = []
        all_pii_types = ["name", "email", "phone", "address", "credit_card", "date"]
        
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

REPLACEMENT MAPPING:
- name → [REDACTED_NAME]
- email → [REDACTED_EMAIL]
- phone → [REDACTED_PHONE]
- address → [REDACTED_ADDRESS]
- credit_card → [REDACTED_CREDIT_CARD]
- date → [REDACTED_DATE]

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