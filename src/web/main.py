from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional
import logging
import os
import json
import threading
import queue
import asyncio
from datetime import datetime
from .auth import verify_chess_user
from .repertoire import handle_repertoire_upload
from .database import initialize_db, get_repertoires_by_user
from src.api.chesscom_api import get_games_from_chesscom
from src.visualization.chess_display import create_index_html
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Chess Opening Analysis API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    initialize_db()

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Mount reports directory to serve generated analysis
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

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
    # Updated CSP to allow scripts and styles from unpkg and fonts
    response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self'; script-src 'self' unpkg.com; style-src 'self' unpkg.com fonts.googleapis.com 'unsafe-inline'; font-src fonts.gstatic.com; img-src 'self' data: https://images.chesscomfiles.com https://www.chess.com https://www.chess.com/bundles/web/images/noavatar_l.84a92b24.gif;"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.get("/")
async def root():
    return FileResponse("src/web/static/index.html")

@app.post("/auth/verify")
@limiter.limit("10/minute")
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
    
    if isinstance(user_info, dict) and user_info.get("error") == "rate_limit":
        raise HTTPException(status_code=503, detail="Chess.com API is busy. Please try again later.")
    
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
    color: str = Form('white'),
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

    result = handle_repertoire_upload(username, content, file.filename, color=color)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail="Failed to process repertoire")
    
    return result

@app.post("/analysis/run")
@limiter.limit("2/minute")
async def run_analysis(
    request: Request,
    username: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    time_class: Optional[str] = Form(None),
    color: Optional[str] = Form(None)
):
    """
    Endpoint to fetch games from Chess.com and run divergence analysis with real-time streaming.
    Supports granular date ranges and time controls.
    """
    q = queue.Queue()
    
    def background_worker():
        try:
            # 1. Fetch user repertoires
            q.put({"type": "info", "message": "Loading repertoire..."})
            repertoires = get_repertoires_by_user(username)
            if not repertoires:
                q.put({"type": "error", "detail": "No repertoire found. Please upload one first."})
                return
            
            repertoire_pgns = [r['pgn_content'] for r in repertoires]
            
            # 2. Parse dates
            try:
                dt_start = datetime.strptime(start_date, "%Y-%m-%d")
                dt_end = datetime.strptime(end_date, "%Y-%m-%d")
                # Make end date inclusive (end of day)
                dt_end = dt_end.replace(hour=23, minute=59, second=59)
            except ValueError:
                q.put({"type": "error", "detail": "Invalid date format. Use YYYY-MM-DD."})
                return

            # 3. Fetch games with progress reporting
            def fetch_progress(current, total, message):
                q.put({"type": "info", "message": f"[{current}/{total}] {message}"})

            q.put({"type": "info", "message": f"Fetching games from {start_date} to {end_date}..."})
            from src.api.chesscom_api import get_user_games
            games_data = get_user_games(
                username, 
                start_date=dt_start, 
                end_date=dt_end, 
                time_class=time_class, 
                color=color,
                progress_callback=fetch_progress
            )
            
            if not games_data:
                q.put({"type": "empty", "message": f"No games found on Chess.com for {username} in the selected range."})
                return
            
            game_pgns = [g.get('pgn') for g in games_data if g.get('pgn')]
            if not game_pgns:
                q.put({"type": "empty", "message": "Found games but they don't contain PGN data."})
                return

            # 4. Run analysis with progress callback
            q.put({"type": "info", "message": f"Analyzing {len(game_pgns)} games..."})
            
            def analysis_progress(current, total, message=None):
                q.put({"type": "progress", "current": current, "total": total, "message": message})

            # Create a unique directory for this analysis session
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = REPORTS_DIR / f"{username.lower()}_{timestamp}"
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path = report_dir / "index.html"
            
            create_index_html(
                games=game_pgns,
                opening_repertoire=repertoire_pgns,
                target_username=username,
                output_file=str(report_path),
                open_in_browser=False,
                progress_callback=analysis_progress
            )
            
            q.put({
                "type": "success",
                "report_url": f"/reports/{report_dir.name}/index.html",
                "game_count": len(game_pgns)
            })
            
        except Exception as e:
            logger.error(f"Analysis failed for {username}: {e}", exc_info=True)
            q.put({"type": "error", "detail": str(e)})
        finally:
            q.put(None) # End signal

    threading.Thread(target=background_worker, daemon=True).start()

    async def event_stream():
        while True:
            try:
                item = await asyncio.to_thread(q.get, timeout=0.1)
                if item is None:
                    break
                yield json.dumps(item) + "\n"
            except queue.Empty:
                await asyncio.sleep(0.1)
                continue

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
