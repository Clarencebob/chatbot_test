#!/bin/bash

# Quick start script for Feishu RAG Chatbot

echo "🚀 Starting Feishu RAG Chatbot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run setup
echo "🔧 Running setup..."
python setup.py

# Check if .env file has been configured
if grep -q "your_app_id_here" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: Please update your .env file with actual credentials!"
    echo "Edit .env and replace the placeholder values."
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Start the application
echo "🎯 Starting FastAPI application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000