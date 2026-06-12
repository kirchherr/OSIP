from __future__ import annotations

import importlib
import sys


def test_python_runtime_is_supported() -> None:
    assert sys.version_info >= (3, 12)


def test_foundation_dependencies_are_importable() -> None:
    modules = [
        "aiomqtt",
        "cloudevents",
        "fastapi",
        "jsonschema",
        "nats",
        "opentelemetry",
        "orjson",
        "prometheus_client",
        "pydantic",
        "yaml",
    ]

    for module in modules:
        importlib.import_module(module)
