# Model Plug-ins

Model plug-ins are the boundary between OSIP and specialized perception models.
The first implementation is declarative. It registers what a model may publish;
it does not execute plug-in code.

## Manifest

`ModelPluginManifest` describes one model plug-in:

- `schema_version`: `model_plugin/0.1`,
- `plugin_id`: stable id; in v0.1 it must match `capability.model_id`,
- `display_name` and `version`,
- `capability`: the OSIP `ModelCapabilityDescriptor`,
- `runtime`: `simulation_stub`, `python_callable`, `external_process`, or
  `http_endpoint`,
- `entrypoint`: required for live runtimes, not required for simulation stubs,
- `application_profiles`: optional profile allow-list such as `rooms` or
  `physical-ai`,
- `requires_hardware` and `sandbox_required`,
- optional license, source URI, tags, and metadata.

The manifest is intentionally not a loader. Runtimes that import Python,
start subprocesses, call HTTP endpoints, or access hardware must be implemented
as later adapters around the same manifest contract.

## Registry

`ModelPluginRegistry` stores manifests in memory and exposes:

- `register(manifest)`,
- `get(plugin_id)`,
- `manifests(profile_id=...)`,
- `capabilities(profile_id=...)`,
- registration metadata with `registered_at` and `status`.

The registry rejects manifests where:

- `plugin_id` differs from `capability.model_id`,
- live runtimes omit an entrypoint,
- a simulation stub declares hardware requirements,
- hardware plug-ins disable sandboxing,
- tags or entrypoints contain invalid whitespace.

## Gateway Integration

`POST /v1/model-plugins/register` accepts a `ModelPluginManifest`, stores it in
the gateway registry, and registers the contained `ModelCapabilityDescriptor`
with the existing capability gate. Percepts still pass through the same
registered-model validation path before they reach context fusion.

This keeps the plug-in system open and extensible while preserving the OSIP
rule that models declare their public outputs before producing runtime data.
