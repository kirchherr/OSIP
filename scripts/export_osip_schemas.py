"""Export OSIP v0.1 JSON Schemas into protocols/schemas."""

from __future__ import annotations

from pathlib import Path

from omnisense_osip.schema_export import export_json_schemas


def main() -> None:
    output_dir = Path("protocols/schemas")
    paths = export_json_schemas(output_dir)
    for path in paths:
        print(path.as_posix())


if __name__ == "__main__":
    main()
