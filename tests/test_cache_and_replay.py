from __future__ import annotations

import json

import pytest

from semantic_python import (
    DecisionRecorder,
    FakeBackend,
    MemoryDecisionCache,
    ReplayBackend,
    Semantic,
    configure,
)


def test_identical_comparisons_are_cached_with_metadata_preserved():
    backend = FakeBackend({("state", "proposition"): (True, 0.91)})
    cache = MemoryDecisionCache()
    configure(backend=backend, cache=cache)

    first = Semantic("state") == "proposition"
    second = Semantic("state") == "proposition"

    assert backend.calls == 1
    assert first.value == second.value
    assert first.probability == second.probability
    assert first.backend == second.backend
    assert first.model == second.model
    assert first.proposition == second.proposition
    assert first.state_hash == second.state_hash
    assert first.cached is False
    assert second.cached is True


@pytest.mark.parametrize(
    ("left", "right"),
    [
        (("state-a", "p"), ("state-b", "p")),
        (("state", "p-a"), ("state", "p-b")),
    ],
)
def test_changed_state_or_proposition_is_a_cache_miss(left, right):
    responses = {left: (True, 0.95), right: (False, 0.05)}
    backend = FakeBackend(responses)
    configure(backend=backend, cache=MemoryDecisionCache())

    _ = Semantic(left[0]) == left[1]
    _ = Semantic(right[0]) == right[1]

    assert backend.calls == 2


def test_backend_identity_is_part_of_cache_key():
    cache = MemoryDecisionCache()
    first_backend = FakeBackend({("state", "p"): (True, 0.95)}, name="fake", model="v1")
    configure(backend=first_backend, cache=cache)
    _ = Semantic("state") == "p"

    second_backend = FakeBackend({("state", "p"): (False, 0.05)}, name="fake", model="v2")
    configure(backend=second_backend, cache=cache)
    decision = Semantic("state") == "p"

    assert second_backend.calls == 1
    assert decision.model == "v2"
    assert decision.value is False


def test_recording_redacts_plaintext_state_and_secrets(tmp_path):
    record_path = tmp_path / "decisions.jsonl"
    secret = "customer says private support message"
    backend = FakeBackend({(secret, "needs help"): (True, 0.9)})
    recorder = DecisionRecorder(record_path)
    configure(backend=backend, recorder=recorder, cache=False)

    _ = Semantic(secret) == "needs help"

    raw = record_path.read_text(encoding="utf-8")
    assert secret not in raw
    assert "sk-live-do-not-log" not in raw
    record = json.loads(raw)
    assert record["state_hash"]
    assert record["proposition"] == "needs help"
    assert record["backend"] == "fake"
    assert record["model"] == "deterministic-v1"
    assert record["probability"] == 0.9


def test_replay_is_deterministic_and_never_calls_original_backend(tmp_path):
    record_path = tmp_path / "decisions.jsonl"
    state, proposition = "private state", "p"
    recording_backend = FakeBackend({(state, proposition): (True, 0.93)})
    recorder = DecisionRecorder(record_path)
    configure(backend=recording_backend, recorder=recorder, cache=False)
    original = Semantic(state) == proposition

    replay = ReplayBackend(record_path)
    configure(backend=replay, cache=False)
    replayed = Semantic(state) == proposition

    assert replayed.value == original.value
    assert replayed.probability == original.probability
    assert replayed.proposition == original.proposition
    assert replayed.state_hash == original.state_hash
    assert replayed.replayed is True


def test_replay_miss_is_explicit(tmp_path):
    record_path = tmp_path / "empty.jsonl"
    record_path.write_text("", encoding="utf-8")
    configure(backend=ReplayBackend(record_path), cache=False)

    # The semantic boundary normalizes provider failures to the public backend
    # error while retaining the replay miss as its cause.
    from semantic_python import BackendError

    with pytest.raises(BackendError, match="replay"):
        _ = Semantic("unrecorded") == "p"
