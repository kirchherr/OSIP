# OSIP Benchmark Report

Overall: PASS

## Summary

- Scenarios: 5
- Passed: 5
- Failed: 0
- Application profiles: rooms
- Benchmark gate failures: 0
- Context latency p50/p95/p99: 120.0/250.0/250.0 ms
- Action proposal latency p50/p95/p99: 200.0/250.0/250.0 ms
- False-positive contexts: 0
- False-negative contexts: 0
- False-positive actions: 0
- False-negative actions: 0
- Action contract blocks: 4

## Scenarios

| Scenario | Profile | Result | Gates | Contexts | Actions | Context Latency | Action Latency |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fall_candidate | rooms | PASS | all passed | expected: context.possible_fall<br>actual: context.possible_fall | expected: action.room.speaker.ask_help_needed<br>actual: action.room.speaker.ask_help_needed | 70 ms / budget 250 ms | 70 ms / budget 500 ms |
| kitchen_burning_food | rooms | PASS | all passed | expected: context.possible_burning_food<br>actual: context.possible_burning_food | expected: action.notify.local, action.hvac.ventilation_boost<br>actual: action.notify.local, action.hvac.ventilation_boost | 250 ms / budget 250 ms | 250 ms / budget 500 ms |
| normal_cooking_no_alarm | rooms | PASS | all passed | expected: none<br>actual: none | expected: none<br>actual: none | n/a / budget 250 ms | n/a / budget 500 ms |
| sensor_conflict_smoke | rooms | PASS | all passed | expected: context.sensor_conflict<br>actual: context.sensor_conflict | expected: none<br>actual: none | 120 ms / budget 250 ms | n/a / budget 500 ms |
| stale_air_high_occupancy | rooms | PASS | all passed | expected: context.high_occupancy_stale_air<br>actual: context.high_occupancy_stale_air | expected: action.hvac.ventilation_boost<br>actual: action.hvac.ventilation_boost | 200 ms / budget 500 ms | 200 ms / budget 800 ms |
