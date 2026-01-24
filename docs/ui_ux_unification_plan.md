# UI/UX and Style Unification Plan

This plan addresses the requirements in `user_plan.md` to enhance the main application's usability and unify the visual design language across all generated reports.

## Proposed Changes

### Main Application (Main Page)
#### [MODIFY] [app.js](file:///home/msok/projects/opening/src/web/static/js/app.js)
- Update avatar rendering to use a default Chess icon if the profile picture is missing or blocked.
- Add a "Color Preference" toggle/selector for White vs Black repertoire uploads.

#### [MODIFY] [index.html](file:///home/msok/projects/opening/src/web/static/index.html)
- Add UI elements for selecting the repertoire color (White/Black).
- Ensure the "Add Another Repertoire" button in the success view is correctly bound and functional.

### Generated Reports (Unification)
#### [MODIFY] [Templates](file:///home/msok/projects/opening/src/visualization/templates/)
- Update `index.html`, `single_game.html`, and `multi_game.html` to use the same glassmorphism CSS system (background gradients, blurred cards, Inter font).
- Sync color palettes and iconography (Lucide).

### Backend
#### [MODIFY] [repertoire.py](file:///home/msok/projects/opening/src/web/repertoire.py)
- Update `handle_repertoire_upload` to accept a `color` parameter and store files in `uploads/<user>/<color>/`.

## Verification Plan
1. **Visual Test**: Connect with various users to see avatar/icon fallback.
2. **Flow Test**: Upload a "White" repertoire, then click "Add Another" and upload a "Black" repertoire.
3. **Consistency Test**: Generate a full report suite and check if the styling matches the landing page.
