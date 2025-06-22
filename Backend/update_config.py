#!/usr/bin/env python3
"""
Configuration Update Script for Fine-tuned PII Detection Model

This script updates the config.env file to use the fine-tuned model.
"""

import os
import re

def update_config_file():
    """Update the config.env file to use the fine-tuned model."""
    config_file = "config.env"
    
    if not os.path.exists(config_file):
        print(f"❌ Config file {config_file} not found")
        return False
    
    # Read the current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Update the MODEL_NAME
    updated_content = re.sub(
        r'MODEL_NAME=.*',
        'MODEL_NAME=pii-detector',
        content
    )
    
    # Write the updated config
    with open(config_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ Configuration updated successfully!")
    print("   MODEL_NAME changed from 'mistral' to 'pii-detector'")
    return True

def main():
    """Main function."""
    print("🔧 Updating configuration for fine-tuned model...")
    
    if update_config_file():
        print("\n📋 Configuration updated!")
        print("   The application will now use the fine-tuned 'pii-detector' model")
        print("   Restart your application to apply the changes")
    else:
        print("❌ Failed to update configuration")

if __name__ == "__main__":
    main() 