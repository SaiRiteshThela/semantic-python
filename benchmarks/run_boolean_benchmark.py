"""Small reproducible benchmark for Boolean semantic decisions."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from dataclasses import asdict, dataclass
from typing import Any

from semantic_python import FakeBackend, LayaBackend, OpenAIBackend, Semantic, configure

PROPOSITION = "the user wants to stop"
EXAMPLES: tuple[tuple[str, bool | None, str], ...] = (
    ("I'm done for today.", True, "positive"),
    ("Please stop the process.", True, "positive"),
    ("That is enough; end the session.", True, "positive"),
    ("Do not stop yet.", False, "negation"),
    ("Keep going with the next task.", False, "negative"),
    ("Continue until I say otherwise.", False, "negative"),
    ("We can review this again tomorrow.", None, "ambiguous"),
    ("Maybe finish soon.", None, "ambiguous"),
)


@dataclass(frozen=True, slots=True)
class ExampleResult:
    state: str
    expected: bool | None
    tag: str
    value: bool
    probability: float
    latency_ms: float
    model: str | None


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def select_backend(name: str) -> Any:
    if name == "fake":
        responses = {
            (state, PROPOSITION): (expected, 0.98 if expected else 0.02)
            for state, expected, _ in EXAMPLES
            if expected is not None
        }
        responses.update(
            {
                (state, PROPOSITION): (False, 0.5)
                for state, expected, _ in EXAMPLES
                if expected is None
            }
        )
        return FakeBackend(responses)
    if name == "laya":
        return LayaBackend()
    return OpenAIBackend()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("fake", "laya", "openai"), default="fake")
    args = parser.parse_args()

    backend = select_backend(args.backend)
    configure(backend=backend, cache=False)
    results: list[ExampleResult] = []

    for state, expected, tag in EXAMPLES:
        started = time.perf_counter()
        decision = Semantic(state) == PROPOSITION
        elapsed_ms = (time.perf_counter() - started) * 1000
        results.append(
            ExampleResult(
                state=state,
                expected=expected,
                tag=tag,
                value=decision.value,
                probability=decision.probability,
                latency_ms=elapsed_ms,
                model=decision.model,
            )
        )

    labeled = [result for result in results if result.expected is not None]
    correct = sum(result.value is result.expected for result in labeled)
    false_positives = sum(result.value and result.expected is False for result in labeled)
    false_negatives = sum(not result.value and result.expected is True for result in labeled)
    brier = statistics.mean(
        (result.probability - float(result.expected)) ** 2 for result in labeled
    )
    latencies = [result.latency_ms for result in results]
    report = {
        "backend": args.backend,
        "backend_identity": backend.identity,
        "labeled_examples": len(labeled),
        "ambiguous_examples": len(results) - len(labeled),
        "accuracy": correct / len(labeled),
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "brier_score": brier,
        "latency_ms": {
            "p50": statistics.median(latencies),
            "p95": percentile(latencies, 0.95),
        },
        "results": [asdict(result) for result in results],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
