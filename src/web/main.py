from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import logging
from .auth import verify_chess_user
from .repertoire import handle_repertoire_upload

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chess Opening Analysis API")

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse
import os

@app.get("/")
async def root():
    return FileResponse("src/web/static/index.html")

@app.post("/auth/verify")
async def verify_user(username: str = Form(...)):
    """
    Endpoint to verify a Chess.com username.
    """
    user_info = verify_chess_user(username)
    if not user_info:
        raise HTTPException(status_code=404, detail="Chess.com user not found")
    
    return {
        "status": "success",
        "username": username,
        "profile": user_info
    }

@app.post("/repertoire/upload")
async def upload_repertoire(
    username: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Endpoint to upload and split a repertoire PGN.
    """
    if not file.filename.endswith(".pgn"):
        raise HTTPException(status_code=400, detail="Only .pgn files are allowed")
    
    content = await file.read()
    result = handle_repertoire_upload(username, content, file.filename)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
