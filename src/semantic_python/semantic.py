"""The explicit semantic value boundary."""

from __future__ import annotations

from typing import ClassVar, Generic, TypeVar, cast

from .cache import decision_cache_key, state_digest
from .config import get_config, require_backend
from .decision import BackendError, Decision, InvalidComparisonError

T = TypeVar("T")


class Semantic(Generic[T]):
    __slots__ = ("_value",)
    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    def __init__(self, value: T) -> None:
        if not isinstance(value, str):
            raise TypeError("v0.1 supports only Semantic[str]")
        self._value = cast(str, value)

    @property
    def value(self) -> T:
        return cast(T, self._value)

    def __repr__(self) -> str:
        return f"Semantic({self._value!r})"

    def __eq__(self, proposition: object) -> Decision[bool]:  # type: ignore[override]
        if isinstance(proposition, Semantic):
            raise InvalidComparisonError(
                "Semantic-to-Semantic equality is ambiguous; compare explicitly"
            )
        if not isinstance(proposition, str):
            raise InvalidComparisonError(
                "Semantic[str] can only be compared with a proposition string"
            )
        return self._decide(proposition)

    def __ne__(self, proposition: object) -> Decision[bool]:  # type: ignore[override]
        return self.__eq__(proposition).negated()

    def _decide(self, proposition: str) -> Decision[bool]:
        config = get_config()
        backend = require_backend()
        identity = getattr(backend, "identity", type(backend).__qualname__)
        key = decision_cache_key(
            backend_identity=identity,
            state=self._value,
            proposition=proposition,
            configuration={
                "false_threshold": config.policy.false_threshold,
                "true_threshold": config.policy.true_threshold,
                "uncertainty": config.policy.uncertainty.value,
                "fallback": config.policy.fallback,
            },
        )
        if config.cache is not None:
            cached = config.cache.get(key)
            if cached is not None:
                return cached.with_policy(config.policy)
        try:
            raw = backend.boolean(self._value, proposition)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as error:
            if isinstance(error, BackendError):
                raise
            raise BackendError(f"backend {identity!r} failed: {error}") from error
        if not isinstance(raw, Decision) or not isinstance(raw.value, bool):
            raise BackendError("boolean backend must return Decision[bool]")
        if raw.proposition != proposition or raw.state_hash != state_digest(self._value):
            raise BackendError("backend returned mismatched proposition or state hash")
        decision = raw.with_policy(config.policy)
        if config.cache is not None:
            config.cache.put(key, decision)
        if config.recorder is not None:
            config.recorder.record(decision)
        return decision
