# Refactoring Frontend to PyHAT Stack (Python, HTMX, AlpineJS, Tailwind)

## Goal
Replace the current static HTML/Vanilla JS frontend with a PyHAT stack solution. This involves serving Jinja2 templates from FastAPI, using HTMX for dynamic content swapping (wizard steps), AlpineJS for interactivity (drag-and-drop, progress bar), and TailwindCSS for styling.

## User Review Required
> [!IMPORTANT]
> This refactor will replace `src/web/static/index.html` and `src/web/static/js/app.js`. The functionality will be preserved but the implementation will be fundamentally different.
> I will use CDN links for Tailwind, HTMX, and AlpineJS to match the "install what is needed" instruction without complex node/npm build steps.

## Proposed Changes

### 1. Template Structure
Create a `src/web/templates` directory with:
- `base.html`: Main layout including Tailwind, HTMX, AlpineJS CDNs.
- `index.html`: The main container.
- `partials/connect.html`: The login form (Step 1).
- `partials/dashboard.html`: The upload/dashboard (Step 2).
- `partials/success.html`: The analysis options (Step 3).

### 2. Backend (FastAPI) Updates
Modify `src/web/main.py`:
- Initialize `Jinja2Templates`.
- Update endpoints (`/auth/verify`, `/repertoire/upload`) to return `HTMLResponse` (rendered partials) for HTMX requests instead of JSON.
- Maintain JSON/Stream support where necessary (e.g., analysis stream), or adapt to HTMX patterns.

### 3. Frontend Logic
- **HTMX**: Handle form submissions and transitions between wizard steps.
- **AlpineJS**:
  - Handle Drag & Drop state (`x-on:dragover`, etc.).
  - Handle the Analysis Stream: Use `x-data` to Poll or consume the NDJSON stream for the progress bar, as this is complex state management best suited for Alpine.
- **Tailwind**: Re-implement `styles.css` using utility classes.

### 4. File Changes

#### [MODIFY] [main.py](file:///home/msok/projects/opening/src/web/main.py)
- Import `Jinja2Templates`.
- Mount logic for templates.
- Update `/` to render `index.html`.
- Update `/auth/verify` to return `partials/dashboard.html` on success.
- Update `/repertoire/upload` to return `partials/success.html` on success.

#### [NEW] [base.html](file:///home/msok/projects/opening/src/web/templates/base.html)
#### [NEW] [index.html](file:///home/msok/projects/opening/src/web/templates/index.html)
#### [NEW] [connect.html](file:///home/msok/projects/opening/src/web/templates/partials/connect.html)
#### [NEW] [dashboard.html](file:///home/msok/projects/opening/src/web/templates/partials/dashboard.html)
#### [NEW] [success.html](file:///home/msok/projects/opening/src/web/templates/partials/success.html)

#### [DELETE] [index.html](file:///home/msok/projects/opening/src/web/static/index.html)
#### [DELETE] [app.js](file:///home/msok/projects/opening/src/web/static/js/app.js)
#### [DELETE] [styles.css](file:///home/msok/projects/opening/src/web/static/css/styles.css)

## Verification Plan

### Manual Verification
1.  **Start Server**: `uvicorn src.web.main:app --reload`
2.  **Steps**:
    -   Load `http://localhost:8000`. Check styling (Tailwind).
    -   **Step 1**: Enter "magnuscarlsen". Click Connect. Verify partial swap to Dashboard.
    -   **Step 2**: Drag & drop a PGN. Verify partial swap to Success/Options.
    -   **Step 3**: Click "Run Analysis". Verify progress bar updates (AlpineJS).
    -   **Step 4**: Verify "View Report" button appears and works.

### Automated Tests
-   Verify existing tests pass: `pytest tests/`
-   Create `tests/web/test_routes.py` to verify endpoints return HTML when requested.
