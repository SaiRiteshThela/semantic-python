"""Deterministic, offline backend for examples and tests."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TypeAlias

from ..cache import state_digest
from ..decision import Decision
from .base import BackendBase

FakeResult: TypeAlias = bool | float | tuple[bool, float]


class FakeBackend(BackendBase):
    def __init__(
        self,
        responses: Mapping[tuple[str, str], FakeResult] | None = None,
        *,
        default: FakeResult | None = None,
        resolver: Callable[[str, str], FakeResult] | None = None,
        name: str = "fake",
        model: str = "deterministic-v1",
    ) -> None:
        self.responses = dict(responses or {})
        self.default = default
        self.resolver = resolver
        self.name = name
        self.model = model
        self.calls = 0

    @property
    def identity(self) -> str:
        return f"{self.name}:{self.model}"

    def boolean(self, state: str, proposition: str) -> Decision[bool]:
        self.calls += 1
        key = (state, proposition)
        if key in self.responses:
            result = self.responses[key]
        elif self.resolver is not None:
            result = self.resolver(state, proposition)
        elif self.default is not None:
            result = self.default
        else:
            raise KeyError(f"no fake response for state/proposition: {key!r}")
        value, probability = self._coerce(result)
        return Decision(
            value=value,
            probability=probability,
            backend=self.name,
            model=self.model,
            proposition=proposition,
            state_hash=state_digest(state),
        )

    @staticmethod
    def _coerce(result: FakeResult) -> tuple[bool, float]:
        if isinstance(result, tuple):
            value, probability = result
        elif isinstance(result, bool):
            value, probability = result, 1.0 if result else 0.0
        else:
            probability = float(result)
            value = probability >= 0.5
        return bool(value), float(probability)
