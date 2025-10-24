#!/bin/bash

# Document Q&A System Startup Script

echo "🚀 Starting Document Q&A System..."

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

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo ""
echo "🎉 Setup complete! You can now:"
echo ""
echo "1. 🌐 Start the web interface:"
echo "   python3 app.py"
echo "   Then open http://localhost:8000 in your browser"
echo ""
echo "2. 💻 Use the CLI interface:"
echo "   python3 cli.py --interactive"
echo ""
echo "3. 📄 Test with the example document:"
echo "   python3 cli.py --file example_document.txt --question 'What services does TechCorp offer?'"
echo ""
echo "📚 For more information, see README.md"
