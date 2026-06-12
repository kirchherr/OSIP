DOCKER_COMPOSE ?= docker compose
SERVICE ?= dev

.PHONY: docker-build docker-shell docker-run docker-test docker-lint docker-format docker-typecheck docker-env nats-up nats-down test lint format typecheck env

docker-build:
	$(DOCKER_COMPOSE) build dev

docker-shell:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) bash

docker-run:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) $(CMD)

docker-test:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) uv run pytest

docker-lint:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) uv run ruff check .

docker-format:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) uv run ruff format .

docker-typecheck:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) uv run mypy

docker-env:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) uv run python scripts/dev_env_check.py

nats-up:
	$(DOCKER_COMPOSE) --profile broker up -d nats

nats-down:
	$(DOCKER_COMPOSE) --profile broker down

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy

env:
	uv run python scripts/dev_env_check.py
