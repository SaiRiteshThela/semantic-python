"""Optional OpenAI Responses API backend."""

from __future__ import annotations

import json
import os
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from ..cache import state_digest
from ..decision import BackendError, Decision
from .base import BackendBase

_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {
            "type": "boolean",
            "description": "Whether the proposition is true; true iff probability is at least 0.5.",
        },
        "probability": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": (
                "P(proposition=true), not confidence in the selected boolean value. "
                "A false value therefore has probability below 0.5."
            ),
        },
    },
    "required": ["value", "probability"],
    "additionalProperties": False,
}


class OpenAIBackend(BackendBase):
    """Remote semantic decisions using OpenAI Structured Outputs.

    ``probability`` is model-reported and must be calibrated on application data
    before it is used for consequential automation.
    """

    def __init__(self, client: Any | None = None, *, model: str = "gpt-6-luna") -> None:
        self._client = client
        self.model = model
        try:
            self.version = version("openai")
        except PackageNotFoundError:
            self.version = "not-installed" if client is None else "injected"

    @property
    def identity(self) -> str:
        return f"openai:{self.version}:{self.model}"

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                OpenAI = import_module("openai").OpenAI
            except ImportError as error:
                raise BackendError(
                    "OpenAIBackend requires the optional 'openai' package"
                ) from error
            if not os.environ.get("OPENAI_API_KEY"):
                raise BackendError("OpenAIBackend requires OPENAI_API_KEY")
            self._client = OpenAI()
        return self._client

    def boolean(self, state: str, proposition: str) -> Decision[bool]:
        try:
            response = self._get_client().responses.create(
                model=self.model,
                instructions=(
                    "Decide whether the proposition is true of the supplied state. "
                    "Return the boolean judgment and your estimated P(proposition=true). "
                    "Probability always means probability that the proposition is true, "
                    "not confidence in whichever boolean you select. Set value=true if and "
                    "only if probability is at least 0.5."
                ),
                input=f"State:\n{state}\n\nProposition:\n{proposition}",
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "semantic_decision",
                        "strict": True,
                        "schema": _SCHEMA,
                    }
                },
            )
            payload = json.loads(response.output_text)
            value = payload["value"]
            probability = float(payload["probability"])
            response_id = getattr(response, "id", None)
        except BackendError:
            raise
        except Exception as error:
            raise BackendError(f"OpenAI returned an invalid decision: {error}") from error
        if not isinstance(value, bool):
            raise BackendError("OpenAI decision value must be a boolean")
        if value is not (probability >= 0.5):
            raise BackendError(
                "OpenAI returned inconsistent value and P(proposition=true): "
                f"value={value!r}, probability={probability!r}"
            )
        return Decision(
            value=value,
            probability=probability,
            backend="openai",
            model=self.model,
            proposition=proposition,
            state_hash=state_digest(state),
            metadata={
                "response_id": response_id,
                "confidence_kind": "model_reported",
                "probability_semantics": "p_proposition_true",
                "provider_version": self.version,
            },
        )
