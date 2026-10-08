from __future__ import annotations

import os

import pytest

from semantic_python import LayaBackend, OpenAIBackend, Semantic, configure


@pytest.mark.live
@pytest.mark.parametrize("backend_name", ["laya", "openai"])
def test_selected_live_backend_returns_a_conforming_decision(backend_name):
    if os.environ.get("SEMANTIC_PYTHON_LIVE_BACKEND") != backend_name:
        pytest.skip(f"set SEMANTIC_PYTHON_LIVE_BACKEND={backend_name} to run")

    backend = LayaBackend() if backend_name == "laya" else OpenAIBackend()
    configure(backend=backend, cache=False)
    decision = Semantic("I'm finished and want to stop.") == "the user wants to stop"

    assert isinstance(decision.value, bool)
    assert 0.0 <= decision.probability <= 1.0
    assert decision.backend == backend_name
    assert decision.model
