from __future__ import annotations

import pytest

from semantic_python import (
    BackendError,
    ConfigurationError,
    Decision,
    FakeBackend,
    InvalidComparisonError,
    Semantic,
    UncertainDecisionError,
    configure,
)


def configured_backend(responses, **configuration):
    backend = FakeBackend(responses)
    configure(backend=backend, **configuration)
    return backend


@pytest.mark.parametrize(
    ("state", "proposition", "answer"),
    [
        ("I'm done", "the user wants to stop", (True, 0.98)),
        ("keep going", "the user wants to stop", (False, 0.01)),
        ("don't stop", "the user wants to stop", (False, 0.01)),
    ],
)
def test_semantic_string_equality_returns_inspectable_decision(state, proposition, answer):
    backend = configured_backend({(state, proposition): answer})

    decision = Semantic(state) == proposition

    assert isinstance(decision, Decision)
    assert decision.value is answer[0]
    assert decision.probability == answer[1]
    assert decision.proposition == proposition
    assert decision.backend == backend.name
    assert decision.model == backend.model
    assert decision.state_hash
    assert state not in decision.state_hash
    assert bool(decision) is answer[0]


def test_inequality_negates_one_inference_instead_of_rephrasing_it():
    backend = configured_backend({("I'm done", "the user wants to stop"): (True, 0.96)})
    value = Semantic("I'm done")

    equal = value == "the user wants to stop"
    unequal = value != "the user wants to stop"

    assert equal.value is True
    assert unequal.value is False
    assert bool(unequal) is False
    assert unequal.metadata["negated_from"] == equal.proposition
    # The second comparison may be served by the identical-decision cache, but
    # it must never ask a separate, negatively worded model question.
    assert backend.calls == 1


def test_identity_remains_python_identity_and_never_calls_backend():
    backend = configured_backend({}, cache=False)
    value = Semantic("same")

    assert value is value
    assert value is not Semantic("same")
    assert backend.calls == 0


def test_normal_strings_keep_literal_python_semantics_without_configuration():
    assert ("I'm done" == "the user wants to stop") is False
    assert ("stop" == "stop") is True
    assert ("stop" != "continue") is True


def test_missing_backend_is_an_explicit_configuration_error():
    with pytest.raises(ConfigurationError):
        _ = Semantic("hello") == "the user is greeting us"


@pytest.mark.parametrize("operand", [None, 1, 3.14, object(), ["proposition"]])
def test_non_string_comparison_is_rejected_without_inference(operand):
    backend = configured_backend({}, cache=False)

    with pytest.raises(InvalidComparisonError):
        _ = Semantic("state") == operand

    assert backend.calls == 0


def test_semantic_to_semantic_comparison_is_rejected_without_inference():
    backend = configured_backend({}, cache=False)

    with pytest.raises(InvalidComparisonError):
        _ = Semantic("left") == Semantic("right")

    assert backend.calls == 0


def test_semantic_values_are_unhashable_and_hashing_never_infers():
    backend = configured_backend({}, cache=False)
    value = Semantic("sensitive")

    with pytest.raises(TypeError):
        hash(value)
    with pytest.raises(TypeError):
        _ = {value}

    assert backend.calls == 0


@pytest.mark.parametrize("probability", [0.16, 0.5, 0.84])
def test_uncertain_truthiness_raises_by_default(probability):
    configured_backend({("maybe", "certain proposition"): (True, probability)})
    decision = Semantic("maybe") == "certain proposition"

    assert isinstance(decision, Decision)
    assert decision.probability == probability
    with pytest.raises(UncertainDecisionError):
        bool(decision)


@pytest.mark.parametrize(("policy", "fallback"), [("fallback", False), ("fallback", True)])
def test_uncertainty_can_use_an_explicit_fallback(policy, fallback):
    configured_backend(
        {("maybe", "certain proposition"): (True, 0.5)},
        uncertainty=policy,
        fallback=fallback,
    )

    assert bool(Semantic("maybe") == "certain proposition") is fallback


def test_custom_thresholds_define_truthiness_boundaries():
    configured_backend(
        {
            ("high", "p"): (True, 0.7),
            ("low", "p"): (False, 0.3),
        },
        true_threshold=0.7,
        false_threshold=0.3,
    )

    assert bool(Semantic("high") == "p") is True
    assert bool(Semantic("low") == "p") is False


def test_backend_exception_is_explicit_and_keeps_its_cause():
    failure = TimeoutError("model timed out")

    def fail(_state, _proposition):
        raise failure

    backend = FakeBackend(resolver=fail)
    configure(backend=backend, cache=False)

    with pytest.raises(BackendError) as captured:
        _ = Semantic("state") == "proposition"

    assert captured.value.__cause__ is failure
    assert backend.calls == 1


def test_decision_rejects_invalid_probabilities():
    with pytest.raises(ValueError):
        Decision(
            value=True,
            probability=1.01,
            backend="fake",
            model="test",
            proposition="p",
            state_hash="sha256:abc",
        )
