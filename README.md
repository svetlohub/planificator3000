# PLANIFICATOR-3000

**PLANIFICATOR-3000** — production-ready MVP для недельного планирования и контроля загрузки команды.

Система использует Google Sheets как source of truth, FastAPI как backend и Next.js dashboard как GUI для руководителя.

## MVP scope

- Weekly dashboard
- Team workload
- Capacity visibility
- Backlog visibility
- Google Sheets integration
- Railway deployment
- Docker production images
- Health endpoint: `/api/health`
- Smoke endpoint: `/api/smoke`

## Stack

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS v4
- FastAPI
- Python 3.12
- Docker
- Railway
- Google Sheets

## Railway deployment

Цель: один Railway project, два сервиса:

- `api`
- `web`

### API service

Dockerfile:

```text
apps/api/Dockerfile
