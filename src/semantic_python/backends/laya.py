"""Optional adapter for the local Laya decision engine.

Laya is imported and its model is loaded only when the first decision is made.
Its zero-shot outputs, especially negation, require application-level evaluation;
they are probabilities, not proof or authorization for consequential actions.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Any

from ..cache import state_digest
from ..decision import BackendError, Decision
from .base import BackendBase


class LayaBackend(BackendBase):
    """Use Laya's ``noul`` head for local proposition decisions.

    Pass an injected router in tests or advanced deployments. Otherwise ``laya``
    is imported lazily; installing the core package does not import torch.
    """

    def __init__(self, router: Any | None = None, *, model: str | None = None) -> None:
        self._router = router
        self.model = model
        try:
            self.version = version("laya")
        except PackageNotFoundError:
            self.version = "not-installed" if router is None else "injected"

    @property
    def identity(self) -> str:
        return f"laya:{self.version}:{self.model or 'auto'}"

    def _get_router(self) -> Any:
        if self._router is None:
            try:
                from laya import Router  # type: ignore[import-not-found]
            except ImportError as error:
                raise BackendError("LayaBackend requires the optional 'laya' package") from error
            self._router = Router()
        return self._router

    def boolean(self, state: str, proposition: str) -> Decision[bool]:
        questions = {
            "decision": {
                "type": "noul",
                "instructions": proposition,
                "criteria": {
                    "true": proposition,
                    "false": f"It is not true that: {proposition}",
                },
            }
        }
        kwargs = {"model": self.model} if self.model is not None else {}
        try:
            result = self._get_router().predict(state, questions, **kwargs)
            probability = float(result["answers"]["decision"]["noul"])
            routing = result["routing"]
            routed_model = str(routing["model"])
        except BackendError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise BackendError(f"Laya returned an invalid decision payload: {error}") from error
        return Decision(
            value=probability >= 0.5,
            probability=probability,
            backend="laya",
            model=routed_model,
            proposition=proposition,
            state_hash=state_digest(state),
            metadata={"routing": dict(routing), "provider_version": self.version},
        )
