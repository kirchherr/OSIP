import importlib
import sys

REQUIRED_MODULES = [
    "aiomqtt",
    "cloudevents",
    "fastapi",
    "httpx",
    "jsonschema",
    "nats",
    "opentelemetry",
    "orjson",
    "omnisense_bus",
    "omnisense_context",
    "omnisense_decision",
    "omnisense_embedding",
    "omnisense_gateway",
    "omnisense_model_plugins",
    "omnisense_osip",
    "omnisense_profiles",
    "omnisense_safety",
    "omnisense_sdk",
    "omnisense_sim",
    "prometheus_client",
    "pydantic",
    "pytest",
    "yaml",
    "omnisense_benchmarks",
    "omnisense_adapters",
]


def main() -> int:
    print(f"python={sys.version.split()[0]}")
    missing: list[str] = []
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            missing.append(module)

    if missing:
        print("missing=" + ",".join(missing))
        return 1

    print("environment=ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
