# Refactoring Frontend to PyHAT Stack (Walkthrough)

I have successfully refactored the frontend to use the PyHAT stack (Python, HTMX, AlpineJS, Tailwind). The application now serves Jinja2 templates instead of static HTML files, and uses HTMX for dynamic interactions.

## Key Changes

### 1. Template Structure (`src/web/templates/`)
-   **`base.html`**: Master layout with Tailwind, HTMX, and AlpineJS CDNs.
-   **`index.html`**: Entry point extending `base.html`.
-   **`partials/connect.html`**: Step 1 (Username input).
-   **`partials/dashboard.html`**: Step 2 (Upload area).
-   **`partials/success.html`**: Step 3 (Analysis controls).

### 2. Backend (`src/web/main.py`)
-   Initialized `Jinja2Templates`.
-   Updated main routes (`/`, `/auth/verify`, `/repertoire/upload`) to return `HTMLResponse` containing rendered templates.
-   Preserved JSON/Streaming logic for the analysis event stream (consumed by AlpineJS).

### 3. Frontend Logic
-   **HTMX**: Used for form submissions (`hx-post`, `hx-target`) to swapwizard steps without full page reloads.
-   **AlpineJS**: Used for:
    -   Drag-and-drop state on the dashboard.
    -   Handling the analysis progress bar (consuming the NDJSON stream).
    -   Date filter initialization.
-   **Tailwind**: Used for all styling (Glassmorphism, responsive layout).

## Verification Results

### Automated Tests (`tests/web/test_routes_html.py`)
-   **`test_root_returns_html`**: PASSED (Returns main page)
-   **`test_verify_user_returns_html_dashboard`**: PASSED (Returns dashboard partial)
-   **`test_upload_repertoire_returns_html_success`**: PASSED (Returns success partial)

### Manual Verification
-   Verified root endpoint returns 200 OK and HTML content via `curl`.
-   Verified `Content-Security-Policy` headers allow necessary CDNs.

## How to Run
```bash
export PYTHONPATH=$PYTHONPATH:.
python src/web/main.py
```
Open [http://localhost:8000](http://localhost:8000) to check the result.
