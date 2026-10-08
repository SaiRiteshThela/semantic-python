# Comparison semantics

The semantic boundary is explicit: `Semantic("state")`. No behavior of ordinary
Python strings changes.

| Expression | v0.1 behavior |
|---|---|
| `"state" == "proposition"` | Python literal equality |
| `Semantic("state") == "proposition"` | One backend boolean decision |
| `Semantic("state") != "proposition"` | Negation of that same decision |
| `semantic is other` | Python identity; never inference |
| `semantic == semantic` | Rejected as ambiguous |
| `semantic == non_string` | Rejected; no inferred contract |
| `hash(semantic)` | Rejected; never inference |

The equality result is a `Decision[bool]`. Its `.value` describes the backend's
classification, while `bool(decision)` applies the configured threshold and
uncertainty policy. Code that needs auditability should keep the decision:

```python
decision = Semantic(message) == "the user wants to stop"
audit(decision.probability, decision.backend, decision.state_hash)
if decision:
    stop()
```

`!=` must not issue an independent, reworded inference. It negates the same
semantic judgment and preserves its provenance. This matters for cost,
repeatability, and logical consistency, especially around phrases such as
"don't stop."

Python's `is` cannot be overloaded. Assignment also does not retain a wrapper:

```python
message = Semantic("stop")
message = "continue"  # now an ordinary str
message = Semantic(message)  # explicitly cross the boundary again
```

Annotation-only wrapping is not runtime behavior. `message: Semantic[str] =
input()` still produces a normal string in ordinary Python and is not a v0.1
feature.

Pattern matching, ordering, ranking, arithmetic, broad non-string support, and
semantic-to-semantic meaning comparison are outside v0.1. An explicit API such
as `same_meaning_as()` may be considered later, but implicit equality will not
guess which question the user intended.
