# Phase 1 verification

Verified locally on Windows on 7 September 2026.

| Check | Result |
|---|---|
| Next.js production compilation and TypeScript | Passed |
| PostgreSQL 18 live connection | Passed on isolated port 55432 |
| Initial Alembic upgrade and downgrade on a fresh disposable PostgreSQL database | Passed |
| Python backend suite | 13 passed |
| Playwright browser suite (Microsoft Edge) | 2 journeys passed |
| Agent-browser initial visual inspection | Landing, dashboard and analysis dialog checked; no recorded page errors |
| Desktop rendering | 1440px screenshot inspected |
| Mobile rendering | 390px; no horizontal overflow; drawer navigation passed |
| Dark mode | Toggle and persistence after reload passed |
| Keyboard command palette | Ctrl+K, search and navigation passed |
| Resume workflow | Register, upload DOCX, choose roles/preferences, reject/accept evidence, confirm, reload, download, logout, login passed |
| PDF | Text extraction fixture passed in backend suite |
| Multi-user isolation | Foreign resume download/fact mutation denied; account lists isolated |
| Invalid uploads | Malformed PDF/DOCX, unsupported extension, empty text and >5 MB rejected |
| Logout revocation | Reusing revoked cookie denied |

The backend suite reports two upstream deprecation warnings from Starlette's test-client compatibility layer. They do not fail the tests.

Screenshots: `dashboard-desktop.png`, `dashboard-mobile.png`, `onboarding-upload.png`, `onboarding-review.png`, `landing-desktop.png`.

Not verified: Docker-based startup, public deployment, live Gemini calls, a representative scanned-PDF OCR journey, email reset delivery, semantic matching, LangGraph execution, resume exports, application submission or third-party form automation.

The app is running on loopback only. The screenshots use fictional demo/test candidates. A production security audit, load testing and comprehensive assistive-technology testing remain outside this Phase 1 verification.
