# Roadmap and limitations

Semantic Python is experimental and pre-alpha. The immediate goal is a small,
testable library MVP, not a new Python dialect.

## v0.1

- explicit `Semantic[str]` wrapping;
- bool-coercible, inspectable decisions from string propositions;
- consistent single-inference equality and inequality;
- deterministic fake backend and fully offline tests;
- explicit threshold, uncertainty, and backend-error policies;
- stable cache identities, redacted inspection, and replay primitives;
- an evaluation-driven Laya adapter as the primary local backend;
- an explicitly selected experimental OpenAI hosted backend;
- three installable, reproducible examples.

The Laya adapter is experimental. Its API, license, installation behavior, and
published limitations are recorded in `laya-verification.md`. Quality, privacy
properties, and latency still need deployment-specific validation before it is
treated as production-ready.

## Later candidates

After the MVP is stable, v0.2 may explore an annotation-aware import hook,
single-decision lowering for semantic `match`-like behavior, a record/replay CLI,
batching, async support, expanded benchmarks, and static warnings for unchanged
loop state.

Longer-term work may include scoring/ranking, type-checker and editor support,
dataset-driven CI quality gates, and research into Jev, Kev, AnyJev, hosted, or
custom providers. None of those additional providers is a current feature or
commitment.

## Current limitations

- Model results can be wrong, biased, poorly calibrated, and nondeterministic.
- Real inference adds latency; synchronous comparison can block.
- Hosted inference may transmit data and incur cost.
- A hash in logs reduces plaintext exposure but does not anonymize predictable
  or low-entropy inputs.
- Only string proposition comparisons are in scope for v0.1.
- Explicit re-wrapping is required after reassignment.
- Pattern matching, ordering, arithmetic, and annotation-only runtime behavior
  are not supported.
- Serialization, the async contract, and broader platform support remain open
  design decisions. The current release targets CPython 3.10 through 3.13 on
  Linux, uses the MIT license, and documents its Laya integration contract.

Compiler work, publishing, public releases, account creation, and promotion are
separate decisions and are not prerequisites for proving the library MVP.
