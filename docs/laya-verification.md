# Laya adapter verification

Verification date: October 7, 2026.

Semantic Python supports Laya `>=0.4.0,<0.5` as an experimental local backend.
The adapter contract was checked against the current `0.4.0` upstream package
and source:

- installation: `python -m pip install laya`;
- license: Apache-2.0;
- Python support: 3.10 through 3.13;
- entry point: `from laya import Router`;
- inference: `Router().predict(state, questions, **options)`;
- Boolean question type: `noul`;
- Boolean output: `answers[question]["noul"]`, documented as `P(true)`;
- provenance: routed model information is returned under `routing`;
- network behavior: the first prediction may download a checkpoint from Hugging Face.

Laya 0.4 changes the fallback routing default to its multilingual checkpoint;
identified English still routes to the English checkpoint. The adapter records
the routed model rather than assuming one.

Primary references:

- [Laya on PyPI](https://pypi.org/project/laya/)
- [Laya source repository](https://github.com/NandhaKishorM/laya)

Upstream publishes GPU and CPU latency figures, but they are hardware-specific.
Semantic Python does not present those figures as local measurements. Run the
repository benchmark on the intended deployment hardware before relying on
latency, accuracy, or calibration. Laya decisions are signals, not authorization
for consequential actions.
