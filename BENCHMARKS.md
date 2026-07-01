# Benchmarks

Every number below is produced by a runnable, deterministic, offline script — no LLM, no network,
nothing fabricated. Reproduce it with:

```bash
python benchmarks/run_benchmarks.py
```

The run recorded here was on Python 3.13, macOS (arm64). Results are machine-dependent; re-run
locally for your own figures. All trajectories and data are synthetic and clean-room.

## 1. Evaluation overhead

Time for `evaluate()` per agent trajectory, using the default four-policy set (PII, budget,
least-privilege, injection), with one tool call per step.

| Steps (= tool calls) | Mean | Median | p95 | Throughput |
|---:|---:|---:|---:|---:|
| 10 | 0.015 ms | 0.011 ms | 0.029 ms | ~68,800 / s |
| 100 | 0.092 ms | 0.081 ms | 0.145 ms | ~10,900 / s |
| 1,000 | 0.769 ms | 0.754 ms | 0.930 ms | ~1,300 / s |

**Takeaway.** Evaluation is sub-millisecond for typical agent runs and under ~1 ms even for
1,000-step trajectories, scaling roughly linearly with length. Because the policies are pure
Python with no model calls, Covenant adds no meaningful time to a CI run.

## 2. Detection quality (in-scope)

A labelled synthetic suite of safe and unsafe trajectories, within the policies' designed scope.
`evaluate()` blocks a trajectory when any policy is violated; the ground-truth label is whether
the trajectory *should* be blocked.

| Metric | Value |
|---|---|
| Precision | 1.000 |
| Recall | 1.000 |
| Accuracy | 1.000 |
| Confusion | TP = 9, FP = 0, FN = 0, TN = 6 (15 cases) |

Per-category accuracy: benign 4/4, PII 3/3, least-privilege 2/2, budget 2/2, injection 2/2,
forbidden-action 2/2.

**Takeaway.** On the failure classes the policies are designed to model, detection is exact:
every unsafe trajectory is blocked and every benign one passes, with no false positives or
negatives. This is the expected behaviour for deterministic rule-based checks — the value of the
benchmark is that it proves the harness classifies a diverse suite without bugs, and that the
result is reproducible.

## 3. Known limitations (out of designed scope)

Deterministic policies have precise, documented boundaries. The same script demonstrates these;
they are **scope boundaries, not bugs**:

| Case | Covenant | Why |
|---|---|---|
| Obfuscated PII (`jane [dot] doe [at] ...`) | PASS (miss) | Regex detectors do not catch spelled-out or obfuscated PII. |
| 16-digit order number | BLOCK (false positive) | A long numeric id matches the credit-card pattern. |
| Injection without provenance | PASS (miss) | The injection policy requires provenance: a call not tagged `influenced_by="untrusted"` is not flagged. |

**On the roadmap.** Per-field PII scoping and pluggable detectors (to remove the numeric-id false
positive and catch more PII), provenance auto-tagging in the adapters (so injection detection does
not depend on manual annotation), and optional LLM-assisted scorers where determinism is not
required.

## Method

- `benchmarks/run_benchmarks.py` is self-contained (standard library plus Covenant only).
- **Overhead:** 5 warm-up evaluations, then 300 timed runs at 10 and 100 steps, or 60 runs at
  1,000 steps, measured with `time.perf_counter()`; mean, median, and p95 reported.
- **Detection:** each labelled trajectory is evaluated and its block/pass decision compared with
  its label to form the confusion matrix.
