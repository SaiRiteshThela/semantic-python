from __future__ import annotations

import pytest

from semantic_python import BackendError, Semantic, configure
from semantic_python.backends import LayaBackend


class StubRouter:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def predict(self, state, questions, **kwargs):
        self.calls.append((state, questions, kwargs))
        return self.result


def test_laya_adapter_maps_noul_payload_without_network_access():
    router = StubRouter(
        {
            "answers": {"decision": {"noul": 0.92}},
            "routing": {"model": "injected-model", "device": "cpu"},
        }
    )
    configure(backend=LayaBackend(router=router, model="requested-model"), cache=False)

    decision = Semantic("I'm finished") == "the user wants to stop"

    assert decision.value is True
    assert decision.probability == 0.92
    assert decision.backend == "laya"
    assert decision.model == "injected-model"
    assert decision.metadata["provider_version"] == "injected"
    assert decision.metadata["routing"]["device"] == "cpu"
    state, questions, kwargs = router.calls[0]
    assert state == "I'm finished"
    assert questions["decision"]["type"] == "noul"
    assert questions["decision"]["instructions"] == "the user wants to stop"
    assert kwargs == {"model": "requested-model"}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"answers": {"decision": {"noul": "not-a-number"}}, "routing": {"model": "m"}},
        {"answers": {"decision": {"noul": 0.9}}, "routing": {}},
    ],
)
def test_laya_adapter_rejects_malformed_provider_payloads(payload):
    configure(backend=LayaBackend(router=StubRouter(payload)), cache=False)

    with pytest.raises(BackendError, match="invalid decision payload"):
        _ = Semantic("state") == "proposition"
