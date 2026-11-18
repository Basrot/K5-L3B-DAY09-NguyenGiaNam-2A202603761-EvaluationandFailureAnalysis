"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import comb

import numpy as np
from scipy.stats import bootstrap

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge):
        raise ValueError("human and judge must have equal length")
    if any(x not in ("PASS", "FAIL") for x in (*human, *judge)):
        raise ValueError("labels must be PASS or FAIL")
    return {
        "tp": sum(h == POS and j == POS for h, j in zip(human, judge)),
        "fp": sum(h != POS and j == POS for h, j in zip(human, judge)),
        "fn": sum(h == POS and j != POS for h, j in zip(human, judge)),
        "tn": sum(h != POS and j != POS for h, j in zip(human, judge)),
    }


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    c = confusion(human, judge)
    return (c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0,
            c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0)


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    c = confusion(human, judge)
    n = sum(c.values())
    if not n:
        raise ValueError("kappa undefined for empty labels")
    observed = (c["tp"] + c["tn"]) / n
    expected = ((c["tp"] + c["fn"]) * (c["tp"] + c["fp"]) +
                (c["tn"] + c["fp"]) * (c["tn"] + c["fn"])) / n**2
    if abs(1 - expected) < 1e-12:
        raise ValueError("kappa undefined for constant labels")
    return (observed - expected) / (1 - expected)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    if not all(0 <= x <= 1 for x in (observed_rate, sensitivity, specificity)):
        raise ValueError("rates must be in [0, 1]")
    denom = sensitivity + specificity - 1
    if denom <= 0:
        raise ValueError("judge has no positive classification signal")
    return min(1.0, max(0.0, (observed_rate + specificity - 1) / denom))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or len(x) != len(y) or not len(x):
        raise ValueError("paired non-empty item arrays required")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("item values must be finite")
    delta = float(np.mean(x - y))
    if np.array_equal(x, y):
        return 0.0, 0.0, 0.0
    ci = bootstrap((x, y), lambda a, b: np.mean(a - b), paired=True,
                   vectorized=False, n_resamples=n_resamples, method="percentile",
                   confidence_level=confidence, rng=np.random.default_rng(rng)).confidence_interval
    return delta, float(ci.low), float(ci.high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    _validate_pass_args(n, c, k)
    return 1.0 if k > n - c else 1.0 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    _validate_pass_args(n, c, k)
    return 0.0 if k > c else comb(c, k) / comb(n, k)


def _validate_pass_args(n: int, c: int, k: int) -> None:
    if any(type(v) is not int for v in (n, c, k)) or n <= 0 or c < 0 or c > n or k < 1 or k > n:
        raise ValueError("require integers n >= 1, 0 <= c <= n, and 1 <= k <= n")
