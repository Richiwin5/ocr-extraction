#!/usr/bin/env bash
# render-build.sh - This runs during Render deployment

echo "🚀 Starting Render build process..."
echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la

echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y tesseract-ocr
apt-get install -y tesseract-ocr-eng
apt-get install -y libgl1-mesa-glx
apt-get install -y libglib2.0-0

echo "✅ System dependencies installed"
echo "Tesseract version:"
tesseract --version

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete!"