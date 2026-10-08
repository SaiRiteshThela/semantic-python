# Uncertainty and safe decisions

Every model decision is uncertain. Its probability is an estimate from a
particular backend and model version; it is not proof that the proposition is
true, and scores from different models may not be calibrated alike.

A useful policy separates confident true, uncertain, and confident false. For
example, true at or above `0.85`, false at or below `0.15`, and uncertain in
between. Those values are illustrative, not universal safety guarantees. Choose
thresholds using representative data and the cost of false positives and false
negatives.

Uncertainty behavior must be explicit. Suitable policies include:

- raise an uncertainty exception and let the caller decide;
- ask the user for confirmation;
- route the item to a human review queue;
- invoke a deliberately configured fallback backend;
- take a documented conservative action, such as doing nothing.

Do not silently coerce an uncertain result or backend error to `False`. That can
be as consequential as a false positive—for example, failing to escalate a
safety report.

For irreversible or high-impact operations, treat semantic inference as a
signal rather than authorization. Require review for deletion, payments,
account access, legal or medical outcomes, and similar actions. Log the decision
metadata needed for audit without logging secrets or raw sensitive state.

Evaluate a real backend with domain data. Report false-positive and
false-negative rates, calibration or Brier score where meaningful, negation and
ambiguity behavior, repeatability, p50/p95 latency, cold start, and cost. Re-run
those checks when the model or prompt/configuration changes.
