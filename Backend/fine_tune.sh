#!/bin/bash

# PII Detection Model Fine-tuning Script
# This script performs fine-tuning using Ollama's built-in capabilities

set -e  # Exit on any error

echo "🎯 PII Detection Model Fine-tuning with Ollama"
echo "=================================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama first:"
    echo "   Visit https://ollama.ai"
    exit 1
fi

echo "✅ Ollama is installed: $(ollama --version)"

# Check if required files exist
if [ ! -f "pii_training_data.json" ]; then
    echo "❌ Training data file 'pii_training_data.json' not found"
    echo "   Please run the dataset generator first: python3 pii_dataset_generator.py"
    exit 1
fi

if [ ! -f "Modelfile" ]; then
    echo "❌ Modelfile not found"
    exit 1
fi

echo "✅ All required files found"

# Create the fine-tuned model
echo ""
echo "🚀 Creating fine-tuned model 'pii-detector'..."
ollama create pii-detector -f Modelfile

echo "✅ Fine-tuning completed successfully!"

# Test the model
echo ""
echo "🧪 Testing the fine-tuned model..."

test_prompts=(
    "My name is John Doe and my email is john@example.com"
    "Contact Sarah Smith at sarah.smith@company.com or call 555-123-4567"
    "The patient's SSN is 123-45-6789 and they live at 123 Main Street, New York, NY 10001"
)

for i in "${!test_prompts[@]}"; do
    echo ""
    echo "--- Test $((i+1)) ---"
    echo "Input: ${test_prompts[$i]}"
    echo "Output: $(ollama run pii-detector "${test_prompts[$i]}")"
done

echo ""
echo "🎉 Fine-tuning process completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your config.env to use the new model:"
echo "   MODEL_NAME=pii-detector"
echo "2. Restart your application to use the fine-tuned model"
echo "3. Test with real PII data to validate improvements" 