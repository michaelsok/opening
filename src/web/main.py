from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional
import logging
import os
from .auth import verify_chess_user
from .repertoire import handle_repertoire_upload

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Chess Opening Analysis API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Configure CORS - Restrict to specific origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict this for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Custom Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' unpkg.com; style-src 'self' fonts.googleapis.com 'unsafe-inline'; font-src fonts.gstatic.com; img-src 'self' data: https://images.chesscomfiles.com https://www.chess.com;"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.get("/")
async def root():
    return FileResponse("src/web/static/index.html")

@app.post("/auth/verify")
@limiter.limit("5/minute")
async def verify_user(request: Request, username: str = Form(...)):
    """
    Endpoint to verify a Chess.com username.
    """
    # Simple input validation
    if not username or len(username) > 40:
        raise HTTPException(status_code=400, detail="Invalid username format")
        
    user_info = verify_chess_user(username)
    if not user_info:
        raise HTTPException(status_code=404, detail="Chess.com user not found")
    
    return {
        "status": "success",
        "username": username,
        "profile": user_info
    }

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

@app.post("/repertoire/upload")
@limiter.limit("2/minute")
async def upload_repertoire(
    request: Request,
    username: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Endpoint to upload and split a repertoire PGN.
    """
    if not file.filename.endswith(".pgn"):
        raise HTTPException(status_code=400, detail="Only .pgn files are allowed")
    
    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 2MB)")
    
    content = await file.read()
    
    # Basic content check
    if b"[" not in content:
        raise HTTPException(status_code=400, detail="Invalid PGN format")

    result = handle_repertoire_upload(username, content, file.filename)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail="Failed to process repertoire")
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
