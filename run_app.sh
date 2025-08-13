#!/bin/bash

echo "🚀 Starting Succession Planning Tool - Minimal Version..."
echo "=============================================================="

# Check if virtual environment exists, if not suggest creating one
if [ ! -d "../.venv" ]; then
    echo "⚠️  Virtual environment not found at ../.venv"
    echo "💡 Consider creating one with: python -m venv ../.venv"
    echo "📦 Installing requirements globally..."
    pip install -r requirements.txt
else
    echo "🔧 Activating virtual environment..."
    source ../.venv/bin/activate
    echo "📦 Installing requirements..."
    pip install -q -r requirements.txt
fi

echo "✅ Minimal succession planning app ready"
echo "📁 Clean modular structure with essential files only"
echo "🔧 Same functionality, minimal footprint"
echo "🗄️ Uses both succession_db.sqlite and succession_plans.sqlite"
echo ""
echo "📱 The app will open in your browser automatically"
echo "Press Ctrl+C to stop the server"
echo "=============================================================="

# Run the app
streamlit run main.py --server.port 8507 --server.address localhost
