# Decision Runtime v0.1

The Decision Runtime turns fused `ContextUpdate` messages into bounded
`ActionProposal` messages. It is deterministic, contract-driven, and
simulation-first. The default Application Profile is `rooms`, but profile
policies and default Action Contract bundles are selected through a registry
instead of being hard-wired into the runtime.

## Scope

- `ActionContractRegistry`: stores and matches registered Action Contracts.
- `DecisionPolicy`: profile-facing interface for matching context events,
  assigning priority, confirmation requirements, and proposal reasons.
- `DecisionProfileRegistry`: maps application profile ids to a decision policy
  plus the profile's default Action Contracts.
- `PreconditionsEvaluator`: evaluates a small non-executable precondition
  language such as `hvac.available == true` or `room.co2_ppm < 1200`.
- `CooldownTracker`: prevents repeated proposals for the same action inside the
  contract cooldown window.
- `RoomsDecisionPolicy`: maps rooms-profile context events to default contracts,
  provided by `omnisense_profiles.rooms.decision`.
- `DecisionRuntime`: publishes `ActionProposal` messages to
  `omnisense.actions.proposals`.
- `ActionCommandExecutorStub`: builds and publishes `ActionCommand` messages
  without real side effects.

## Profile Registry

`DecisionRuntime(bus)` keeps `rooms` as the MVP default. A new profile attaches
by registering a `DecisionProfile` that contains a `DecisionPolicy` and its
default Action Contracts.

```python
profile = DecisionProfile(
    profile_id="xxx",
    policy=XxxDecisionPolicy(),
    contracts=tuple(default_xxx_contracts()),
)
runtime = DecisionRuntime(
    bus,
    application_profile="xxx",
    profile_registry=DecisionProfileRegistry([profile]),
)
```

Unknown profiles fail closed with `UnknownDecisionProfileError`.

## Default Rooms Contracts

- `action.notify.local` for `context.possible_burning_food`
- `action.hvac.ventilation_boost` for `context.possible_burning_food` and
  `context.high_occupancy_stale_air`
- `action.room.speaker.ask_help_needed` for `context.possible_fall`

The runtime only proposes an action when:

1. A context event matches a registered contract.
2. Event confidence is at least `contract.min_confidence`.
3. All contract preconditions are satisfied by runtime facts.
4. The action is outside its cooldown window.

## Safety Boundary

No proposal is emitted without an Action Contract. The command stub only
materializes an OSIP `ActionCommand`; it does not call hardware, cloud APIs, or
vendor SDKs.

Real execution belongs in later adapters, and those adapters must keep the same
Action Contract bounds, idempotency, rollback, and safe-state rules.

## Validation

Run:

```bash
docker compose run --rm dev uv run pytest tests/unit/test_decision_runtime.py tests/integration/test_decision_runtime_flow.py
```

Full checks:

```bash
docker compose run --rm dev make test
docker compose run --rm dev make lint
docker compose run --rm dev make typecheck
```
