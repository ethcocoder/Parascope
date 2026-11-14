# Parascope Architecture

## 1. Pipeline

```
 metrics ──┐
 logs    ──┼─► Signalizer ─► Spectral Engine ─► Anomaly Scorer ─► Coherence Grouper ─► Incidents
 traces  ──┘        │                ▲                                   │
                    │         Baseline Store (by context)                ▼
                    └── Context Encoder (geometry g) ───────────►  Report / alerts
```

## 2. Components

### 2.1 Signalizer
Converts raw telemetry into evenly sampled series (sample period Δ, default 10 s or 60 s).

| Source | Signal(s) |
|---|---|
| Metrics | Used as-is; resampled and gap-filled |
| Logs | Template mining (e.g. Drain), then count per template per Δ; plus error-level rate |
| Traces | Per service edge: call rate, p50/p95/p99 latency, error rate |

Each signal gets an id: `source/entity/name`.

### 2.2 Spectral Engine
- Rolling **STFT** per signal (window `W`, hop `H`) to produce a power spectrogram.
- Optional **wavelet** transform for short transients (v2).
- Output: log-power `P[f, n]` for window index `n`.

### 2.3 Context Encoder (geometry)
- Builds `g ∈ R^K` from context: hour-of-week encoding, deploy flag, traffic-level bucket, special-event flag.
- v1: discrete context buckets (hour-of-week × deploy flag). v2: continuous `g` that mixes learned baselines.

### 2.4 Baseline Store
- Per signal and context: mean `μ[f]` and spread `σ[f]` of log-power over training windows.
- Updated slowly (exponential moving average) so drift is absorbed, with guards so incidents do not poison the baseline.

### 2.5 Anomaly Scorer
For each signal and window, compute:
- **Excess power score:** how far above baseline across frequencies
- **New-peak score:** a spectral line that did not exist in the baseline
- **Peak-shift score:** movement of the dominant frequency
- **Periodicity-loss score:** a baseline peak that vanished
- **Broadband-noise score:** rise in spectral flatness

Combined into one `a_s[n] ∈ [0, 1]` with the components kept for explanations.

### 2.6 Coherence Grouper
- Only considers signals flagged anomalous in the same time range.
- Computes magnitude-squared **coherence** and **cross-spectrum phase** between pairs.
- Builds a graph (edge = high coherence in an anomalous band); each connected component is an **incident**.
- Phase lag gives a "who moved first" ordering.

### 2.7 Report
Per incident: involved signals, time range, dominant frequency band, lead/lag order, score breakdown, and a spectrum-vs-baseline plot per signal.

## 3. Deployment modes

| Mode | Description |
|---|---|
| **Batch / offline** | Reads exported data (CSV, Parquet); best for evaluation |
| **Prometheus reader** | Pulls metrics via the HTTP API (read-only) |
| **OpenTelemetry** | Consumes metrics, logs, traces via the collector |
| **Streaming service** | Rolling windows, alert webhooks (later) |

## 4. Scale notes
- Thousands of signals: STFT is cheap per signal; pairwise coherence is **not**. Compute it only among flagged signals and prune pairs by service-graph neighbors.
- Keep the baseline store compact: store `μ` and `σ` per frequency bin (about 100 numbers per signal and context).

## 5. Design rules
1. Every alert must carry an explanation (which band, how far from baseline).
2. Do not auto-update baselines during an active incident.
3. Any claim of fewer alerts must come with recall, never alert count alone.
