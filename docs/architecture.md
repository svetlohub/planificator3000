# Architecture

ПЛАНИФИКАТОР-3000 построен как монорепозиторий с независимыми приложениями и общими пакетами.

## Boundaries

- `apps/web` — пользовательский интерфейс на Next.js App Router.
- `apps/api` — HTTP API на FastAPI и Pydantic v2.
- `packages/ui` — переиспользуемые React-компоненты в стиле shadcn/ui.
- `packages/shared` — общие TypeScript-типы и продуктовые константы.
- `packages/config` — централизованные конфиги TypeScript.

## Principles

1. Strict typing by default.
2. Package-level ownership and small public APIs.
3. CI parity with local `make` commands.
4. Docker images that can be built independently per app.
