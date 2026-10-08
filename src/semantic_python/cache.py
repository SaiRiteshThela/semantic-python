"""Stable cache keys and an in-memory decision cache."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from threading import RLock
from typing import Any

from .decision import Decision


def state_digest(state: str) -> str:
    return hashlib.sha256(state.encode("utf-8")).hexdigest()


def decision_cache_key(
    *, backend_identity: str, state: str, proposition: str, configuration: Any
) -> str:
    config = json.dumps(configuration, sort_keys=True, separators=(",", ":"), default=str)
    material = "\0".join((backend_identity, state_digest(state), proposition, config))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


class MemoryDecisionCache:
    def __init__(self) -> None:
        self._items: dict[str, Decision[Any]] = {}
        self._lock = RLock()

    def get(self, key: str) -> Decision[Any] | None:
        with self._lock:
            decision = self._items.get(key)
        return replace(decision, cached=True) if decision is not None else None

    def put(self, key: str, decision: Decision[Any]) -> None:
        with self._lock:
            self._items[key] = replace(decision, cached=False)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)
