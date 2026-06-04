SHELL := /usr/bin/env bash

.PHONY: install dev build lint format typecheck test api-dev web-dev docker-build docker-up docker-down

install:
	corepack enable
	pnpm install
	uv sync --project apps/api --all-extras --dev

dev:
	pnpm dev

build:
	pnpm build

lint:
	pnpm lint
	uv run --project apps/api ruff check .

format:
	pnpm format
	uv run --project apps/api ruff format .

typecheck:
	pnpm typecheck
	uv run --project apps/api mypy app

test:
	pnpm test
	uv run --project apps/api pytest

api-dev:
	uv run --project apps/api fastapi dev app/main.py

web-dev:
	pnpm --filter @planner3000/web dev

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down --remove-orphans
