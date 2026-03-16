import tempfile
import os
from fastapi import FastAPI, UploadFile, File, Form
from schemas import ThreatRequest, ThreatResponse
from detector import ThreatDetector

app = FastAPI(title="Kavach Cybersecurity API")
detector = ThreatDetector()

@app.get("/")
async def root():
    return {"message": "Welcome to Kavach AI Platform"}

@app.post("/detect", response_model=ThreatResponse)
async def detect_threat(request: ThreatRequest):
    result = detector.detect(request.content, request.content_type)
    return result

@app.post("/detect-file", response_model=ThreatResponse)
async def detect_file_threat(
    content_type: str = Form(...),
    file: UploadFile = File(...)
):
    # Read the file contents (or simulate reading for deepfake detection)
    try:
        file_bytes = await file.read()
        file_size = len(file_bytes)
    finally:
        await file.close()

    result = detector.detect_file(file.filename, file_size, content_type, file_bytes)
    return result
