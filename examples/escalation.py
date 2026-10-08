"""Handle an ambiguous escalation signal instead of silently coercing it."""

from semantic_python import FakeBackend, Semantic, UncertainDecisionError, configure

PROPOSITION = "the ticket requires urgent escalation"
TICKET = "This seems odd and I would like someone to look when possible"


def main() -> None:
    backend = FakeBackend({(TICKET, PROPOSITION): (True, 0.58)})
    configure(
        backend=backend,
        true_threshold=0.85,
        false_threshold=0.15,
        uncertainty="raise",
    )

    decision = Semantic(TICKET) == PROPOSITION
    print(f"raw={decision.value} probability={decision.probability:.2f} model={decision.model}")

    try:
        if decision:
            print("Escalate")
        else:
            print("Do not escalate")
    except UncertainDecisionError as error:
        # Uncertainty is routed to review. It is not treated as False, and the
        # semantic result is not authorization for a consequential action.
        print(f"Uncertain: send to human review (probability={error.decision.probability:.2f})")


if __name__ == "__main__":
    main()
