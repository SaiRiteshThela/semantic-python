# Semantic Python

> Python, but `==` can understand meaning.

Semantic Python adds opt-in, model-backed semantic values to ordinary Python.
Only values explicitly wrapped in `Semantic` can invoke a model; every other
Python value keeps its standard behavior.

```python
from semantic_python import FakeBackend, Semantic, configure

proposition = "the user wants to stop"
configure(backend=FakeBackend({("I'm done", proposition): (True, 0.98)}))

message = Semantic("I'm done")
if message == proposition:
    print("Stop requested")
```

The comparison returns an inspectable `Decision` containing the Boolean result,
probability, backend, model, proposition, and a digest of the input state.

> [!WARNING]
> Semantic Python is experimental and pre-alpha. Model decisions are estimates,
> not facts or authorization for consequential actions.

## Installation

```bash
python -m pip install semantic-python
```

The distribution name is `semantic-python`; the import package is
`semantic_python`.

## Deterministic quickstart

The fake backend provides a complete offline example with no API key or network
access:

```python
from semantic_python import FakeBackend, Semantic, configure

PROPOSITION = "the user wants to stop"

backend = FakeBackend(
    {
        ("I'm done", PROPOSITION): (True, 0.98),
        ("Keep going", PROPOSITION): (False, 0.03),
    }
)
configure(backend=backend, threshold=0.85)

message = Semantic("I'm done")
decision = message == PROPOSITION

print(decision.value)  # True
print(decision.probability)  # 0.98
print(decision.backend)  # fake

if decision:
    print("Stopping")
```

## OpenAI backend

Install the optional dependency and provide the key through the environment:

```bash
python -m pip install 'semantic-python[openai]'
export OPENAI_API_KEY="..."
```

Select OpenAI explicitly:

```python
from semantic_python import OpenAIBackend, Semantic, configure

configure(
    backend=OpenAIBackend(model="gpt-6-luna"),
    true_threshold=0.85,
    false_threshold=0.15,
    uncertainty="raise",
)

message = Semantic("Please save my work and close this session.")
decision = message == "the user wants to stop"

print(
    decision.value,
    decision.probability,
    decision.backend,
    decision.model,
)
```

This comparison sends the wrapped state and proposition to OpenAI and may incur
latency and API cost. The probability is model-reported and is not independently
calibrated by this package.

## Laya backend

Laya is the primary local backend:

```bash
python -m pip install 'semantic-python[laya]'
```

```python
from semantic_python import LayaBackend, Semantic, configure

configure(backend=LayaBackend(), threshold=0.85)
decision = Semantic("I'm finished for today") == "the user wants to stop"

print(decision.value, decision.probability, decision.model)
```

The first prediction may download model checkpoints. Review the
[Laya verification record](docs/laya-verification.md) before deployment.

## Comparison semantics

| Expression | Behavior |
| --- | --- |
| `"done" == "stop"` | Normal Python equality; never invokes a model. |
| `Semantic(text) == proposition` | Produces a semantic `Decision`. |
| `Semantic(text) != proposition` | Negates the same cached judgment. |
| `semantic is other` | Normal Python identity. |
| `Semantic(...) == Semantic(...)` | Rejected as ambiguous. |
| `Semantic(...) == non_string` | Rejected. |
| `hash(Semantic(...))` | Rejected; hashing never invokes inference. |

The default truth policy accepts probabilities at or above `0.85`, rejects
probabilities at or below `0.15`, and raises `UncertainDecisionError` between
those bounds.

Backend failures are raised explicitly rather than silently converted to
`False`.

## Why return a `Decision`?

A model judgment should not lose its uncertainty or origin when used in control
flow. A decision preserves:

- `value`: the backend's Boolean classification;
- `probability`: `P(proposition=true)`;
- `backend` and `model`: inference provenance;
- `proposition`: the question evaluated;
- `state_hash`: a non-plaintext identifier for the wrapped state;
- `cached`: whether the result came from the decision cache;
- backend-specific metadata.

`Decision` is bool-coercible, so it works with ordinary `if` and `while`
statements while remaining available for inspection.

## Examples

- [`stop_loop.py`](examples/stop_loop.py) — semantic control flow;
- [`ticket_routing.py`](examples/ticket_routing.py) — deterministic routing;
- [`escalation.py`](examples/escalation.py) — uncertainty and human review;
- [`semantic_python_demo.ipynb`](examples/semantic_python_demo.ipynb) — focused
  OpenAI demonstration;
- [`python_primitives_demo.ipynb`](examples/python_primitives_demo.ipynb) —
  Python language features with an OpenAI-backed workflow.

Run the offline examples from the repository root:

```bash
python examples/stop_loop.py
python examples/ticket_routing.py
python examples/escalation.py
```

## VS Code notebooks

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[openai,notebook]'
python -m ipykernel install --user --name sempy --display-name "Python (sempy)"
```

Open a notebook and select `Python (sempy)` from **Select Kernel**. The notebooks
request `OPENAI_API_KEY` through `getpass` when it is not already available in
the environment.

## Safety and privacy

- Hosted backends transmit the wrapped state and proposition to their provider.
- Local backends may download checkpoints and load substantial dependencies.
- Model outputs can be wrong, biased, nondeterministic, or poorly calibrated.
- A state digest reduces plaintext exposure but does not anonymize predictable
  input.
- Consequential actions should use conservative thresholds and human review.
- API keys belong in environment variables or a secrets manager, never source
  files or notebooks.

See [Backends and data egress](docs/backends.md) and
[Uncertainty and safe decisions](docs/uncertainty.md) for the complete model.

## Development

```bash
git clone git@github.com:SaiRiteshThela/semantic-python.git
cd semantic-python
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

pytest --cov=semantic_python --cov-report=term-missing
ruff check .
ruff format --check .
mypy
```

The offline test suite does not require model downloads, network access, or API
keys. Live backend tests are opt-in.

## Documentation

- [Design](docs/design.md)
- [Comparison semantics](docs/semantics.md)
- [Backends and data egress](docs/backends.md)
- [Laya verification](docs/laya-verification.md)
- [Uncertainty](docs/uncertainty.md)
- [Roadmap and limitations](docs/roadmap.md)
- [Benchmark harness](benchmarks/README.md)

## License

Semantic Python is available under the [MIT License](LICENSE).
