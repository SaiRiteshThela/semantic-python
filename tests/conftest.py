from __future__ import annotations

import pytest

from semantic_python import reset_config


@pytest.fixture(autouse=True)
def _isolated_semantic_configuration():
    """No test may leak backend, cache, or policy state into another test."""
    reset_config()
    yield
    reset_config()
