# Web App Security Hardening Walkthrough

I have implemented multiple layers of security to protect the application from common web attacks and resource abuse.

## Security Measures Added

### Backend (FastAPI)
- **Rate Limiting**: Protected `/auth/verify` (5/min) and `/repertoire/upload` (2/min) using `slowapi` to prevent brute force and DoS.
- **Security Headers**: Added middleware to enforce strict browser policies:
  - `Content-Security-Policy`: Restricts scripts/styles to trusted sources.
  - `X-Frame-Options: DENY`: Prevents clickjacking.
  - `X-Content-Type-Options: nosniff`: Prevents MIME-type sniffing.
  - `Strict-Transport-Security`: Enforces HTTPS (HSTS).
- **Input Sanitization**:
  - Usernames are validated against alphanumeric patterns.
  - User-controlled filenames are discarded for fixed internal paths to prevent path traversal.
- **File Constraints**: Enforced a **2MB limit** on PGN uploads to prevent disk exhaustion.

### Frontend (Vanilla SPA)
- **XSS Prevention**: Refactored the entire UI logic to use `textContent` and `createElement` instead of `innerHTML`, ensuring user-provided data (like PGN content or names) cannot execute malicious scripts.
- **Redundant CSP**: Added a fallback `<meta http-equiv="Content-Security-Policy">` for older browsers.

## Verification Results

### Success
- **Rate Limit Test**: Confirmed that the server returns `429 Too Many Requests` after 5 authentication attempts.
- **Security Header Test**: Confirmed headers are present in all responses via `curl`.
- **Payload Size Test**: Confirmed the server returns `413 Payload Too Large` for files exceeding 2MB.
- **Security Injection**: Confirmed that dangerous usernames or filenames are safely handled without traversal or XSS.

## Changes Checklist
- [x] Backend: `slowapi` integration.
- [x] Backend: Custom security middleware.
- [x] Backend: Filename/Username regex sanitization.
- [x] Frontend: Refactored `app.js` (DOM methods).
- [x] Frontend: CSP meta tag in `index.html`.
