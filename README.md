# Semantic Python

[![PyPI](https://img.shields.io/pypi/v/semantic-python.svg)](https://pypi.org/project/semantic-python/)
[![Python](https://img.shields.io/pypi/pyversions/semantic-python.svg)](https://pypi.org/project/semantic-python/)
[![CI](https://github.com/SaiRiteshThela/semantic-python/actions/workflows/ci.yml/badge.svg)](https://github.com/SaiRiteshThela/semantic-python/actions/workflows/ci.yml)

> Python, but `==` can understand meaning.

Semantic Python is not a model like Laya or Jev. It is an opt-in Python value
layer that turns backend inference into inspectable decisions for normal Python
control flow. Only `Semantic(...)` values can invoke a model.

[Compare Jev, Laya, JevLang, and Semantic Python](https://sairiteshthela.github.io/semantic-python/comparisons/jev-laya-semantic-python/)

## Install

```bash
python -m pip install 'semantic-python[openai]'
export OPENAI_API_KEY="..."
```

## Demo

Use natural-language intent in ordinary loops and async code:

`functions` · `if` · `try/except` · `for` · `while` · `comprehensions` ·
`generators` · `classes` · `with` · `async/await`

```python
import asyncio

from semantic_python import (
    OpenAIBackend,
    Semantic,
    UncertainDecisionError,
    configure,
)

STOP = "the user wants to stop"

configure(
    backend=OpenAIBackend(model="gpt-6-luna"),
    true_threshold=0.85,
    false_threshold=0.15,
    uncertainty="raise",
)


def decide(text: str):
    return Semantic(text) == STOP


messages = [
    "Continue with the next ticket.",
    "Save the work and close this session.",
]

for text in messages:
    decision = decide(text)
    print(f"stop={decision.value} p={decision.probability:.2f} model={decision.model}")

    try:
        if decision:
            print("Stop requested")
            break
    except UncertainDecisionError:
        print("Send to human review")


async def decide_async(text: str):
    return await asyncio.to_thread(decide, text)


async_result = asyncio.run(decide_async(text))
opposite = Semantic(text) != STOP

print("async cache hit:", async_result.cached)
print("negated:", opposite.value, opposite.probability)
```

The comparison returns a bool-coercible `Decision`, so `if` and loops work
normally while probability, model provenance, caching, and replay remain
available. `!=` negates the same judgment instead of issuing a second inference.

## More Python patterns

These examples continue with the configured backend and `STOP` proposition from
the main demo.

### `while`

```python
queue = iter(["Keep going", "Not yet", "Finished for today"])
message = Semantic(next(queue))

while message != STOP:
    print("Processing:", message.value)
    message = Semantic(next(queue))
```

### Comprehensions and generators

```python
texts = ["Continue", "Pause here", "That is all for today"]
decisions = {text: decide(text) for text in texts}

stop_requests = [text for text, decision in decisions.items() if decision.value]

probabilities = (decision.probability for decision in decisions.values())
print(stop_requests, list(probabilities))
```

### Classes

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntentRule:
    proposition: str

    def evaluate(self, text: str):
        return Semantic(text) == self.proposition


stop_rule = IntentRule("the user wants to stop")
decision = stop_rule.evaluate("Please close the session")
print(decision.value, decision.probability)
```

### Context managers and offline tests

```python
from semantic_python import FakeBackend, configuration

state = "I'm done"
fixtures = {(state, STOP): (True, 0.99)}

with configuration(backend=FakeBackend(fixtures), cache=False):
    assert Semantic(state) == STOP
```

## Backends

Application code stays the same when the configured backend changes.

| Backend | Install | Purpose |
| --- | --- | --- |
| `OpenAIBackend` | `semantic-python[openai]` | Hosted inference |
| `LayaBackend` | `semantic-python[laya]` | Local inference |
| `FakeBackend` | Included | Deterministic offline tests |

OpenAI receives the wrapped state and proposition. Laya may download model
checkpoints on first use. FakeBackend performs no network requests.

Jev is a hosted decision model/API, Laya is an open-weights decision engine,
and Semantic Python is the Python value layer around explicitly selected
backends. Jev integration is roadmap research and is not currently implemented.

## Semantics

| Expression | Result |
| --- | --- |
| `plain_string == other` | Ordinary Python equality |
| `Semantic(text) == proposition` | Inspectable semantic `Decision` |
| `Semantic(text) != proposition` | Negated cached judgment |
| `semantic is other` | Ordinary Python identity |
| `Semantic(...) == Semantic(...)` | Rejected as ambiguous |
| `hash(Semantic(...))` | Rejected; inference is never used for hashing |

Probabilities at or above `0.85` resolve true, probabilities at or below `0.15`
resolve false, and the default policy raises `UncertainDecisionError` between
those thresholds. Backend failures are raised rather than converted to `False`.

## Examples

- [OpenAI demo](examples/semantic_python_demo.ipynb)
- [Python control-flow demo](examples/python_primitives_demo.ipynb)
- [Stop loop](examples/stop_loop.py)
- [Ticket routing](examples/ticket_routing.py)
- [Uncertainty and escalation](examples/escalation.py)

The offline examples run without credentials:

```bash
python -m pip install -e .
python examples/stop_loop.py
python examples/ticket_routing.py
python examples/escalation.py
```

## Safety

- Model probability is an estimate, not truth or authorization.
- Hosted inference can transmit sensitive text and incur cost.
- Consequential actions should use conservative thresholds and human review.

See [semantics](docs/semantics.md), [backends](docs/backends.md), and
[uncertainty](docs/uncertainty.md) for the complete behavior.

MIT licensed. Experimental and pre-alpha.
