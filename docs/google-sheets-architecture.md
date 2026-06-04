# Google Sheets Integration Architecture

The Google Sheets integration layer is infrastructure only. It provides typed access to spreadsheet rows and deterministic mapping into domain contracts. It does **not** plan work, allocate capacity, normalize fuzzy inputs, generate reports, call LLMs, or contain product policy.

## Data Flow

```text
Google Sheets
  -> GoogleSheetsClient
  -> SheetsRepository
  -> Raw DTO rows
  -> SheetsMapper
  -> Domain Models
```

1. `GoogleSheetsClient` authenticates with Google and performs low-level worksheet operations.
2. `SheetsRepository` reads configured worksheets and validates each row as a DTO.
3. DTO models represent raw sheet contracts and are independent from the domain layer.
4. `SheetsMapper` converts DTOs into domain models with exact, deterministic rules.
5. Future application services can decide how to use domain models, but that logic is outside this connector.

## Settings

The connector uses the existing application settings layer. The following environment variables configure access and worksheet names:

- `GOOGLE_SHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_WORKSHEET_COMPLETED_TASKS`
- `GOOGLE_WORKSHEET_MONTHLY_PLAN`
- `GOOGLE_WORKSHEET_RECURRING_TASKS`
- `GOOGLE_WORKSHEET_TEAM_ROSTER`
- `GOOGLE_WORKSHEET_CONFIG`

`GOOGLE_SERVICE_ACCOUNT_JSON` is expected to contain the service-account JSON payload as a string. It should be provided by a secret manager in production.

## DTO Layer

DTOs live in `app/connectors/sheets/schemas.py`:

- `CompletedTaskRow`
- `MonthlyPlanRow`
- `RecurringTaskRow`
- `TeamRosterRow`
- `ConfigRow`

DTOs model spreadsheet rows and column names. They intentionally do not import or reference domain models. This keeps the spreadsheet contract isolated from business concepts and allows sheet validation to evolve independently.

## Client Layer

`GoogleSheetsClient` wraps `gspread` and `google-auth` and exposes a minimal operational API:

- `get_worksheet()`
- `read_records()`
- `write_records()`
- `clear_worksheet()`
- `health_check()`

The client is responsible for authentication, worksheet access, basic reads/writes, clearing worksheets, and future health endpoint support.

## Repository Layer

`SheetsRepository` uses `GoogleSheetsClient` plus configured worksheet names to load typed DTOs:

- `load_completed_tasks()`
- `load_monthly_plan()`
- `load_recurring_tasks()`
- `load_team_roster()`
- `load_config()`

The repository returns DTOs, not domain models. This is deliberate: repositories represent persistence/integration boundaries, while mapping into domain objects is a separate translation concern.

## Mapper Layer

`SheetsMapper` converts DTOs into domain models. The mapper is deterministic:

- no LLM calls;
- no fuzzy matching;
- no AI inference;
- no hidden planner policy;
- no allocation or reporting logic.

Examples:

- `CompletedTaskRow` maps to `Task` with `source=completed` and `status=done`.
- `MonthlyPlanRow` maps status by exact enum value only.
- `RecurringTaskRow` maps to `Task` with `source=recurring` and `status=pending`.
- `TeamRosterRow` maps comma-separated skills into `TeamMember.skills`.

## Why the Connector Does Not Know About Planner

The connector is an infrastructure boundary. Its job is to fetch and write spreadsheet data safely. Planner behavior is a higher-level application/domain concern and will depend on policies such as ordering, capacity strategy, carry-over handling, and conflict resolution.

Keeping planner logic out of this layer prevents hidden coupling between a Google Sheets schema and future planning algorithms.

## Why Repository Does Not Return Domain Models Directly

Returning domain models directly from the repository would merge two responsibilities:

1. reading external data from Google Sheets;
2. translating external data into domain contracts.

Separating them gives us clearer tests, better error handling, and easier replacement of Google Sheets with another source in the future. It also allows validation failures to identify whether the issue is sheet shape, DTO validation, or domain mapping.

## Error Handling

Connector errors are represented by explicit exceptions:

- `SheetsError` — base connector error;
- `WorksheetNotFoundError` — configured worksheet is missing;
- `SheetAccessError` — authentication, spreadsheet access, API, or write failures;
- `InvalidSheetDataError` — DTO validation or deterministic mapping failure.

## Production Readiness

`health_check()` is implemented on both client and repository to support a future API endpoint. The method verifies that the configured spreadsheet can be opened without performing planner, allocator, or reporter work.
