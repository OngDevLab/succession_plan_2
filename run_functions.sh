#!/bin/bash

echo "🚀 Starting Succession Planning Tool - Pure Functions Version..."
echo "=============================================================="

# Activate virtual environment
source ../.venv/bin/activate

# Install requirements including PyYAML
echo "📦 Installing requirements..."
pip install -q -r requirements.txt

# Copy both database files
echo "📁 Copying database files..."
cp ../succession_db.sqlite . 2>/dev/null && echo "✅ Copied employee database"
cp ../succession_plans.sqlite . 2>/dev/null && echo "✅ Copied succession plans database"
cp ../people_insights_logo.png . 2>/dev/null && echo "✅ Copied logo file"

echo "✅ Pure function-based modularization with YAML config"
echo "📁 No classes - just your app_final.py split into functions"
echo "🔧 Exact same logic, just organized into modules"
echo "📄 Configuration now in clean YAML format"
echo "🗄️ Uses both succession_db.sqlite and succession_plans.sqlite"
echo ""
echo "📱 The app will open in your browser automatically"
echo "Press Ctrl+C to stop the server"
echo "=============================================================="

# Run the functions app
streamlit run main.py --server.port 8506 --server.address localhost
