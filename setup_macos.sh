#!/bin/bash

# Modular Agentic System - macOS Setup Script
# Sets up the full standalone application on macOS

set -e  # Exit on error

echo "======================================================================"
echo "  MODULAR AGENTIC SYSTEM - macOS Setup"
echo "  World-Class AI Content Generation System"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9 or higher is required. Found: $python_version"
    echo "Please install Python 3.9+ from https://www.python.org"
    exit 1
fi

echo "✅ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Failed to install some dependencies"
    echo "Please check the error messages above"
    exit 1
fi
echo ""

# Create necessary directories
echo "Creating system directories..."
mkdir -p outputs
mkdir -p data/vector_store
mkdir -p data/knowledge_graphs
mkdir -p data/cache
mkdir -p data/learning
mkdir -p logs
mkdir -p config

echo "✅ Directories created"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your Anthropic API key!"
        echo "   Open .env and set: ANTHROPIC_API_KEY=your-key-here"
    else
        echo "Creating new .env file..."
        cat > .env << EOF
# Anthropic API Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: OpenAI API (for embeddings)
# OPENAI_API_KEY=your-openai-api-key-here

# System Configuration
LOG_LEVEL=INFO
CACHE_ENABLED=true
LEARNING_ENABLED=true

# Quality Thresholds
RESEARCH_QUALITY_THRESHOLD=8.0
VIRAL_QUALITY_THRESHOLD=9.0
CONTENT_QUALITY_THRESHOLD=9.0
EOF
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your Anthropic API key!"
    fi
else
    echo "✅ .env file already exists"
fi
echo ""

# Create config files if they don't exist
if [ ! -f "config/default_config.yaml" ]; then
    echo "Creating default configuration..."
    cat > config/default_config.yaml << 'EOF'
# Modular Agentic System - Configuration

system:
  name: "Modular Agentic System"
  version: "3.0"
  log_level: "INFO"

orchestrator:
  quality_threshold: 9.0
  max_iterations: 5
  enable_learning: true
  enable_caching: true

research:
  quality_threshold: 8.0
  max_papers: 50
  databases:
    - semantic_scholar
    - crossref
    - arxiv

viral_analysis:
  quality_threshold: 9.0
  hook_count: 10
  trigger_count: 16

content_synthesis:
  quality_threshold: 9.0
  max_tokens: 8192
  temperature: 0.7

intelligence:
  primary_model: "claude-sonnet-4-20250514"
  fallback_model: "claude-haiku-4-20250319"
  max_tokens: 8192
  temperature: 0.7

database:
  vector_store_path: "data/vector_store"
  knowledge_graph_path: "data/knowledge_graphs"
  cache_path: "data/cache"
  learning_path: "data/learning"
  cache_ttl: 3600
  max_cache_size: 1000
EOF
    echo "✅ Configuration files created"
else
    echo "✅ Configuration files already exist"
fi
echo ""

# Create macOS application launcher (optional)
echo "Creating macOS application launcher..."
cat > run_system.command << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 main.py "$@"
EOF

chmod +x run_system.command
echo "✅ Launcher created: run_system.command"
echo ""

# Test import
echo "Testing system imports..."
python3 << 'PYTHON_TEST'
try:
    import sys
    sys.path.insert(0, '.')

    # Test core imports
    from src.core.anthropic_client import AnthropicClient
    from src.intelligence import IntelligenceLayer
    from src.database import VectorDatabase
    from src.research import ResearchGatekeeper
    from src.viral_analysis import ViralAnalyserGatekeeper
    from src.orchestrator import MasterOrchestrator

    print("✅ All system modules imported successfully!")
    sys.exit(0)
except Exception as e:
    print(f"❌ Import test failed: {e}")
    sys.exit(1)
PYTHON_TEST

if [ $? -eq 0 ]; then
    echo ""
else
    echo "⚠️  Some modules failed to import. Please check the installation."
    exit 1
fi

echo "======================================================================"
echo "  ✅ SETUP COMPLETE!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env and add your Anthropic API key:"
echo "   nano .env"
echo ""
echo "2. Run the system in interactive mode:"
echo "   ./run_system.command"
echo "   or: source venv/bin/activate && python3 main.py"
echo ""
echo "3. Run with specific topic:"
echo "   python3 main.py --topic \"Your Topic\" --duration 15"
echo ""
echo "4. For help:"
echo "   python3 main.py --help"
echo ""
echo "======================================================================"
echo ""
echo "📚 Documentation: See ARCHITECTURE.md and docs/ folder"
echo "🚀 Ready to generate world-class content!"
echo ""
