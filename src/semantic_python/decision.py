"""Structured semantic decisions and their truthiness policy."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class SemanticError(Exception):
    """Base class for semantic-runtime errors."""


class BackendError(SemanticError):
    """A semantic backend could not produce a decision."""


class ConfigurationError(SemanticError):
    """The semantic runtime is not configured correctly."""


class InvalidComparisonError(TypeError, SemanticError):
    """An operand has no defined implicit semantic comparison."""


class UncertaintyPolicy(str, Enum):
    RAISE = "raise"
    FALLBACK = "fallback"
    USE_VALUE = "use_value"


class UncertainDecisionError(SemanticError):
    """Raised when a decision falls inside the configured uncertainty band."""

    def __init__(self, decision: Decision[Any]) -> None:
        self.decision = decision
        super().__init__(
            f"semantic decision is uncertain (probability={decision.probability:.3f}, "
            f"proposition={decision.proposition!r})"
        )


@dataclass(frozen=True, slots=True)
class TruthPolicy:
    """Controls conversion of a boolean decision to a Python bool."""

    false_threshold: float = 0.15
    true_threshold: float = 0.85
    uncertainty: UncertaintyPolicy = UncertaintyPolicy.RAISE
    fallback: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.false_threshold < self.true_threshold <= 1.0:
            raise ValueError("thresholds must satisfy 0 <= false < true <= 1")
        object.__setattr__(self, "uncertainty", UncertaintyPolicy(self.uncertainty))

    def resolve(self, decision: Decision[bool]) -> bool:
        if decision.probability >= self.true_threshold:
            return True
        if decision.probability <= self.false_threshold:
            return False
        if self.uncertainty is UncertaintyPolicy.FALLBACK:
            return self.fallback
        if self.uncertainty is UncertaintyPolicy.USE_VALUE:
            return decision.value
        raise UncertainDecisionError(decision)


@dataclass(frozen=True, slots=True)
class Decision(Generic[T]):
    """A typed result retaining confidence and provenance.

    ``probability`` is the probability that ``proposition`` is true, rather than
    confidence in the selected value. This makes negation mechanically exact.
    """

    value: T
    probability: float
    backend: str
    proposition: str
    state_hash: str
    model: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    policy: TruthPolicy = field(default_factory=TruthPolicy, repr=False, compare=False)
    cached: bool = field(default=False, compare=False)
    replayed: bool = field(default=False, compare=False)

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")
        if not self.backend:
            raise ValueError("backend must not be empty")
        if not self.proposition:
            raise ValueError("proposition must not be empty")
        if not self.state_hash:
            raise ValueError("state_hash must not be empty")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def __bool__(self) -> bool:
        if not isinstance(self.value, bool):
            raise TypeError("only boolean decisions have truthiness")
        return self.policy.resolve(self)  # type: ignore[arg-type]

    def negated(self) -> Decision[bool]:
        if not isinstance(self.value, bool):
            raise TypeError("only boolean decisions can be negated")
        return Decision(
            value=not self.value,
            probability=1.0 - self.probability,
            backend=self.backend,
            model=self.model,
            proposition=f"not ({self.proposition})",
            state_hash=self.state_hash,
            metadata={**self.metadata, "negated_from": self.proposition},
            policy=self.policy,
            cached=self.cached,
            replayed=self.replayed,
        )

    def with_policy(self, policy: TruthPolicy) -> Decision[T]:
        return replace(self, policy=policy)
