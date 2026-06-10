# Backlog

## P0 — Production-critical

* Move Google Sheets loading from frontend CSV to FastAPI backend.
* Add Google Sheets API integration with service account.
* Auto-detect latest month tab.
* Read all tabs metadata from Google Sheets API.
* Store selected spreadsheet and tab configuration per user.
* Make report and plan generation deterministic on backend.
* Add real error states for Google Sheets access failures.

## P1 — Planning logic

* Separate report tasks and planned tasks by task date.
* Add support for completed / planned / backlog statuses.
* Add employee-level grouping.
* Add routine task matrix.
* Add manual marking: routine / project / one-off.
* Add carry-over logic for unfinished tasks.
* Add weekly memory for last 4–6 weeks.
* Add true monthly and 2-month counters from history.

## P2 — AI module

* Add backend AI provider abstraction.
* Support Google AI Studio free tier.
* Support Groq free tier.
* Add task normalization assistant.
* Add safe mode: AI cannot invent tasks.
* Add explanation of planning decisions.
* Add ambiguity detection.

## P3 — UX

* Add tab selector in settings.
* Add loading skeletons.
* Add import success details.
* Add export to CSV.
* Add export back to Google Sheets.
* Add editable task rows.
* Add delete task from plan.
* Add drag-and-drop between report and plan.
* Improve favicon and brand typography.

## P4 — Infrastructure

* Add production environment variables documentation.
* Add Railway deploy checklist.
* Add smoke test script.
* Add backend logging.
* Add Sentry or equivalent error reporting.
* Add CI build validation for web and API.
  