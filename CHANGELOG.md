# Changelog

All notable changes will be documented here.

## [0.1.0a1] - 2026-10-07

### Added

- Initial experimental `Semantic[str]` runtime.
- Inspectable, bool-coercible decisions with explicit uncertainty handling.
- Deterministic fake backend, caching, and offline record/replay support.
- Experimental Laya 0.4 and OpenAI backend adapters with explicit data-egress
  documentation.
- Polished offline examples and opt-in OpenAI notebooks.
- Python 3.10 through 3.13 testing, strict typing, and release artifact validation.

### Security

- Raw semantic state is excluded from decision recordings.
- Hosted credentials are loaded from environment or secure runtime configuration.
