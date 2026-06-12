from __future__ import annotations

from pathlib import Path

from omnisense_benchmarks import ScenarioBenchmarkRunner, render_markdown_report

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "scenarios"


async def test_benchmark_runner_passes_current_scenario_suite() -> None:
    result = await ScenarioBenchmarkRunner(SCENARIO_DIR).run_suite()

    assert result.passed
    assert result.summary.scenario_count == 5
    assert result.summary.passed_scenarios == 5
    assert result.summary.failed_scenarios == 0
    assert result.summary.false_positive_contexts == 0
    assert result.summary.false_negative_contexts == 0
    assert result.summary.false_positive_actions == 0
    assert result.summary.false_negative_actions == 0
    assert result.summary.context_latency.p95_ms == 250.0
    assert result.summary.action_proposal_latency.p95_ms == 250.0


async def test_benchmark_runner_handles_scenario_without_expected_contexts() -> None:
    result = await ScenarioBenchmarkRunner(SCENARIO_DIR).run_suite(
        ["normal_cooking_no_alarm.yaml"],
    )

    assert result.passed
    assert result.scenarios[0].detected_contexts == ()


async def test_benchmark_markdown_report_contains_scenario_table() -> None:
    result = await ScenarioBenchmarkRunner(SCENARIO_DIR).run_suite(
        ["fall_candidate.yaml"],
    )

    markdown = render_markdown_report(result)

    assert "# OSIP Benchmark Report" in markdown
    assert "fall_candidate" in markdown
    assert "action.room.speaker.ask_help_needed" in markdown
