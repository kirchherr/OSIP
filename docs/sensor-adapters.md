# Sensor Adapters

`SensorToPerceptAdapter` is the first generic ingress boundary for real sensor
integrations. It keeps OSIP Core hardware-free while defining how future camera,
audio, air-quality, robot, or building-system SDKs can feed the runtime.

The adapter does not import vendor SDKs. A live integration only has to provide
a small `SensorReadingSource` with:

```python
async def receive() -> SensorReading | None: ...
```

The reference adapter then:

- validates the reading timestamp, modality, claims, quality, and latency,
- checks modality and claim labels against a `ModelCapabilityDescriptor`,
- converts the reading to an OSIP `PerceptPacket`,
- publishes to `omnisense.percepts.<modality>.<source_model>`,
- returns an `AdapterRunResult` for deterministic tests and diagnostics.

Minimal reading shape:

```json
{
  "reading_id": "reading_0001",
  "modality": "rgb",
  "timestamp": "2026-06-12T14:31:09.210Z",
  "valid_for_ms": 800,
  "latency_ms": 18,
  "claims": [{"label": "person.presence", "confidence": 0.91, "value": true}],
  "quality": {"status": "usable"}
}
```

This is not a hardware driver. Hardware-specific code belongs in later adapter
wrappers that translate SDK data into `SensorReading` records and set
`requires_hardware=true` in adapter metadata.
