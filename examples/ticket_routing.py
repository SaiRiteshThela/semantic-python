"""Deterministic support routing with retained confidence and provenance."""

from semantic_python import FakeBackend, Semantic, configure

BILLING = "the ticket is about billing"
TECHNICAL = "the ticket is about a technical problem"
TICKET = "I was charged twice for my subscription"


def main() -> None:
    backend = FakeBackend(
        {
            (TICKET, BILLING): (True, 0.97),
            (TICKET, TECHNICAL): (False, 0.06),
        }
    )
    configure(backend=backend, threshold=0.85)

    ticket = Semantic(TICKET)
    billing = ticket == BILLING
    technical = ticket == TECHNICAL

    # A production system should persist only appropriate audit metadata. A
    # state hash reduces plaintext exposure, but is not anonymization.
    print("billing:", billing.value, billing.probability, billing.state_hash[:12])
    print("technical:", technical.value, technical.probability)

    if billing:
        queue = "billing-review"
    elif technical:
        queue = "technical-support"
    else:
        queue = "human-triage"
    print("route:", queue)


if __name__ == "__main__":
    main()
