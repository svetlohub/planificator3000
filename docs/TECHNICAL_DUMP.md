# PLANIFICATOR-3000 — Technical Dump

## Что это

PLANIFICATOR-3000 — MVP-сервис для недельного планирования команды.

Цель продукта: автоматически собирать задачи из Google Sheets, превращать их в отчёт за прошедшую неделю и план на текущую неделю.

Главный принцип:

> Не придумывай. Не угадывай. Не усложняй.

Система не заменяет менеджера. Она экономит время на рутине: сборе, фильтрации, форматировании и переносе задач.

---

## Текущий production workflow

1. Пользователь открывает нужную вкладку месяца в Google Sheets.
2. Копирует ссылку из адресной строки браузера, не Share link.
3. Вставляет ссылку в настройки PLANIFICATOR-3000.
4. На главном экране нажимает «Загрузить из Google Sheets».
5. Продукт читает:
   - столбец A — название задачи;
   - столбец B — дата создания задачи;
   - столбец C и ссылки игнорируются.
6. Продукт строит:
   - отчёт за неделю;
   - план на текущую неделю;
   - счётчики задач;
   - список задач для копирования.

---

## Google Sheets structure

Каждая таблица используется на одно полугодие.

Вкладки разбиты по месяцам:

- Январь
- Февраль
- Март
- Апрель
- Май
- Июнь

Текущий frontend читает выбранную вкладку по `gid` из URL.

Формула для дат:

```text
=IF(A3<>""; IF(B3<>""; B3; TODAY()); "")
````

Формула должна быть протянута вниз начиная с B3.

---

## Игнорируемые строки

Продукт автоматически игнорирует:

* Важные незапланированные проекты
* Текущие задачи месяца
* Задачи от СОСЕДНИХ отделов
* Название задачи
* Ссылка на задачу
* пустые строки
* ссылки
* служебные строки

---

## Frontend

Stack:

* Next.js 15
* React 19
* TypeScript
* Tailwind CSS
* Railway deployment
* Standalone Next.js Docker image

Main frontend files:

```text
apps/web/app/page.tsx
apps/web/app/settings/page.tsx
apps/web/app/layout.tsx
apps/web/public/favicon.svg
```

Current UX:

* Header with brand mark
* Settings icon
* Compact task counters
* Left panel: weekly report
* Right panel: next week plan
* Google Sheets load button
* Manual task addition to plan
* Copy output button
* Local browser storage for settings and routines

LocalStorage keys:

```text
planner3000:name
planner3000:sheetUrl
planner3000:routines
```

---

## Backend

Stack:

* FastAPI
* Python 3.12
* Pydantic v2
* uv
* Docker
* Railway

Current API state:

* Health endpoint works
* Smoke endpoint works
* Google Sheets backend API is not yet the main path
* Frontend currently loads public CSV directly from Google Sheets

Important endpoints:

```text
/api/health
/api/smoke
```

---

## Railway

Project architecture:

```text
Single Railway project
├── planner3000/web
└── api
```

Known domains:

```text
Frontend:
https://planner3000web-production.up.railway.app

API:
https://api-production-4656.up.railway.app
```

Important web setting:

```text
Public Networking Port: 8080
```

Important API setting:

```text
Public Networking Port: 8000
Healthcheck: /api/health
APP_ENV=local
API_PREFIX=/api
PORT=8000
```

---

## Architecture today

```text
Google Sheets public CSV
        ↓
Frontend CSV loader
        ↓
CSV parser
        ↓
Task filter
        ↓
Date range classifier
        ↓
Weekly report
        ↓
Weekly plan
        ↓
Copy/export
```

---

## Target architecture

```text
Google Sheets API
        ↓
FastAPI Sheets endpoint
        ↓
Task normalization layer
        ↓
Routine memory
        ↓
Planning engine
        ↓
Weekly report / plan
        ↓
Dashboard
```

---

## Main technical decisions

1. MVP uses Google Sheets as source of truth.
2. Frontend-first Google Sheets CSV loading was used for speed.
3. Backend API exists and is deployable.
4. Google Sheets API should move into FastAPI later.
5. AI should not run in frontend because API keys would leak.
6. AI module should be added through backend only.

---

## Current limitations

* Public Google Sheets CSV can only read selected `gid`.
* Frontend cannot reliably discover all sheet tabs.
* Latest tab auto-detection needs Google Sheets API.
* Current counters are approximate.
* Monthly / 2-month counters are currently derived from weekly count.
* No authenticated user model yet.
* No real database yet.
* Routine memory is browser-local only.
  