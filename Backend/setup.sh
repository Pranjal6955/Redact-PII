#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script's directory
cd "$SCRIPT_DIR"

echo "🚀 Setting up PII Redaction API"
echo "================================"

# Check if Python 3.8+ is installed
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
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

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
        echo "⚠️  Ollama is installed but not running"
        echo "   Start Ollama with: ollama serve"
    fi
else
    echo "⚠️  Ollama is not installed"
    echo "   Install Ollama from: https://ollama.ai/"
    echo "   Or run: curl -fsSL https://ollama.ai/install.sh | sh"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Ollama: ollama serve"
echo "2. Pull a model: ollama pull mistral"
echo "3. Start the API: python run.py"
echo "4. Test the API: python test_api.py"
echo "5. View docs: http://localhost:8000/docs"
echo ""
echo "Happy redacting! 🛡️"

# Change back to the original directory
cd - > /dev/null 