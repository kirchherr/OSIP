from __future__ import annotations

import json
from pathlib import Path

from omnisense_gateway import create_app


def main() -> int:
    output_path = Path("protocols/openapi/openapi.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(create_app().openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
