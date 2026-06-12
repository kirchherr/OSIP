# Security Policy

## Supported Versions

OSIP is pre-1.0. Security fixes target the `main` branch until versioned
release branches exist.

## Reporting A Vulnerability

Please do not report vulnerabilities through a public issue first.

Use GitHub private vulnerability reporting if it is enabled for this repository.
If that is not available, contact the maintainers privately through the
repository owner before public disclosure.

Please include:

- affected component or package,
- reproduction steps,
- expected impact,
- whether real hardware, physical actuators, or external services are involved,
- any logs, traces, schemas, or scenario files needed to reproduce safely.

## Security Scope

Particularly sensitive areas include:

- OSIP schema validation,
- Gateway model registration and CapabilityGate behavior,
- Action Contracts, preconditions, cooldowns, safe states, and idempotency,
- simulator and adapter boundaries,
- future learning, model-promotion, and emergent-autonomy paths.

Do not test against real physical systems, robots, building equipment, or
third-party services without explicit authorization and a safe-state plan.
