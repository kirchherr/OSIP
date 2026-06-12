FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONPATH="/workspace/packages/osip:/workspace/packages/bus:/workspace/packages/context_engine:/workspace/packages/profiles:/workspace/packages/decision_runtime:/workspace/packages/safety:/workspace/packages/benchmarks:/workspace/packages/simulators:/workspace/packages/gateway:/workspace/packages/sdk_python"

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        make \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --dev --no-install-project

COPY . .

CMD ["bash"]
