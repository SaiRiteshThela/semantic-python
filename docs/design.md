# Design

Semantic Python is a library-level experiment: selected values can ask a typed
decision backend whether a proposition holds, while the Python language and all
unwrapped values remain unchanged.

## Boundary and flow

`Semantic(value)` is the only runtime opt-in in v0.1. Comparing a
`Semantic[str]` to a string proposition asks the configured backend for a
boolean decision. The core validates and enriches that result, applies the
configured truth policy, and exposes provenance for inspection.

```text
wrapped state + proposition
          |
          v
  configured backend ----> typed result (value + probability + provenance)
          |                                      |
          +---------- cache / record ------------+
                                                 |
                                                 v
                                           Decision[bool]
```

The backend abstraction owns inference, not language semantics. This gives the
deterministic fake backend and the sole current real-backend target, Laya, the
same typed boundary. The core remains responsible for operand validation,
negation, truth coercion, cache identity, and preserving metadata. Other
provider integrations are roadmap items, not current features.

## Decisions are data

A `Decision` includes the proposed boolean, its probability, backend and model
identity when available, the proposition, and a non-plaintext state identifier.
Keeping this structure makes decisions inspectable and replayable. It also
prevents uncertainty from disappearing prematurely into a bare `bool`.

Synchronous operator syntax is intentionally narrow. It is convenient for
small programs but a real backend can block. Async behavior, batching, and
compiler/import-hook work are deferred until the library MVP is stable.

## Cache and replay boundaries

Only identical decisions are reusable. A stable identity must include backend
and model/version, relevant normalized configuration, state digest, and the
exact proposition. Cached or replayed decisions retain their original metadata.
Changing any inference-relevant input must produce a miss.

Logs and records should avoid plaintext state by default and must never contain
credentials. A state digest protects casual disclosure, not dictionary attacks;
sensitive inputs still require access controls and an appropriate retention
policy.

## Deliberate constraints

The project does not patch `str`, add operators, fork CPython, or make type
annotations execute. It does not silently turn backend failures into negative
answers. These constraints keep ordinary Python deterministic and make the
costly or fallible boundary visible in code.
