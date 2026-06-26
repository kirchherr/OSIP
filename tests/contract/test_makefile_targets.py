from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"


def test_makefile_exposes_benchmark_publication_targets() -> None:
    text = MAKEFILE.read_text(encoding="utf-8")

    assert "benchmark-publication:" in text
    assert "benchmark-publication-check:" in text
    assert "docker-benchmark-publication:" in text
    assert "docker-benchmark-publication-check:" in text


def test_makefile_benchmark_targets_write_manifest_and_run_gate() -> None:
    text = MAKEFILE.read_text(encoding="utf-8")

    assert "--manifest-output $(BENCHMARK_MANIFEST)" in text
    assert "--git-commit $(BENCHMARK_GIT_COMMIT)" in text
    assert "--project-version $(BENCHMARK_PROJECT_VERSION)" in text
    assert "scripts/check_benchmark_publication.py \\" in text
    assert "$(BENCHMARK_PUBLICATION_FLAGS)" in text
