# app/api/routes.py
from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
from typing import Optional
from app.ocr.ocr_engine import extract_text

router = APIRouter()

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf"]

@router.post("/extract-id")
async def extract_id(file: UploadFile, background_tasks: BackgroundTasks):
    """
    Extract information from any ID document
    Supports: Voter's Card, NIN, International Passport, Driver's License
    """
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed"
        )

    # Save uploaded file temporarily
    os.makedirs("temp", exist_ok=True)
    
    temp_filename = f"temp_{uuid.uuid4()}{ext}"
    temp_path = f"temp/{temp_filename}"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Process document
        result = extract_text(temp_path)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Prepare response
        response_data = {
            "success": True,
            "filename": file.filename,
            "document_type": result.get("document_type", "unknown"),
            "confidence": result.get("classification_confidence", 0),
            "country": result.get("country", "unknown"),
            "raw_text": result.get("raw_text", ""),
            "fields": result.get("fields", {}),
        }
        
        # Add photo info if available
        if result.get("photo_path"):
            photo_filename = os.path.basename(result["photo_path"])
            response_data["profile_photo"] = {
                "filename": photo_filename,
                "url": f"/photos/{photo_filename}",
                "path": result["photo_path"]
            }
        
        # Clean up temp file
        background_tasks.add_task(cleanup_file, temp_path)
        
        return response_data
        
    except Exception as e:
        cleanup_file(temp_path)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/photos/{photo_filename}")
async def get_photo(photo_filename: str):
    """Serve extracted photos"""
    photos_dir = "extracted_photos"
    photo_path = os.path.join(photos_dir, photo_filename)
    
    if not os.path.exists(photo_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return FileResponse(
        photo_path, 
        media_type="image/jpeg",
        filename=photo_filename
    )

@router.get("/document-types")
async def get_document_types():
    """Get list of supported document types"""
    return {
        "supported_documents": [
            {
                "type": "voters_card",
                "name": "Nigerian Voter's Card",
                "fields": ["vin", "full_name", "date_of_birth", "occupation", "address", "state", "lga", "ward", "polling_unit"]
            },
            {
                "type": "nin",
                "name": "National Identification Number (NIN)",
                "fields": ["nin", "full_name", "surname", "first_name", "middle_name", "date_of_birth", "gender", "address", "phone_number"]
            },
            {
                "type": "international_passport",
                "name": "International Passport",
                "fields": ["passport_number", "full_name", "surname", "first_name", "middle_name", "nationality", "date_of_birth", "place_of_birth", "issue_date", "expiry_date", "gender"]
            },
            {
                "type": "drivers_license",
                "name": "Driver's License",
                "fields": ["license_number", "full_name", "surname", "first_name", "middle_name", "date_of_birth", "issue_date", "expiry_date", "vehicle_categories", "blood_group", "address", "height"]
            }
        ]
    }

def cleanup_file(file_path: str):
    """Clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up {file_path}: {e}")


# from fastapi import APIRouter, UploadFile, HTTPException
# import shutil
# import os
# from app.ocr.ocr_engine import extract_text

# router = APIRouter()

# ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# @router.post("/extract-id")
# async def extract_id(file: UploadFile):
#     # 1️⃣ Check file extension
#     ext = os.path.splitext(file.filename)[1].lower()
#     if ext not in ALLOWED_EXTENSIONS:
#         raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG files are allowed")

#     # 2️⃣ Save uploaded file temporarily
#     os.makedirs("temp", exist_ok=True)
#     path = f"temp/{file.filename}"
#     with open(path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # 3️⃣ Call OCR engine
#     result = extract_text(path)

#     # 4️⃣ Return structured JSON
#     return {
#         "raw_text": result.get("raw_text"),
#         "fields": result.get("fields"),
#         "photo_path": result.get("photo_path")  # This is the saved face/photo path
#     }



