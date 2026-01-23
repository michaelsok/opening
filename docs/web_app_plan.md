# Opening Analysis Web App

Create an interactive web application for Chess.com authentication and repertoire management.

## User Review Required

> [!IMPORTANT]
> Chess.com does not provide a public OAuth2 system for 3rd party apps. Authentication will be implemented as a "Connect by Username" flow, where we verify the username's existence and fetch profile data to establish a session.

## Proposed Changes

### Backend (FastAPI)
Initialize a backend server to handle logic and file processing.

#### [NEW] [main.py](file:///home/msok/projects/opening/src/web/main.py)
- Entry point for the FastAPI server.
- Endpoints for authentication and file upload.

#### [NEW] [auth.py](file:///home/msok/projects/opening/src/web/auth.py)
- Logic to verify Chess.com usernames.

#### [NEW] [repertoire.py](file:///home/msok/projects/opening/src/web/repertoire.py)
- Logic to handle PGN uploads and integrate with existing `repertoire_manager.py`.

### Frontend (Vite)
Create a modern, premium frontend in a new `frontend/` directory.

#### [NEW] [Login Page](file:///home/msok/projects/opening/frontend/src/pages/Login.html)
- High-end visual design with glassmorphism.
- Integration with Chess.com verify API.

#### [NEW] [Dashboard](file:///home/msok/projects/opening/frontend/src/pages/Dashboard.html)
- User profile display.
- Drag-and-drop repertoire upload.
- Success/failure animations.

## Verification Plan

### Automated Tests
- Pytest for backend endpoints (mocking Chess.com API).

### Manual Verification
- Run `npm run dev` and `uvicorn main:app`.
- Test the full flow: Login -> Upload -> Success.
