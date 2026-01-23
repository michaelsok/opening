# Security Hardening Implementation Plan

Comprehensive security measures to protect the application from common web vulnerabilities.

## Proposed Changes

### Backend Security (FastAPI)

#### Rate Limiting
- Use `slowapi` to restrict `/auth/verify` (5/min) and `/repertoire/upload` (2/min) per IP to prevent brute force and DoS.

#### Security Headers
- Implement custom Middleware to set:
  - `Content-Security-Policy`: Restrict scripts and styles to trusted sources.
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: strict-origin-when-cross-origin`

#### Input Sanitization
- Validate usernames against Chess.com's allowed pattern.
- Sanitize filenames and use UUIDs or fixed paths to prevent path traversal.

#### File Upload Constraints
- Enforce a 2MB limit for PGN files.
- Verify file headers to ensure it's a valid PGN format.

### Frontend Security (Vanilla SPA)

#### XSS Prevention
- Refactor `innerHTML` usage in `app.js` to use `textContent` and `createElement` for user-generated content.

#### Content Security Policy
- Add a `<meta>` tag CSP for redundant protection.

## Verification Plan

### Manual Verification
- Use `curl` to verify response headers.
- Attempt to upload an oversized file and verify rejection.
- Rapidly click "Connect" to trigger rate limiting (429 Too Many Requests).
