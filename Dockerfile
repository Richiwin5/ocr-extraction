FROM python:3.9-slim

# Install Tesseract and OpenCV dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create necessary directories
RUN mkdir -p temp extracted_photos

# Use server:app directly (no wsgi.py needed)
CMD gunicorn server:app --bind 0.0.0.0:$PORT --timeout 120