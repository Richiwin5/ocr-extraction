# app/ocr/ocr_engine.py
import cv2
import pytesseract
import os
import uuid
import numpy as np
from typing import Dict, Any
import logging

from app.ocr.document_classifier import DocumentClassifier
from app.ocr.extractors import (
    VotersCardExtractor,
    NINExtractor,
    PassportExtractor,
    DriversLicenseExtractor
)

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
class OCRAnalyticsEngine:
    """Main OCR Engine that handles different document types"""
    
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.extractors = {
            "voters_card": VotersCardExtractor(),
            "nin": NINExtractor(),
            "international_passport": PassportExtractor(),
            "drivers_license": DriversLicenseExtractor(),
        }
    
    def process_document(self, image_path: str) -> Dict[str, Any]:
        """
        Process document: classify type and extract relevant fields
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Could not read image file"}
            
            # Preprocess image for OCR
            processed = self.preprocess_image(image)
            
            # Extract text
            raw_text = self.extract_text(processed)
            
            # Log the extracted text for debugging
            logger.info(f"Extracted text: {raw_text[:200]}...")
            
            # Classify document type
            classification = self.classifier.classify(raw_text)
            logger.info(f"Document classified as: {classification}")
            
            # Extract fields based on document type
            fields = {}
            doc_type = classification["document_type"]
            
            if doc_type in self.extractors:
                extractor = self.extractors[doc_type]
                fields = extractor.extract(raw_text)
                logger.info(f"Extracted fields: {fields}")
            
            # Extract photo
            photo_path = self.extract_photo(image, doc_type)
            
            return {
                "document_type": doc_type,
                "classification_confidence": classification["confidence"],
                "country": classification["country"],
                "raw_text": raw_text,
                "fields": fields,
                "photo_path": photo_path,
                "photo_url": f"/photos/{os.path.basename(photo_path)}" if photo_path else None
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {"error": str(e)}
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        try:
            # Resize image to standard height
            height = 1000
            ratio = height / image.shape[0]
            width = int(image.shape[1] * ratio)
            image = cv2.resize(image, (width, height))
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while keeping edges sharp
            gray = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    def extract_text(self, image):
        """Extract text using Tesseract with multiple configurations"""
        try:
            # Try different PSM (Page Segmentation Mode) configurations
            configs = [
                '--psm 3',  # Fully automatic, default
                '--psm 4',  # Assume a single column of text
                '--psm 6',  # Assume a single uniform block of text
                '--psm 11',  # Sparse text
            ]
            
            best_text = ""
            max_length = 0
            
            for config in configs:
                text = pytesseract.image_to_string(image, config=config)
                if len(text) > max_length:
                    max_length = len(text)
                    best_text = text
            
            return best_text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_photo(self, image, doc_type):
        """Extract photo from document"""
        try:
            # Create directory for extracted photos
            photos_dir = "extracted_photos"
            os.makedirs(photos_dir, exist_ok=True)
            
            # Try face detection
            face_image = self.detect_face(image)
            
            if face_image is not None:
                # Save face
                unique_id = str(uuid.uuid4())
                photo_filename = f"face_{doc_type}_{unique_id}.jpg"
                photo_path = os.path.join(photos_dir, photo_filename)
                cv2.imwrite(photo_path, face_image)
                logger.info(f"Face extracted and saved to {photo_path}")
                return photo_path
            
            # If no face detected, save a resized version of the whole image
            unique_id = str(uuid.uuid4())
            photo_filename = f"full_{doc_type}_{unique_id}.jpg"
            photo_path = os.path.join(photos_dir, photo_filename)
            
            # Resize to a standard size
            resized = cv2.resize(image, (400, 400))
            cv2.imwrite(photo_path, resized)
            logger.info(f"Full image saved to {photo_path}")
            
            return photo_path
            
        except Exception as e:
            logger.error(f"Error extracting photo: {e}")
            return None
    
    def detect_face(self, image):
        """Detect face in image using Haar Cascade"""
        try:
            # Load the cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50)
            )
            
            if len(faces) > 0:
                # Get the largest face
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                x, y, w, h = largest_face
                
                # Add margin around the face (20%)
                margin = int(min(w, h) * 0.2)
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(image.shape[1] - x, w + 2 * margin)
                h = min(image.shape[0] - y, h + 2 * margin)
                
                # Extract face region
                face_image = image[y:y+h, x:x+w]
                return face_image
            
        except Exception as e:
            logger.error(f"Error detecting face: {e}")
        
        return None

# Create singleton instance
ocr_engine = OCRAnalyticsEngine()

def extract_text(image_path: str) -> Dict[str, Any]:
    """Main function to extract text from document"""
    return ocr_engine.process_document(image_path)



















# import cv2
# import pytesseract
# import numpy as np
# import os
# import re

# def extract_text(image_path):
#     # ----------------------------
#     # 1️⃣ Read image
#     # ----------------------------
#     image = cv2.imread(image_path)
#     if image is None:
#         raise ValueError("Image not found at path: " + image_path)

#     orig_image = image.copy()

#     # ----------------------------
#     # 2️⃣ Convert to grayscale
#     # ----------------------------
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     # ----------------------------
#     # 3️⃣ Edge detection & contour
#     # ----------------------------
#     edges = cv2.Canny(gray, 50, 150)
#     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # ----------------------------
#     # 4️⃣ Find largest rectangle → assume ID card
#     # ----------------------------
#     max_area = 0
#     best_cnt = None
#     for cnt in contours:
#         approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
#         if len(approx) == 4:
#             area = cv2.contourArea(cnt)
#             if area > max_area:
#                 max_area = area
#                 best_cnt = approx

#     if best_cnt is not None:
#         x, y, w, h = cv2.boundingRect(best_cnt)
#         cropped = image[y:y+h, x:x+w]
#     else:
#         cropped = image  # fallback: use full image

#     # ----------------------------
#     # 5️⃣ Preprocess cropped for OCR
#     # ----------------------------
#     gray_crop = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
#     gray_crop = cv2.equalizeHist(gray_crop)  
#     gray_crop = cv2.bilateralFilter(gray_crop, 9, 75, 75)
#     thresh = cv2.adaptiveThreshold(
#         gray_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY, 11, 2
#     )

#     # ----------------------------
#     # 6️⃣ Deskew the ID
#     # ----------------------------
#     coords = np.column_stack(np.where(thresh > 0))
#     angle = cv2.minAreaRect(coords)[-1]
#     if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle

#     (h, w) = thresh.shape[:2]
#     M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
#     thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


#     # 7️⃣ OCR extraction with ID-optimized config

#     # custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:/< '
#     # text = pytesseract.image_to_string(thresh, config=custom_config)

#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(thresh, config=custom_config)
#     # 8️ Face/photo extraction
  
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#     faces = face_cascade.detectMultiScale(gray_crop, scaleFactor=1.05, minNeighbors=4, minSize=(30,30))
#     photo_path = None
#     for (fx, fy, fw, fh) in faces:
#         photo = cropped[fy:fy+fh, fx:fx+fw]
#         os.makedirs("temp", exist_ok=True)
#         photo_path = "temp/photo.jpg"
#         cv2.imwrite(photo_path, photo)
#         break  # take the first detected face

#     # 9️ Structured field extraction
 
#     data = {}
#     text_clean = text.replace("\n", " ").replace("  ", " ")

#     # Full name (simplified regex)
#     name_match = re.search(r'([A-Z ]{2,})', text_clean)
#     if name_match:
#         data["full_name"] = name_match.group(1).title()

#     # Date of Birth
#     dob_match = re.search(r'(\d{2}/\d{2}/\d{4})', text_clean)
#     if dob_match:
#         data["date_of_birth"] = dob_match.group(1)

#     # Passport / ID numbers
#     passport_match = re.search(r'([A-Z]{2}\d{7,9})', text_clean)
#     if passport_match:
#         data["passport_no"] = passport_match.group(1)

#     # NIN (numbers only)
#     nin_match = re.search(r'(\d{11,})', text_clean.replace(" ", ""))
#     if nin_match:
#         data["nin"] = nin_match.group(1)

#     # ----------------------------
#     # 10️⃣ Return everything
#     # ----------------------------
#     return {
#         "raw_text": text.strip(),
#         "photo_path": photo_path,
#         "fields": data
#     }


# import cv2
# import pytesseract
# import numpy as np
# import os
# import re

# # =========================
# # 1️⃣ OCR + Photo Extraction
# # =========================
# def extract_text(image_path):
#     # Read image
#     image = cv2.imread(image_path)
#     if image is None:
#         raise ValueError(f"Image not found at path: {image_path}")

#     # Convert to grayscale & enhance
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
#     gray = cv2.bilateralFilter(gray, 9, 75, 75)

#     # Edge detection
#     edges = cv2.Canny(gray, 50, 150)

#     # Find contours
#     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # Detect largest rectangle → ID card
#     max_area = 0
#     best_cnt = None
#     for cnt in contours:
#         approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
#         if len(approx) == 4:
#             x, y, w, h = cv2.boundingRect(approx)
#             aspect_ratio = w / h
#             if 1.4 < aspect_ratio < 1.8:  # typical ID ratio
#                 area = cv2.contourArea(cnt)
#                 if area > max_area:
#                     max_area = area
#                     best_cnt = approx

#     # Crop ID card (or fallback)
#     if best_cnt is not None:
#         x, y, w, h = cv2.boundingRect(best_cnt)
#         cropped = image[y:y+h, x:x+w]
#     else:
#         cropped = image

#     # Preprocess cropped image for OCR
#     gray_crop = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
#     gray_crop = cv2.convertScaleAbs(gray_crop, alpha=1.5, beta=0)
#     gray_crop = cv2.bilateralFilter(gray_crop, 9, 75, 75)
#     thresh = cv2.adaptiveThreshold(
#         gray_crop, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY, 11, 2
#     )

#     # OCR
#     custom_config = r'--oem 3 --psm 6'
#     text = pytesseract.image_to_string(thresh, config=custom_config)
#     text = text.replace("\n\n", "\n").strip()

#     # Detect photo inside ID
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
#     faces = face_cascade.detectMultiScale(gray_crop, scaleFactor=1.1, minNeighbors=4)

#     photo_path = None
#     for (fx, fy, fw, fh) in faces:
#         photo = cropped[fy:fy+fh, fx:fx+fw]
#         os.makedirs("temp", exist_ok=True)
#         photo_path = "temp/photo.jpg"
#         cv2.imwrite(photo_path, photo)
#         break  # first detected face only

#     return {
#         "raw_text": text,
#         "photo_path": photo_path
#     }

# # =========================
# # 2️⃣ Extract key fields
# # =========================
# def extract_fields(text):
#     data = {}

#     # Name
#     name = re.search(r'NAME[: ]+(.*)', text, re.I)
#     if name:
#         data["full_name"] = name.group(1).strip()

#     # Date of Birth
#     dob = re.search(r'(\d{2}/\d{2}/\d{4})', text)
#     if dob:
#         data["date_of_birth"] = dob.group(1)

#     # Nigerian NIN (11 digits)
#     nin = re.search(r'\b\d{11}\b', text)
#     if nin:
#         data["nin"] = nin.group(0)

#     # Passport (e.g., A1234567)
#     passport = re.search(r'\b[A-Z]{1}\d{7}\b', text)
#     if passport:
#         data["passport_number"] = passport.group(0)

#     # Driver License (e.g., AB123456)
#     driver_license = re.search(r'\b[A-Z]{2}\d{6}\b', text)
#     if driver_license:
#         data["driver_license"] = driver_license.group(0)

#     return data

# # app/ocr/ocr_engine.py
# import cv2
# import pytesseract
# import re
# import os
# import uuid
# from typing import Dict, Any

# def extract_text(image_path: str) -> Dict[str, Any]:
#     """
#     Extract text and fields from ID document image
#     """
#     # Read image
#     image = cv2.imread(image_path)
#     if image is None:
#         return {"error": "Could not read image file"}
    
