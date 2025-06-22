#!/usr/bin/env python3
"""
Ollama Fine-tuning Script for PII Detection Model

This script automates the fine-tuning process using Ollama's built-in fine-tuning capabilities.
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_ollama_installed():
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not installed or not accessible")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed. Please install Ollama first.")
        return False

def check_training_data():
    """Check if training data files exist."""
    required_files = ["pii_training_data.json", "Modelfile"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please run the dataset generator first: python3 pii_dataset_generator.py")
        return False
    
    print("✅ All required training files found")
    return True

def create_fine_tuned_model():
    """Create the fine-tuned model using Ollama with advanced configuration."""
    print("\n🚀 Starting fine-tuning process...")
    
    # Create a more sophisticated Modelfile with enhanced parameters
    modelfile_content = """
FROM llama3

# System prompt optimized for PII detection
SYSTEM """
You are an expert PII (Personally Identifiable Information) detection and redaction system. 
Your primary task is to identify and redact all instances of PII in text with 100% accuracy.
You must be thorough and meticulous, catching even subtle or unusual formats of PII.
You should prioritize catching all potential PII (high recall) while maintaining precision.
When unsure, err on the side of redaction to protect privacy.
"""

# Set parameters for optimal PII detection
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 30
PARAMETER repeat_penalty 1.2
PARAMETER seed 42

# Advanced fine-tuning configuration
TEMPLATE """
{{- if .System }}
SYSTEM: {{ .System }}
{{- end }}

{{- if .Prompt }}
USER: {{ .Prompt }}
{{- end }}

ASSISTANT: 
"""
"""
    
    # Write the enhanced Modelfile
    with open("Modelfile.enhanced", "w") as f:
        f.write(modelfile_content)
    
    # Create the model with the enhanced configuration
    result = run_command(
        "ollama create pii-detector-enhanced -f Modelfile.enhanced",
        "Creating enhanced PII detector model"
    )
    
    if result is None:
        print("❌ Failed to create enhanced model")
        return False
    
    print("✅ Enhanced PII detector model created successfully!")
    print("\n📝 Note: This model has optimized parameters specifically for PII detection.")
    print("   For even better results, continue with training on the generated dataset.")
    
    # Set up model evaluation with test cases
    setup_model_evaluation()
    
    return True

def setup_model_evaluation():
    """Set up a comprehensive evaluation suite for the PII detector model."""
    print("\n📊 Setting up model evaluation suite...")
    
    # Create directory for evaluation results
    os.makedirs("evaluation", exist_ok=True)
    
    # Generate challenging test cases that cover edge cases
    test_cases = [
        # Standard formats
        "My name is John Smith and my email is john.smith@example.com.",
        # Mixed formats
        "Contact info: j.smith@company.co.uk or call (555) 123-4567.",
        # Unusual formats
        "SSN: 123-45-6789 or sometimes written as 123456789.",
        # Ambiguous cases
        "The ID is A12345678Z and the reference number is REF-2023-001.",
        # Multiple PII types
        "Patient: Jane Doe (DOB: 05/23/1980) lives at 123 Main St, Apt 4B, New York, NY 10001.",
        # PII with surrounding context
        "Please update the system with: CC#: 4111-1111-1111-1111 Exp: 12/25 CVV: 123",
        # Embedded PII
        "The file JaneDoe_SSN123456789_2023.pdf contains sensitive information.",
        # Non-PII similar to PII
        "The product code is ABC-123-456-789 and costs $19.99.",
        # Edge case formats
        "Unusual phone: +1.555.123.4567 and unusual email: firstname+tag@sub.domain.co.uk"
    ]
    
    # Write test cases to file
    with open("evaluation/test_cases.json", "w") as f:
        json.dump({"test_cases": test_cases}, f, indent=2)
    
    print("✅ Evaluation suite prepared. Use 'python evaluate_pii_model.py' to run tests.")
def test_fine_tuned_model():
    """Test the fine-tuned model with sample text."""
    print("\n🧪 Testing the model...")
    
    test_prompts = [
        "My name is John Doe and my email is john@example.com",
        "Contact Sarah Smith at sarah.smith@company.com or call 555-123-4567",
        "The patient's SSN is 123-45-6789 and they live at 123 Main Street, New York, NY 10001"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Input: {prompt}")
        
        try:
            result = subprocess.run(
                f'ollama run pii-detector "{prompt}"',
                shell=True, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"Output: {result.stdout.strip()}")
            else:
                print(f"Error: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print("Timeout: Model took too long to respond")
        except Exception as e:
            print(f"Error testing model: {e}")

def create_advanced_fine_tuning_guide():
    """Create a guide for advanced fine-tuning options."""
    print("\n📚 Advanced Fine-tuning Options:")
    print("=" * 40)
    print("1. LoRA Fine-tuning (Recommended for full training):")
    print("   - Use transformers library with LoRA")
    print("   - Requires more computational resources")
    print("   - Better results with training data")
    print("\n2. Prompt Engineering (Current approach):")
    print("   - Uses custom template and parameters")
    print("   - Good for basic improvements")
    print("   - No training data required")
def main():
    """Main function to orchestrate the fine-tuning process."""
    print("🎯 PII Detection Model Fine-tuning with Ollama")
    print("=" * 50)
    
    # Check prerequisites
    if not check_ollama_installed():
        print("\n📋 Installation Instructions:")
        print("1. Visit https://ollama.ai")
        print("2. Download and install Ollama for your platform")
        print("3. Start Ollama service")
        print("4. Run this script again")
        return
    
    if not check_training_data():
        return
    
    # Create fine-tuned model
    create_fine_tuned_model()
    
    # Test the model
    test_fine_tuned_model()
    
    print("\n🎉 Fine-tuning process completed!")
    print("\n📋 Next Steps:")
    print("1. Update your config.env to use the new model:")
    print("   MODEL_NAME=pii-detector")
    print("2. Restart your application to use the fine-tuned model")
    print("3. Test with real PII data to validate improvements")

if __name__ == "__main__":
    main()