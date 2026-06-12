"""Benchmark report rendering."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from omnisense_benchmarks.runner import SuiteBenchmarkResult


def write_reports(
    result: SuiteBenchmarkResult,
    *,
    json_path: Path,
    markdown_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(result.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown_report(result), encoding="utf-8")


def render_markdown_report(result: SuiteBenchmarkResult) -> str:
    summary = result.summary
    lines = [
        "# OSIP Benchmark Report",
        "",
        f"Overall: {'PASS' if result.passed else 'FAIL'}",
        "",
        "## Summary",
        "",
        f"- Scenarios: {summary.scenario_count}",
        f"- Passed: {summary.passed_scenarios}",
        f"- Failed: {summary.failed_scenarios}",
        f"- Context latency p50/p95/p99: {_format_percentiles(summary.context_latency.as_dict())}",
        (
            "- Action proposal latency p50/p95/p99: "
            f"{_format_percentiles(summary.action_proposal_latency.as_dict())}"
        ),
        f"- False-positive contexts: {summary.false_positive_contexts}",
        f"- False-negative contexts: {summary.false_negative_contexts}",
        f"- False-positive actions: {summary.false_positive_actions}",
        f"- False-negative actions: {summary.false_negative_actions}",
        f"- Action contract blocks: {summary.action_contract_blocks}",
        "",
        "## Scenarios",
        "",
        "| Scenario | Result | Contexts | Actions | Context Latency | Action Latency |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for scenario in result.scenarios:
        context_latency = _format_budget(
            scenario.first_context_latency_ms,
            scenario.context_latency_budget_ms,
        )
        action_latency = _format_budget(
            scenario.first_action_proposal_latency_ms,
            scenario.action_latency_budget_ms,
        )
        lines.append(
            "| "
            f"{scenario.scenario_id} | "
            f"{'PASS' if scenario.passed else 'FAIL'} | "
            f"{_format_expected_actual(scenario.expected_contexts, scenario.detected_contexts)} | "
            f"{_format_expected_actual(scenario.expected_actions, scenario.proposed_actions)} | "
            f"{context_latency} | "
            f"{action_latency} |"
        )
    lines.append("")
    return "\n".join(lines)


def _format_percentiles(values: Mapping[str, object]) -> str:
    if values["count"] == 0:
        return "n/a"
    return f"{values['p50_ms']}/{values['p95_ms']}/{values['p99_ms']} ms"


def _format_expected_actual(expected: tuple[str, ...], actual: tuple[str, ...]) -> str:
    expected_text = ", ".join(expected) if expected else "none"
    actual_text = ", ".join(actual) if actual else "none"
    return f"expected: {expected_text}<br>actual: {actual_text}"


def _format_budget(observed: int | None, budget: int | None) -> str:
    observed_text = "n/a" if observed is None else f"{observed} ms"
    if budget is None:
        return observed_text
    return f"{observed_text} / budget {budget} ms"
