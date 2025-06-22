#!/bin/bash

# Consolidated Setup and Execution Script for PII Redaction API

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script's directory
cd "$SCRIPT_DIR"

# --- HELP FUNCTION ---
show_help() {
    echo "Usage: $0 {install|start|fine-tune|test|all}"
    echo ""
    echo "Commands:"
    echo "  install      - Install system and Python dependencies."
    echo "  start        - Start the application (using Gunicorn for production or Uvicorn for development)."
    echo "  fine-tune    - Run the fine-tuning process for the Ollama model."
    echo "  test         - Run the PII detection test script."
    echo "  all          - Run install, then start the application."
    echo ""
    echo "This script consolidates setup, start, and fine-tuning operations."
}


# --- INSTALLATION FUNCTIONS ---

# Install system dependencies (for Debian-based systems like Render)
install_system_dependencies() {
    echo "==> Installing system dependencies..."
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y --no-install-recommends \
            tesseract-ocr \
            libmagic1 \
            libgl1 \
            python3-dev \
            python3-pip \
            python3-venv
        echo "✅ System dependencies installed."
    else
        echo "⚠️  apt-get not found. Skipping system dependency installation. This is expected on non-Debian systems (e.g., macOS, Windows)."
    fi
}

# Setup Python environment and install dependencies
setup_python_env() {
    echo "🚀 Setting up Python environment for PII Redaction API"
    echo "====================================================="

    # Check if Python 3.8+ is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    required_version="3.8"

    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
        echo "✅ Python $python_version detected (>= $required_version)"
    else
        echo "❌ Python 3.8+ is required. Current version: $python_version"
        exit 1
    fi

    # Check if pip is installed
    if command -v pip3 &> /dev/null; then
        echo "✅ pip3 is installed"
    else
        echo "❌ pip3 is not installed. Please install pip3 first."
        exit 1
    fi

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "❌ Failed to create virtual environment. Check Python installation."
            echo "Try installing python3-venv package if on Debian/Ubuntu:"
            echo "sudo apt-get install python3-venv"
            exit 1
        fi
        echo "✅ Virtual environment created"
    else
        echo "✅ Virtual environment already exists"
    fi

    # Activate virtual environment
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "❌ Failed to activate virtual environment."
        exit 1
    fi

    # Upgrade pip
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: Failed to upgrade pip, but continuing..."
    fi

    # Install dependencies
    echo "📚 Installing dependencies from requirements.txt..."
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        echo "❌ requirements.txt not found at $SCRIPT_DIR"
        exit 1
    fi
    
    pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        echo "Try installing python3-dev if on Debian/Ubuntu:"
        echo "sudo apt-get install python3-dev"
        exit 1
    fi
    echo "✅ Python dependencies installed."
    
    # Check if config.env exists
    if [ ! -f "config.env" ]; then
        echo "⚙️  Creating config.env from template..."
        cat > config.env << EOF
# Ollama Configuration
MODEL_NAME=mistral
OLLAMA_BASE_URL=http://localhost:11434

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# PII Detection Configuration
HYBRID_MODE_ENABLED=True
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
EOF
        echo "✅ config.env created"
    else
        echo "✅ config.env already exists"
    fi

    # Check if Ollama is installed
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama is installed"
        
        # Check if Ollama is running
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "✅ Ollama is running"
        else
            echo "⚠️  Ollama is installed but not running. Start it with: ollama serve"
        fi
    else
        echo "⚠️  Ollama is not installed. Install from https://ollama.ai/ or run: curl -fsSL https://ollama.ai/install.sh | sh"
    fi
}

run_install() {
    install_system_dependencies
    setup_python_env
    echo ""
    echo "🎉 Installation complete!"
    echo "Next, you can start the application with: ./setup.sh start"
}


# --- APPLICATION START FUNCTION ---
run_start() {
    echo "🚀 Starting PII Redaction API..."

    # Create necessary directories
    mkdir -p uploads outputs

    # Activate virtual environment
    if [ -d "venv" ]; then
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
        if [ $? -ne 0 ]; then
            echo "❌ Failed to activate virtual environment."
            exit 1
        fi
    else
        echo "❌ Virtual environment not found. Please run './setup.sh install' first."
        exit 1
    fi
    
    # Check if run.py exists
    if [ ! -f "run.py" ]; then
        echo "❌ run.py not found. Make sure you are in the correct directory."
        exit 1
    fi
    
    # Check if config.py exists (required by run.py)
    if [ ! -f "config.py" ]; then
        echo "❌ config.py not found. Make sure all required files are present."
        exit 1
    fi
    
    # Check if all required Python modules are present
    echo "🔍 Checking for required modules..."
    
    required_files=("regex_redactor.py" "pii_service.py" "ollama_client.py" "main.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "❌ Required file $file not found!"
            exit 1
        fi
    done
    
    # Check if we're in a production environment (like Render)
    if [ -n "$RENDER" ]; then
        echo "🌐 Production environment detected (Render)"
        echo "📝 Using gunicorn for production deployment"
        
        # Start with gunicorn for production
        exec gunicorn main:app -c gunicorn.conf.py
    else
        echo "🔧 Development environment detected"
        echo "📝 Using uvicorn for development"
        
        # Start with uvicorn for development
        exec python run.py
    fi 
}


# --- TEST FUNCTION ---
run_test() {
    echo "🧪 Running PII detection test script..."
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
        if [ $? -ne 0 ]; then
            echo "❌ Failed to activate virtual environment."
            exit 1
        fi
    else
        echo "❌ Virtual environment not found. Please run './setup.sh install' first."
        exit 1
    fi
    
    # Check if test script exists
    if [ ! -f "test_pii_detection.py" ]; then
        echo "❌ test_pii_detection.py not found. Create it first."
        exit 1
    fi
    
    # Run the test script
    python test_pii_detection.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Test completed successfully."
    else
        echo "❌ Test failed."
        exit 1
    fi
}


# --- FINE-TUNING FUNCTION ---
run_fine_tune() {
    set -e  # Exit on any error
    echo "🎯 PII Detection Model Fine-tuning with Ollama"
    echo "=================================================="

    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        echo "❌ Ollama is not installed. Please install Ollama first: https://ollama.ai"
        exit 1
    fi

    echo "✅ Ollama is installed: $(ollama --version)"
    
    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Ollama is not running. Please start Ollama with: ollama serve"
        exit 1
    fi

    # Check if required files exist
    if [ ! -f "Modelfile" ]; then
        echo "⚙️ Creating Modelfile for PII detection..."
        cat > Modelfile << EOF
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
EOF
        echo "✅ Modelfile created"
    else
        echo "✅ Modelfile exists"
    fi

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
    echo "1. Update your config.env to use the new model: MODEL_NAME=pii-detector"
    echo "2. Restart your application to use the fine-tuned model"
    
    # Ask if user wants to update config.env
    read -p "Would you like to update config.env to use the new model? (y/n) " answer
    if [[ $answer == [Yy]* ]]; then
        python update_config.py
    fi
}


# --- MAIN LOGIC ---
main() {
    if [ "$#" -ne 1 ]; then
        show_help
        exit 1
    fi

    case "$1" in
        install)
            run_install
            ;;
        start)
            run_start
            ;;
        fine-tune)
            run_fine_tune
            ;;
        test)
            run_test
            ;;
        all)
            run_install
            run_start
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# Execute main function with all script arguments
main "$@"

# Change back to the original directory (if not starting a server)
cd - > /dev/null