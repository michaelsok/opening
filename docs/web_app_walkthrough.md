# Opening Analysis Web App Walkthrough

I have developed a modern, full-stack web application for the Chess Opening Analysis tool. It allows users to connect with Chess.com and upload their opening repertoire PGNs.

## Features

### Connect with Chess.com
- A premium, glassmorphism-inspired landing page.
- Direct integration with the Chess.com Player API to verify usernames and fetch profile data (Avatar, Location, Name).

### Repertoire Management
- An interactive dashboard for logged-in users.
- Drag-and-drop support for PGN file uploads.
- Real-time feedback and processing animations.
- Backend logic that automatically splits the repertoire into recognized opening categories (e.g., "Ruy Lopez").

## Technical Stack
- **Backend**: FastAPI (Python) for high-performance API handling.
- **Frontend**: Vanilla HTML5, CSS3 (with custom design system), and modern JS for a lightweight but premium experience.
- **Styling**: Modern typography (Inter), glassmorphism, and Lucide icons for a state-of-the-art aesthetic.

## Verification Results

### Success
Verified all endpoints using `curl`:
- **Auth**: Correctly fetches Chess.com profile data.
- **Upload**: Successfully processes PGN files and returns identified opening categories.

### How to Run
1. Start the server:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   python3 -m src.web.main
   ```
2. Navigate to `http://localhost:8000` in your browser.
