"""Privacy-conscious JSONL recording and deterministic replay."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from threading import RLock
from typing import IO, Any, cast

from .backends.base import BackendBase
from .cache import state_digest
from .decision import Decision


def decision_to_record(decision: Decision[Any]) -> dict[str, Any]:
    return {
        "value": decision.value,
        "probability": decision.probability,
        "backend": decision.backend,
        "model": decision.model,
        "proposition": decision.proposition,
        "state_hash": decision.state_hash,
        "metadata": dict(decision.metadata),
    }


class DecisionRecorder:
    """Append decisions as JSON lines; raw semantic state is never recorded."""

    def __init__(self, target: str | Path | IO[str]) -> None:
        self.target = target
        self._lock = RLock()

    def record(self, decision: Decision[Any]) -> None:
        line = json.dumps(decision_to_record(decision), sort_keys=True) + "\n"
        with self._lock:
            if hasattr(self.target, "write"):
                stream = cast(IO[str], self.target)
                stream.write(line)
                stream.flush()
            else:
                with Path(self.target).open("a", encoding="utf-8") as stream:
                    stream.write(line)


class ReplayBackend(BackendBase):
    """Backend that matches recorded decisions by state hash and proposition."""

    def __init__(self, source: str | Path | IO[str] | Iterable[dict[str, Any]]) -> None:
        if isinstance(source, (str, Path)):
            with Path(source).open(encoding="utf-8") as stream:
                records = [json.loads(line) for line in stream if line.strip()]
        elif hasattr(source, "read"):
            replay_stream = cast(IO[str], source)
            records = [json.loads(line) for line in replay_stream if line.strip()]
        else:
            records = list(source)
        self._records = {(r["state_hash"], r["proposition"]): r for r in records}

    @property
    def identity(self) -> str:
        return "replay:jsonl-v1"

    def boolean(self, state: str, proposition: str) -> Decision[bool]:
        digest = state_digest(state)
        try:
            record = self._records[(digest, proposition)]
        except KeyError as error:
            raise KeyError(f"no replay decision for {digest}:{proposition}") from error
        return Decision(
            value=bool(record["value"]),
            probability=float(record["probability"]),
            backend=str(record["backend"]),
            model=record.get("model"),
            proposition=proposition,
            state_hash=digest,
            metadata=record.get("metadata", {}),
            replayed=True,
        )
