# Contributing

Semantic Python is experimental. Open an issue before proposing changes to public semantics.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check .
ruff format --check .
mypy
python -m build
```

Keep changes small, add offline tests for behavioral changes, and never require paid credentials in the default test suite. Live provider tests must be explicitly opted into.

## Design changes

Changes to equality, truthiness, uncertainty, privacy, or backend behavior need a written rationale and documentation. Ordinary non-semantic Python behavior must remain untouched.

## Security and privacy

Do not commit credentials or fixtures containing private user input. Prefer hashed or redacted state in logs and bug reports.
