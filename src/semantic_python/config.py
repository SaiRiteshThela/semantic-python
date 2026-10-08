"""Runtime configuration scoped with context variables."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, cast

from .backends.base import DecisionBackend
from .cache import MemoryDecisionCache
from .decision import ConfigurationError, TruthPolicy, UncertaintyPolicy
from .replay import DecisionRecorder


@dataclass(frozen=True, slots=True)
class Config:
    backend: DecisionBackend | None = None
    policy: TruthPolicy = field(default_factory=TruthPolicy)
    cache: MemoryDecisionCache | None = None
    recorder: DecisionRecorder | None = None


def _default_config() -> Config:
    # Equality followed by inequality should reuse the same underlying judgment.
    return Config(cache=MemoryDecisionCache())


_DEFAULT = _default_config()
_config: ContextVar[Config] = ContextVar("sem_config", default=_DEFAULT)
_UNSET = object()


def get_config() -> Config:
    return _config.get()


def configure(
    *,
    backend: DecisionBackend | object | None = _UNSET,
    threshold: float | None = None,
    true_threshold: float | None = None,
    false_threshold: float | None = None,
    uncertainty: UncertaintyPolicy | str | None = None,
    fallback: bool | None = None,
    cache: MemoryDecisionCache | bool | object | None = _UNSET,
    recorder: DecisionRecorder | object | None = _UNSET,
) -> Config:
    current = get_config()
    high = threshold if threshold is not None else true_threshold
    low = (
        1.0 - threshold
        if threshold is not None
        else false_threshold
        if false_threshold is not None
        else current.policy.false_threshold
    )
    uncertainty_policy = (
        UncertaintyPolicy(uncertainty) if uncertainty is not None else current.policy.uncertainty
    )
    policy = TruthPolicy(
        false_threshold=low,
        true_threshold=high if high is not None else current.policy.true_threshold,
        uncertainty=uncertainty_policy,
        fallback=fallback if fallback is not None else current.policy.fallback,
    )
    selected_cache = MemoryDecisionCache() if cache is True else (None if cache is False else cache)
    result = Config(
        backend=current.backend if backend is _UNSET else cast(DecisionBackend | None, backend),
        policy=policy,
        cache=(
            current.cache if cache is _UNSET else cast(MemoryDecisionCache | None, selected_cache)
        ),
        recorder=(
            current.recorder if recorder is _UNSET else cast(DecisionRecorder | None, recorder)
        ),
    )
    _config.set(result)
    return result


def reset_config() -> None:
    _config.set(_default_config())


@contextmanager
def configuration(**changes: Any) -> Iterator[Config]:
    previous = get_config()
    try:
        configured = configure(**changes)
        yield configured
    finally:
        _config.set(previous)


def require_backend() -> DecisionBackend:
    backend = get_config().backend
    if backend is None:
        raise ConfigurationError("no semantic backend configured; call configure(backend=...)")
    return backend
