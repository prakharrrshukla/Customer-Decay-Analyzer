#!/bin/bash

# Customer Decay Analyzer - Automated Setup Script
# This script sets up the complete development environment

set -e  # Exit on error

echo "=========================================="
echo "Customer Decay Analyzer - Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.9+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python version must be 3.9 or higher${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✓${NC} pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file not found"
    echo "Creating .env template..."
    cat > .env << EOF
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Qdrant Configuration
QDRANT_URL=https://your-instance.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# Flask Configuration
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
EOF
    echo -e "${GREEN}✓${NC} .env template created"
    echo -e "${YELLOW}⚠${NC} Please edit .env with your API keys before running the application"
    echo ""
else
    echo -e "${GREEN}✓${NC} .env file already exists"
    echo ""
fi

# Create data directory
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
    echo -e "${GREEN}✓${NC} Data directory created"
    echo ""
fi

# Check if data files exist
DATA_EXISTS=false
if [ -f "data/customers.csv" ] && [ -f "data/behavior_events.csv" ] && [ -f "data/churned_customers.csv" ]; then
    DATA_EXISTS=true
    echo -e "${GREEN}✓${NC} Sample data already exists"
    echo ""
fi

# Verify setup
echo "=========================================="
echo "Verifying setup..."
echo "=========================================="
python scripts/verify_setup.py
echo ""

# Generate sample data (optional)
if [ "$DATA_EXISTS" = false ]; then
    read -p "Generate sample data now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Generating sample data..."
        python scripts/generate_sample_data.py
        echo -e "${GREEN}✓${NC} Sample data generated"
        echo ""
    fi
fi

# Final instructions
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure API keys in .env file:"
echo "   - Get Gemini API key: https://makersuite.google.com/app/apikey"
echo "   - Get Qdrant credentials: https://cloud.qdrant.io"
echo ""
echo "2. Test API connections:"
echo "   python scripts/test_connections.py"
echo ""
echo "3. Populate Qdrant vector database:"
echo "   python scripts/populate_qdrant.py"
echo ""
echo "4. Run tests:"
echo "   python tests/test_pipeline.py"
echo ""
echo "5. Start the server:"
echo "   python app.py"
echo ""
echo "6. Access the API:"
echo "   http://localhost:5000/api/health"
echo ""
echo "Documentation:"
echo "   - README.md - Getting started guide"
echo "   - API_DOCS.md - Complete API reference"
echo "   - RUN_TESTS.md - Testing guide"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
