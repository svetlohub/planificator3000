# Changelog

## 2026-06-10 — MVP Railway production demo

### Added

* Railway deployment for frontend and API.
* Public frontend domain.
* Public API domain.
* FastAPI health endpoint.
* FastAPI smoke endpoint.
* Russian production UI.
* Settings page.
* Google Sheets URL setting.
* Routine tasks setting.
* Google Sheets CSV import from selected tab.
* Task filtering for service rows.
* Task date parsing from column B.
* Weekly report panel.
* Weekly plan panel.
* Manual task addition to plan.
* Copy output button.
* Compact task counters.
* Russian favicon and brand mark.

### Fixed

* Railway web port mismatch: Next.js listens on 8080.
* API CORS parsing for Railway environment variables.
* API startup failure in production mode without Google credentials.
* TypeScript monorepo path configuration.
* Next.js lint errors around browser globals.
* European date display.
* Google Sheets multiline CSV parsing.
* Filtering of sheet section headers and link rows.

### Changed

* Main workflow changed from manual text input to Google Sheets-first.
* Manual text input removed from main screen.
* Settings moved to separate page.
* Google Sheets instructions moved to settings.
* Report and plan are rendered as task rows instead of raw text.

### Known issues

* Google Sheets API is not yet connected through backend.
* Automatic latest sheet tab detection is not implemented.
* Browser CSV loading requires the sheet to be public/viewable.
* Monthly statistics are still approximate.
  