# main.py
from fastapi import FastAPI
from app.api.routes import router  # Correct import path
import os

# Create temp directory if it doesn't exist
os.makedirs("temp", exist_ok=True)

app = FastAPI(title="ID Document OCR API")

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "ID Document OCR API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



# from fastapi import FastAPI, UploadFile, File
# from app.ocr.ocr_engine import extract_text

# app = FastAPI()

# @app.post("/extract-id")
# async def extract_id(file: UploadFile = File(...)):
#     file_path = f"temp/{file.filename}"
#     with open(file_path, "wb") as f:
#         f.write(await file.read())
#     result = extract_text(file_path)
#     return result



# # main.py
# from fastapi import FastAPI
# from app.api.routes import router  # Make sure this import is correct

# app = FastAPI()

# # Include your API router
# app.include_router(router)