"""Deterministic stop-intent loop; no model, network, or credentials required."""

from semantic_python import FakeBackend, Semantic, configure

PROPOSITION = "the user wants to stop"
MESSAGES = ["keep going", "not yet", "I'm done"]


def main() -> None:
    backend = FakeBackend(
        {
            ("keep going", PROPOSITION): (False, 0.02),
            ("not yet", PROPOSITION): (False, 0.03),
            ("I'm done", PROPOSITION): (True, 0.98),
        }
    )
    configure(backend=backend, threshold=0.85)

    for text in MESSAGES:
        message = Semantic(text)  # reassignment requires explicit re-wrapping
        decision = message == PROPOSITION
        print(
            f"{text!r}: stop={decision.value} "
            f"probability={decision.probability:.2f} backend={decision.backend}"
        )
        if decision:
            print("Stopping after an explicit, inspectable decision.")
            break
        print("Continuing.")


if __name__ == "__main__":
    main()
