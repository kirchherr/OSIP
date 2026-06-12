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
    assert result.summary.application_profiles == ("rooms",)
    assert result.summary.benchmark_gate_failures == 0
    assert result.summary.false_positive_contexts == 0
    assert result.summary.false_negative_contexts == 0
    assert result.summary.false_positive_actions == 0
    assert result.summary.false_negative_actions == 0
    assert result.summary.safe_state_activations == 0
    assert result.summary.context_latency.p95_ms == 250.0
    assert result.summary.action_proposal_latency.p95_ms == 250.0
    assert result.scenarios[0].application_profile_display_name == "Rooms"
    assert result.scenarios[0].application_profile_version == "0.1"
    assert all(gate.passed for scenario in result.scenarios for gate in scenario.gates)


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
    assert "Benchmark gate failures: 0" in markdown
    assert "| Scenario | Profile | Result | Gates |" in markdown
    assert "| Scenario | Profile | Result | Gates | Contexts | Actions | Safety |" in markdown
    assert "action.room.speaker.ask_help_needed" in markdown


async def test_benchmark_runner_fails_unknown_application_profile(tmp_path: Path) -> None:
    scenario_text = (SCENARIO_DIR / "fall_candidate.yaml").read_text(encoding="utf-8")
    scenario_path = tmp_path / "unknown_profile.yaml"
    scenario_path.write_text(
        scenario_text.replace("application_profile: rooms", "application_profile: unknown"),
        encoding="utf-8",
    )

    result = await ScenarioBenchmarkRunner(tmp_path).run_suite(["unknown_profile.yaml"])

    assert not result.passed
    assert result.summary.failed_scenarios == 1
    assert result.summary.benchmark_gate_failures >= 1
    assert result.scenarios[0].application_profile == "unknown"
    assert result.scenarios[0].application_profile_display_name is None
    assert result.scenarios[0].gates[0].name == "application_profile_registered"
    assert result.scenarios[0].gates[0].passed is False


async def test_benchmark_runner_evaluates_expected_safety_watchdog_activation(
    tmp_path: Path,
) -> None:
    scenario_text = (SCENARIO_DIR / "fall_candidate.yaml").read_text(encoding="utf-8")
    scenario_path = tmp_path / "fall_candidate_with_safety.yaml"
    scenario_path.write_text(
        scenario_text.replace(
            "percepts:\n",
            """safety:
  safety_case:
    schema_version: osip/0.1
    type: profile.safety_case
    safety_case_id: safety_rooms_benchmark
    profile_id: rooms
    heartbeat_timeout_ms: 50
    stale_context_ms: 120
    default_safe_states:
      - target: room.speaker
        safe_state: speaker.silent
        triggers:
          - heartbeat_timeout
        max_transition_ms: 20
        requires_hardware_interlock: false
  evaluate_at_ms: 230
  heartbeats:
    - at_ms: 0
      adapter_id: room_speaker_bridge
      profile_id: rooms
      status: alive
      ttl_ms: 50
  expect_safe: false
  expected_safe_states:
    - target: room.speaker
      safe_state: speaker.silent
      trigger: heartbeat_timeout
percepts:
""",
        ),
        encoding="utf-8",
    )

    result = await ScenarioBenchmarkRunner(tmp_path).run_suite(
        ["fall_candidate_with_safety.yaml"],
    )

    assert result.passed
    assert result.summary.safe_state_activations == 1
    scenario = result.scenarios[0]
    assert scenario.safety_observed_safe is False
    assert scenario.safe_state_activations == ("room.speaker->speaker.silent:heartbeat_timeout",)
    safety_gate = next(gate for gate in scenario.gates if gate.name == "safety_watchdog")
    assert safety_gate.passed
