DOCKER_COMPOSE ?= docker compose
SERVICE ?= dev
BENCHMARK_SCENARIO_DIR ?= scenarios
BENCHMARK_JSON ?= docs/results/latest.json
BENCHMARK_MD ?= docs/results/latest.md
BENCHMARK_MANIFEST ?= docs/results/latest.manifest.json
BENCHMARK_GIT_COMMIT ?= local
BENCHMARK_GIT_DIRTY_FLAG ?= --no-git-dirty
BENCHMARK_PROJECT_VERSION ?= 0.1.0
BENCHMARK_PUBLICATION_FLAGS ?=

.PHONY: docker-build docker-shell docker-run docker-test docker-lint docker-format docker-typecheck docker-env docker-benchmark docker-benchmark-publication-check docker-benchmark-publication nats-up nats-down test lint format typecheck env openapi asyncapi benchmark benchmark-publication-check benchmark-publication

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

docker-benchmark:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) uv run python scripts/run_benchmark.py \
		--scenario-dir $(BENCHMARK_SCENARIO_DIR) \
		--json-output $(BENCHMARK_JSON) \
		--markdown-output $(BENCHMARK_MD) \
		--manifest-output $(BENCHMARK_MANIFEST) \
		--git-commit $(BENCHMARK_GIT_COMMIT) \
		--project-version $(BENCHMARK_PROJECT_VERSION) \
		$(BENCHMARK_GIT_DIRTY_FLAG)

docker-benchmark-publication-check:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) uv run python scripts/check_benchmark_publication.py \
		$(BENCHMARK_MANIFEST) \
		$(BENCHMARK_PUBLICATION_FLAGS)

docker-benchmark-publication: docker-benchmark docker-benchmark-publication-check

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

openapi:
	uv run python scripts/export_openapi.py

asyncapi:
	uv run python scripts/export_asyncapi.py

benchmark:
	uv run python scripts/run_benchmark.py \
		--scenario-dir $(BENCHMARK_SCENARIO_DIR) \
		--json-output $(BENCHMARK_JSON) \
		--markdown-output $(BENCHMARK_MD) \
		--manifest-output $(BENCHMARK_MANIFEST) \
		--git-commit $(BENCHMARK_GIT_COMMIT) \
		--project-version $(BENCHMARK_PROJECT_VERSION) \
		$(BENCHMARK_GIT_DIRTY_FLAG)

benchmark-publication-check:
	uv run python scripts/check_benchmark_publication.py \
		$(BENCHMARK_MANIFEST) \
		$(BENCHMARK_PUBLICATION_FLAGS)

benchmark-publication: benchmark benchmark-publication-check
