#!/bin/bash

# Streamlit Document Q&A System Startup Script

echo "🚀 Starting Document Q&A Streamlit Dashboard..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please check your Python environment."
        exit 1
    fi
    echo "✅ Dependencies installed successfully!"
else
    echo "⚠️  requirements.txt not found. Skipping dependency installation."
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f "env_example.txt" ]; then
        cp env_example.txt .env
        echo "📝 Please edit .env file and add your API keys before running the application."
    else
        echo "❌ env_example.txt not found. Please create .env file manually."
    fi
fi

# Check if Tesseract is installed (required for OCR)
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found. Please install Tesseract for OCR functionality:"
    echo "   macOS: brew install tesseract"
    echo "   Ubuntu: sudo apt-get install tesseract-ocr"
    echo "   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

echo ""
echo "🎉 Starting Streamlit dashboard..."
echo "📱 The dashboard will open in your default browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start Streamlit
streamlit run streamlit_app.py
