#!/usr/bin/env bash
# render-build.sh

echo "Starting Render build process..."

# Install system dependencies for OCR
apt-get update
apt-get install -y tesseract-ocr
apt-get install -y tesseract-ocr-eng
apt-get install -y libgl1-mesa-glx  # For OpenCV
apt-get install -y libglib2.0-0     # For OpenCV

# Verify installations
echo "Tesseract version:"
tesseract --version

echo "Python packages:"
pip install -r requirements.txt

echo "Build complete!"