# Codex Project Notes

## Status
- Initialized on 2026-03-22.
- This file is maintained after each completed task.

## Tech Stack
- Python 3 standard library
- GitHub REST API (public, unauthenticated)
- Static Web UI: HTML, CSS, JavaScript (no frontend framework)
- Fonts via Google Fonts:
  - Playfair Display (display/headlines)
  - Source Serif 4 (body copy)
  - JetBrains Mono (labels/metadata)

## Architecture
- `scripts/monitor.py`
  - Core data logic for fetching PRs, extracting `val_bpb`, suspect filtering, classification, and sorting.
  - Shared by CLI monitor and Web UI server.
- `scripts/webui.py`
  - Lightweight threaded HTTP server (`http.server`).
  - Serves static files from `/web`.
  - Railway-ready binding via environment variables:
    - `HOST` (default `0.0.0.0`)
    - `PORT` (default `8000`)
  - Provides JSON API endpoint:
    - `GET /api/leaderboard`
    - Query params: `mode`, `since`, `records_only`, `include_suspect`, `top`, `me`, `suspect_threshold`
  - Reuses logic from `monitor.py` to avoid duplicated business rules.
- `Procfile`
  - Declares Railway web process startup:
    - `web: python3 scripts/webui.py`
- `nixpacks.toml`
  - Explicit Railway/Nixpacks runtime and start configuration:
    - setup `python312`
    - start command `python3 scripts/webui.py`
- `runtime.txt`
  - Pins Python runtime family (`python-3.12`) for hosting compatibility.
- `web/index.html`
  - Semantic single-page app shell.
  - Hero, query controls, stats section, leaderboard table.
- `web/styles.css`
  - Minimalist Monochrome tokenized styling:
    - strict black/white palette
    - serif-first typography
    - zero border radius
    - simple section rules
    - responsive layout + focus-visible states
- `web/app.js`
  - Frontend behavior and rendering.
  - Calls `/api/leaderboard`, renders stats/table, applies user filter controls.

## Work Log
- 2026-03-22: Created codex.md scaffold per AGENTS.md instructions.
- 2026-03-22: Added Web UI backend at `scripts/webui.py` with `/api/leaderboard` endpoint.
- 2026-03-22: Built full frontend (`web/index.html`, `web/styles.css`, `web/app.js`) in Minimalist Monochrome style.
- 2026-03-22: Simplified frontend styling by removing non-essential decorative sections/effects for a cleaner UI.
- 2026-03-22: Updated `README.md` with Web UI usage.
- 2026-03-22: Verified via `py_compile` and live API smoke test against `http://127.0.0.1:8000/api/leaderboard`.
- 2026-03-22: Added Railway deployment support (`Procfile`, env-based host/port binding in `scripts/webui.py`, and README deployment steps).
- 2026-03-22: Verified server startup with Railway-style env vars (`PORT=9090`, `HOST=127.0.0.1`) and confirmed UI/API responses.
- 2026-03-22: Created and pushed a new GitHub repository `fbedev/parameter-golf-monitor-webui` and added it as git remote `new-origin`.
- 2026-03-22: Attempted Railway CLI deployment from this environment; blocked by non-interactive auth (`railway login` requires interactive session).
- 2026-03-22: Added explicit Railway deployment hardening (`nixpacks.toml`, `runtime.txt`) after a user-reported deploy failure.
