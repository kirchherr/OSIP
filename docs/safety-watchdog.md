# Safety Watchdog

The safety watchdog turns OSIP safety contracts into deterministic safe-state
activation decisions. It does not control hardware directly.

Input:

- `profile.safety_case`: profile-level watchdog thresholds and default safe
  states.
- `adapter.heartbeat`: adapter liveness, TTL, status, and active safe state.
- `context.update`: current context timestamp for stale-context checks.
- Runtime flags such as bus disconnect, manual emergency stop, contract
  violation, or sensor dropout.

Output:

- `SafetyEvaluation.safe`: true when no safe-state trigger is active.
- `SafeStateActivation`: target, safe state, trigger, reason, optional age, and
  whether a hardware interlock is required.

The reference implementation is pure Python in
`packages/safety/omnisense_safety`. It uses deterministic timestamps and has no
broker, network, hardware, or wall-clock dependency.

Benchmarks can embed a `safety` section in scenario YAML. The benchmark runner
then evaluates the watchdog after replay and reports `safe_state_activations`
plus a `safety_watchdog` gate in JSON and Markdown output.

Example:

```python
from omnisense_safety import evaluate_safety_case

evaluation = evaluate_safety_case(
    safety_case,
    now=now,
    context=current_context,
    heartbeats=[robot_heartbeat],
)
```

Adapter responsibilities:

- load the relevant `profile.safety_case` before accepting action commands,
- map activations to adapter-specific bounded actions or hardware safety
  controllers,
- report heartbeat status frequently enough to satisfy the configured TTL,
- never treat this reference watchdog as a certified emergency-stop controller.
