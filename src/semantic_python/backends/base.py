"""Backend-neutral semantic decision protocol."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from ..decision import Decision


@runtime_checkable
class DecisionBackend(Protocol):
    @property
    def identity(self) -> str:
        """Stable backend/model/version identity used by cache keys."""

    def boolean(self, state: str, proposition: str) -> Decision[bool]: ...

    def choice(self, state: str, options: Sequence[str]) -> Decision[str]: ...

    def score(self, state: str, rubric: str) -> Decision[float]: ...


class BackendBase:
    """Convenience base for boolean-only v0.1 backends."""

    def choice(self, state: str, options: Sequence[str]) -> Decision[str]:
        raise NotImplementedError("choice decisions are not implemented in v0.1")

    def score(self, state: str, rubric: str) -> Decision[float]:
        raise NotImplementedError("score decisions are not implemented in v0.1")
