from __future__ import annotations

from pathlib import Path

from omnisense_bus.asyncapi_export import export_asyncapi


def main() -> int:
    output_path = Path("protocols/asyncapi/asyncapi.json")
    export_asyncapi(output_path)
    print(f"wrote={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