#     # Preprocess image
#     processed = preprocess_image(image)
    
#     # Extract text using OCR
#     raw_text = pytesseract.image_to_string(processed)
    
#     # Extract structured fields
#     fields = extract_fields(raw_text)
    
#     # Extract face/photo if needed
#     photo_path = extract_and_save_photo(image)
    
#     return {
#         "raw_text": raw_text,
#         "fields": fields,
#         "photo_path": photo_path
#     }

# def preprocess_image(image):
#     """Preprocess image for better OCR results"""
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     gray = cv2.bilateralFilter(gray, 9, 75, 75)
#     thresh = cv2.adaptiveThreshold(
#         gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY, 11, 2
#     )
#     return thresh

# def extract_fields(text):
#     """Extract structured fields from OCR text"""
#     data = {}
    
#     # Name extraction
#     name = re.search(r'NAME[: ]+(.*)', text, re.I)
#     if name:
#         data["full_name"] = name.group(1).strip()
    
#     # Date of birth extraction
#     dob = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', text)
#     if dob:
#         data["date_of_birth"] = dob.group(1)
    
#     # ID number extraction
#     id_num = re.search(r'ID[:\s]*(\d+)', text, re.I)
#     if id_num:
#         data["id_number"] = id_num.group(1)
    
#     return data

