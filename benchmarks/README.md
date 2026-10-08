# Boolean decision benchmark

The benchmark exercises obvious positive and negative stop-intent examples,
negation, and ambiguous inputs. It reports accuracy, false positives, false
negatives, Brier score, and p50/p95 latency for labeled examples. Ambiguous
examples are reported but excluded from accuracy metrics.

The default run is deterministic, offline, and free:

```console
python benchmarks/run_boolean_benchmark.py --backend fake
```

Real backends are explicit and may download models, transmit text, incur cost,
or take substantial time:

```console
python -m pip install -e '.[laya]'
python benchmarks/run_boolean_benchmark.py --backend laya

python -m pip install -e '.[openai]'
export OPENAI_API_KEY='...'
python benchmarks/run_boolean_benchmark.py --backend openai
```

Record the package, backend, model, hardware, and date with every published
result. Provider probability is not automatically calibrated for a new domain.
