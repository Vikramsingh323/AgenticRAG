#!/bin/bash

# RAG Chatbot - Quick Setup Script
# This script installs all dependencies and starts the application

set -e

echo "🚀 RAG Chatbot Setup"
echo "===================="
echo ""

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found!"
    echo "Install with: brew install node"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found!"
    echo "Install with: brew install python"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ Python version: $(python3 --version)"
echo ""

# Navigate to project
cd "$(dirname "$0")" || exit

# Install dependencies
echo "📦 Installing dependencies..."
npm install > /dev/null 2>&1
echo "✅ Dependencies installed"
echo ""

# Setup environment
if [ ! -f .env.local ]; then
    echo "⚙️  Setting up environment..."
    cp .env.example .env.local
    echo "✅ Created .env.local (please edit if needed)"
    echo ""
fi

# Start application
echo "🎯 Starting RAG Chatbot..."
echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev
