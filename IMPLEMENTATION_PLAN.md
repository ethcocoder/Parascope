# Parascope Implementation Plan

Stack: Python 3.10+, NumPy, SciPy (`scipy.signal`), pandas, matplotlib. Optional later: a log template miner (Drain implementation), FastAPI for a service.

## Repo layout

```
parascope/
  parascope/
    __init__.py
    signalize.py      # logs/traces -> series
    spectral.py       # STFT, log-power
    baseline.py       # per-context baselines
    score.py          # anomaly components + combiner
    coherence.py      # coherence, lead/lag, grouping
    report.py         # plots and incident summaries
    baselines_ref.py  # z-score, STL, spectral residual, isolation forest
  eval/
    datasets.py       # loaders for public benchmarks
    metrics.py        # range-based F1, time-to-detect, alert counts
    run_eval.py
  tests/
  examples/
```

## Step 0: Get data and baselines first (days 1 to 3)
1. Download public benchmarks (see `EXPERIMENTS.md`).
2. Implement reference detectors: rolling z-score, STL + residual threshold, Spectral Residual.
3. Record their scores. This is the bar to beat.

## Step 1: Spectral core (days 4 to 6)

```python
import numpy as np
from scipy import signal

def log_spectrogram(x, fs=1.0, nperseg=256, noverlap=128):
    f, t, Z = signal.stft(x - np.mean(x), fs=fs, nperseg=nperseg, noverlap=noverlap)
    return f, t, np.log1p(np.abs(Z) ** 2)          # shape (F, N)

def fit_baseline(P):
    return P.mean(axis=1), P.std(axis=1) + 1e-6      # mu[f], sd[f]

def excess_power_score(P, mu, sd):
    z = (P - mu[:, None]) / sd[:, None]
    return np.clip(z, 0, None).mean(axis=0)          # (N,)

def spectral_flatness(P):
    S = np.exp(P)
    return np.exp(np.log(S + 1e-12).mean(axis=0)) / (S.mean(axis=0) + 1e-12)
```

**Tests:** (a) a pure sine plus noise produces one baseline peak; (b) adding a second sine in test data triggers the new-peak score; (c) removing the sine triggers the periodicity-loss score.

## Step 2: Context baselines (days 7 to 8)
- Hour-of-week buckets (168) and deploy flag.
- Fall back to a global baseline when a bucket has too little data.
- Ablation hook: baseline with vs. without context.

## Step 3: Combined scorer and evaluation (days 9 to 12)
- Implement all five components; start with equal weights.
- Run on NAB and SMD; compute range-based F1 / VUS-PR rather than point-adjusted F1 (point adjustment inflates scores).
- Fit weights by logistic regression on a validation split.

## Step 4: Coherence grouping (days 13 to 16)

```python
def lead_lag(x, y, fs=1.0, nperseg=256):
    f, Cxy = signal.coherence(x, y, fs=fs, nperseg=nperseg)
    _, Sxy = signal.csd(x, y, fs=fs, nperseg=nperseg)
    k = 1 + np.argmax(Cxy[1:])                      # skip DC
    lag = np.angle(Sxy[k]) / (2 * np.pi * f[k])     # verify sign with a synthetic test
    return f[k], Cxy[k], lag
```

**Synthetic test (required):** make `y[k] = x[k - d]` for known `d`; confirm the recovered lag equals `±d` and fix the sign convention once.
- Remove baseline-explained components first (use residuals) to avoid false coherence from shared daily cycles.
- Build the graph and extract incidents.

## Step 5: Logs and traces (days 17 to 21)
- Log template mining on LogHub datasets; per-template count series.
- Trace edge signals from fault-injection microservice datasets.
- Evaluate each source alone, then combined.

## Step 6: Report and CLI (days 22 to 25)
- `parascope scan data.csv --context hourofweek` prints incidents with plots.
- HTML or PNG report per incident.

## Definition of done for v0.1
- [ ] Reference baselines implemented and scored
- [ ] Spectral scorer evaluated on at least NAB and SMD
- [ ] Lead/lag synthetic test passes
- [ ] Coherence grouping evaluated on one multi-signal fault dataset
- [ ] Context ablation table
- [ ] Honest results table in the README

## Pitfalls
- Using point-adjusted F1 (it makes weak detectors look strong).
- Training the baseline on data that contains anomalies.
- Shared daily cycles creating fake coherence.
- Window too long (misses short incidents) or too short (cannot see slow cycles).
- Comparing alert counts without recall.
