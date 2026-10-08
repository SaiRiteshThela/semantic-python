from __future__ import annotations

from types import SimpleNamespace

import pytest

from semantic_python import BackendError, OpenAIBackend, Semantic, configure


class StubResponses:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text, id="resp_test")


class StubClient:
    def __init__(self, output_text: str) -> None:
        self.responses = StubResponses(output_text)


def test_openai_backend_uses_structured_output_without_network():
    client = StubClient('{"value":true,"probability":0.93}')
    configure(backend=OpenAIBackend(client=client, model="test-openai"), cache=False)

    decision = Semantic("I'm done") == "the user wants to stop"

    assert decision.value is True
    assert decision.probability == 0.93
    assert decision.backend == "openai"
    assert decision.model == "test-openai"
    assert decision.metadata["confidence_kind"] == "model_reported"
    assert decision.metadata["probability_semantics"] == "p_proposition_true"
    assert decision.metadata["provider_version"] == OpenAIBackend(client=client).version
    assert decision.metadata["response_id"] == "resp_test"
    call = client.responses.calls[0]
    assert call["text"]["format"]["strict"] is True
    assert "not confidence" in call["instructions"]
    assert (
        "P(proposition=true)"
        in call["text"]["format"]["schema"]["properties"]["probability"]["description"]
    )
    assert "I'm done" in call["input"]


@pytest.mark.parametrize(
    "output",
    [
        "not json",
        '{"value":"yes","probability":0.9}',
        '{"value":true,"probability":1.1}',
        '{"value":false,"probability":0.99}',
        '{"value":true,"probability":0.01}',
    ],
)
def test_openai_backend_rejects_malformed_decisions(output):
    configure(backend=OpenAIBackend(client=StubClient(output)), cache=False)

    with pytest.raises(BackendError):
        _ = Semantic("state") == "proposition"
