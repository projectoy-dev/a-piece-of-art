# 공통 명령어 — `make help` 로 목록 확인
SERVER := cd server &&

.PHONY: help setup db-up db-down dev migrate migration db-schema test lint format

help: ## 명령어 목록
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: ## server 의존성 설치 + .env 파일 생성
	$(SERVER) uv sync
	@test -f server/.env || cp server/.env.example server/.env
	@test -f .env || cp .env.example .env

db-up: ## 로컬 PostgreSQL 실행
	docker compose up -d db

db-down: ## 로컬 컨테이너 중지
	docker compose down

dev: ## server 개발 서버 실행 (http://localhost:8000)
	$(SERVER) uv run fastapi dev app/main.py

migrate: ## DB 마이그레이션 적용
	$(SERVER) uv run alembic upgrade head

migration: ## 마이그레이션 생성 — make migration m="create posts"
	$(SERVER) uv run alembic revision --autogenerate -m "$(m)"

db-schema: ## DB 스키마 문서 생성 (server/docs/db-schema.md)
	$(SERVER) uv run python -m app.utils.schema_doc

test: ## 테스트
	$(SERVER) uv run pytest

lint: ## 린트 · 포맷 검사
	$(SERVER) uv run ruff check . && uv run ruff format --check .

format: ## 자동 수정 · 포맷
	$(SERVER) uv run ruff check --fix . && uv run ruff format .