# def extract_and_save_photo(image):
#     """
#     Extract photo from ID document and save it
#     This is a placeholder - you'll need actual face detection logic
#     """
#     try:
#         # Create directory for extracted photos
#         photos_dir = "extracted_photos"
#         os.makedirs(photos_dir, exist_ok=True)
        
#         # For demonstration, let's assume we found a face region
#         # You would use face detection here (e.g., Haar Cascade, Deep Learning)
        
#         # Placeholder: Save the entire image as the "photo" for now
#         # In reality, you'd crop to the face region
#         unique_id = str(uuid.uuid4())
#         photo_filename = f"{unique_id}.jpg"
#         photo_path = os.path.join(photos_dir, photo_filename)
        
#         # For demo: save a resized version of the original image
#         # You should replace this with actual face detection
#         height, width = image.shape[:2]
        
#         # Assume the photo is in the top half for ID cards
#         # This is a naive approach - replace with actual detection
#         if height > width:  # Portrait orientation
#             photo_region = image[0:height//3, 0:width]
#         else:  # Landscape orientation
#             photo_region = image[0:height, 0:width//3]
        
#         cv2.imwrite(photo_path, photo_region)
        
#         return photo_path
#     except Exception as e:
#         print(f"Error extracting photo: {e}")
#         return None
# # =========================
# # 3️⃣ Combined extraction
# # =========================
# def extract_id_info(image_path):
#     result = extract_text(image_path)
#     fields = extract_fields(result["raw_text"])
#     result["fields"] = fields
#     return result

# Example usage:
# result = extract_id_info("samples/id_card.jpg")
# print(result)