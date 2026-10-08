# TODO

## After v0.1

- Evaluate and, if justified, add a Jev hosted-backend adapter.
- Evaluate Kev as an additional local/self-hosted backend.
- Evaluate AnyJev as a research adapter path.
- Define a stable public custom-backend registration API.
- Add configurable retry, timeout, and cost-budget controls for hosted providers.
- Add cross-backend conformance tests and reproducible quality/calibration benchmarks.

These items are deliberately outside v0.1. Laya remains the primary local backend,
OpenAI remains an explicitly selected experimental hosted backend, and `FakeBackend`
exists for deterministic offline development, examples, and tests.
