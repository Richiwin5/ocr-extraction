# app.py
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import shutil
import logging
import sys
from app.ocr.ocr_engine import extract_text
from flask_cors import CORS



app = Flask(__name__)
CORS(app) 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix for Render - Make sure Tesseract is found
try:
    import pytesseract
    import subprocess
    
    # Check if tesseract is in PATH
    try:
        result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
        if result.returncode == 0:
            tesseract_path = result.stdout.strip()
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f" Tesseract found at: {tesseract_path}")
            
            # Test Tesseract
            version = subprocess.check_output(['tesseract', '--version'], text=True)
            logger.info(f" Tesseract version: {version.split(chr(10))[0]}")
        else:
            logger.error(" Tesseract not found in PATH")
    except Exception as e:
        logger.error(f" Error finding Tesseract: {e}")
        
except ImportError as e:
    logger.error(f"pytesseract import error: {e}")
# Initialize Flask app




# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['PHOTOS_FOLDER'] = 'extracted_photos'
app.config['ALLOWED_EXTENSIONS'] = {'.jpg', '.jpeg', '.png', '.pdf'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PHOTOS_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'ID Document OCR API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/extract-id', methods=['POST'])
def extract_id():
    """Extract information from ID document"""
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Only {", ".join(app.config["ALLOWED_EXTENSIONS"])} files are allowed'
        }), 400
    
    try:
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1].lower()
        temp_filename = f"{uuid.uuid4()}{ext}"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        # Save uploaded file
        file.save(temp_path)
        
        # Process document
        result = extract_text(temp_path)
        
        if "error" in result:
            return jsonify({'error': result["error"]}), 500
        
        # Prepare response
        response_data = {
            'success': True,
            'filename': file.filename,
            'document_type': result.get('document_type', 'unknown'),
            'confidence': result.get('classification_confidence', 0),
            'country': result.get('country', 'unknown'),
            'fields': result.get('fields', {}),
        }
        
        # Add photo info if available
        if result.get('photo_path'):
            photo_filename = os.path.basename(result['photo_path'])
            response_data['profile_photo'] = {
                'filename': photo_filename,
                'url': f"/photos/{photo_filename}",
                'path': result['photo_path']
            }
        
        # Clean up temp file (optional)
        # os.remove(temp_path)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/photos/<filename>', methods=['GET'])
def get_photo(filename):
    """Serve extracted photos"""
    # Security: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    photo_path = os.path.join(app.config['PHOTOS_FOLDER'], filename)
    
    if not os.path.exists(photo_path):
        return jsonify({'error': 'Photo not found'}), 404
    
    return send_file(photo_path, mimetype='image/jpeg')

@app.route('/document-types', methods=['GET'])
def get_document_types():
    """Get list of supported document types"""
    return jsonify({
        'supported_documents': [
            {
                'type': 'voters_card',
                'name': "Nigerian Voter's Card",
                'fields': ['vin', 'full_name', 'date_of_birth', 'occupation', 'address', 'state', 'lga', 'ward', 'polling_unit']
            },
            {
                'type': 'nin',
                'name': 'National Identification Number (NIN)',
                'fields': ['nin', 'full_name', 'surname', 'first_name', 'middle_name', 'date_of_birth', 'gender', 'address', 'phone_number']
            },
            {
                'type': 'international_passport',
                'name': 'International Passport',
                'fields': ['passport_number', 'full_name', 'surname', 'first_name', 'middle_name', 'nationality', 'date_of_birth', 'place_of_birth', 'issue_date', 'expiry_date', 'gender']
            },
            {
                'type': 'drivers_license',
                'name': "Driver's License",
                'fields': ['license_number', 'full_name', 'surname', 'first_name', 'middle_name', 'date_of_birth', 'issue_date', 'expiry_date', 'vehicle_categories', 'blood_group', 'address', 'height']
            }
        ]
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))
    app.run(host='0.0.0.0', port=port, debug=False)