# ПЛАНИФИКАТОР-3000

Production-ready монорепозиторий для продукта **ПЛАНИФИКАТОР-3000**: Next.js frontend, FastAPI backend и общие пакеты для UI, типов и конфигураций.

## Стек

### Frontend

- Next.js 15 App Router
- React 19
- TypeScript в strict mode
- Tailwind CSS v4
- shadcn/ui-compatible конфигурация
- Framer Motion
- Lucide Icons

### Backend

- Python 3.12
- FastAPI
- Pydantic v2 и pydantic-settings
- uv package manager
- ruff
- mypy strict
- pytest

### Tooling

- Turborepo
- pnpm workspaces
- ESLint flat config
- Prettier + Tailwind plugin
- Husky
- lint-staged
- EditorConfig
- VSCode workspace settings
- Docker / Docker Compose
- GitHub Actions CI

## Структура

```text
planner3000/
├── apps/
│   ├── web/              # Next.js application
│   └── api/              # FastAPI application
├── packages/
│   ├── ui/               # Shared React UI primitives
│   ├── shared/           # Shared TypeScript contracts/constants
│   └── config/           # Shared TypeScript configuration
├── docs/                 # Architecture and project docs
├── .github/workflows/    # CI pipelines
├── docker-compose.yml
├── Makefile
├── package.json
├── pnpm-workspace.yaml
└── turbo.json
```

## Быстрый старт

### Требования

- Node.js 22+
- Corepack
- pnpm 9.15+
- Python 3.12
- uv
- Docker и Docker Compose для контейнерного запуска

### Установка

```bash
make install
```

Команда включает Corepack, устанавливает pnpm-зависимости и синхронизирует Python окружение через uv.

### Переменные окружения

Скопируйте примеры и настройте значения под окружение:

```bash
cp apps/web/.env.example apps/web/.env
cp apps/api/.env.example apps/api/.env
```

Frontend:

- `NEXT_PUBLIC_APP_URL` — публичный URL web-приложения.
- `NEXT_PUBLIC_API_URL` — публичный URL API.

Backend:

- `APP_NAME` — имя сервиса.
- `APP_ENV` — окружение (`local`, `staging`, `production`).
- `API_PREFIX` — префикс HTTP API.
- `CORS_ORIGINS` — разрешённые origins для браузерных клиентов.

## Разработка

Запустить весь monorepo dev loop:

```bash
make dev
```

Запустить только web:

```bash
make web-dev
```

Запустить только API:

```bash
make api-dev
```

По умолчанию:

- Web: <http://localhost:3000>
- API: <http://localhost:8000>
- OpenAPI: <http://localhost:8000/docs>
- Healthcheck: <http://localhost:8000/api/v1/health>

## Качество кода

```bash
make lint
make typecheck
make test
make format
```

Что проверяется:

- ESLint для TypeScript/React кода.
- Prettier для форматирования frontend/config/docs файлов.
- ruff для Python linting и formatting.
- mypy в strict mode для backend.
- pytest для backend тестов.
- TypeScript strict mode для web и packages.

## Git hooks

Husky запускает `lint-staged` перед коммитом. Для staged файлов автоматически выполняются:

- Prettier для JS/TS/JSON/Markdown/CSS/YAML.
- ESLint с `--fix` для JS/TS.
- ruff format/check для Python файлов backend.

## Docker

Собрать контейнеры:

```bash
make docker-build
```

Запустить stack:

```bash
make docker-up
```

Остановить stack:

```bash
make docker-down
```

Compose поднимает два сервиса:

- `web` — Next.js standalone runtime на порту `3000`.
- `api` — FastAPI runtime на порту `8000`.

## CI

GitHub Actions workflow `.github/workflows/ci.yml` запускает два независимых job:

1. `frontend` — install, format check, lint, typecheck, build.
2. `backend` — uv sync, ruff format check, ruff check, mypy, pytest.

## Пакеты

### `@planner3000/ui`

Переиспользуемые React-компоненты и CSS theme tokens. Компонент `Button` сделан в стиле shadcn/ui с `class-variance-authority`, `Radix Slot` и `tailwind-merge`.

### `@planner3000/shared`

Общие продуктовые контракты: `APP_NAME`, `PlanStatus`, `PlanSummary`.

### `@planner3000/config`

Единые TypeScript конфигурации:

- `@planner3000/config/typescript/base`
- `@planner3000/config/typescript/next`
- `@planner3000/config/typescript/react-library`

## Production notes

- Next.js настроен с `output: "standalone"` для production Docker image.
- FastAPI создаётся через `create_app()`, что упрощает тестирование и будущую настройку lifespan hooks.
- CORS конфигурируется через environment variables.
- Shared TypeScript packages имеют узкие exports и могут развиваться независимо.
- Все проверки представлены в Makefile и CI, чтобы локальная разработка совпадала с pipeline.
