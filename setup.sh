#!/bin/bash
# Setup and run the Sydney Rent Prediction system

set -e

echo "================================================"
echo "Sydney Rent Prediction - Setup Script"
echo "================================================"

# Check Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Ensure data files are in ./data/"
echo "2. Train models: python3 src/pipeline.py --data-path ./data"
echo "3. Launch Streamlit: cd src/streamlit_app && streamlit run app.py"
echo ""
