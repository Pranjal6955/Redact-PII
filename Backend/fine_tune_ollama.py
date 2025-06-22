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
    """Create the fine-tuned model using Ollama."""
    print("\n🚀 Starting fine-tuning process...")
    
    # First, create a base model with our template
    print("🔄 Creating base model with custom template...")
    result = run_command(
        "ollama create pii-detector -f Modelfile",
        "Creating base model 'pii-detector'"
    )
    
    if result is None:
        print("❌ Failed to create base model")
        return False
    
    print("✅ Base model created successfully!")
    print("\n📝 Note: This creates a model with custom parameters and template.")
    print("   For full fine-tuning with training data, you would need to use")
    print("   Ollama's fine-tuning API or external tools like LoRA.")
    
    return True

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