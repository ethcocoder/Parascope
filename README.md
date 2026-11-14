# Parascope

> *para* + *scope*: one observability tool that treats logs, metrics and traces as signals and watches their spectrum.

Parascope converts every kind of telemetry into time-series signals, learns what the **normal spectrum** looks like for each one, and flags anomalies as new, shifted or vanished frequencies. It then uses **cross-signal coherence** to group alerts that belong to the same incident, so one outage produces one alert instead of fifty.

## The problem

- Logs, metrics and traces live in separate tools with separate alert rules.
- Static thresholds break with daily and weekly cycles, so teams drown in false alarms (**alert fatigue**).
- One real incident triggers dozens of alerts on different signals, and humans must work out they are related.

## Core idea

1. **One primitive: the signal.** Metrics are already signals. Logs become event-rate series per log template. Traces become latency and call-rate series per service edge.
2. **Spectral fingerprint.** Each signal has a normal spectrum (its rhythms and noise level). Deviations from it are anomalies.
3. **Coherence grouping.** Signals that become anomalous together and share a spectral band are probably one incident. The phase lead/lag between them gives a hint about which signal moved first.

## String theory mapping

| String theory | Parascope |
|---|---|
| One primitive, many vibration modes | One signal type; metrics, logs and traces are just different modes |
| Compact dimensions set allowed vibrations | **Geometry** = context (hour of week, deploy in progress, traffic level) selects which baseline spectrum is "normal" |
| Duality: two views, one system | **Spectrum view** to detect, **time view** to localize when it happened |
| Strings join and split | **Join** related alerts into one incident; **split** an incident back into per-signal contributions |
| Resonance | Coherent anomalies across services show how a fault propagates |

## What is claimed as new

1. A **unified signal layer** for metrics, logs and traces with one detector.
2. **Context-conditioned spectral baselines** (the geometry vector).
3. **Coherence-based incident grouping** with lead/lag hints for root cause.

## Honest status

Prior art is substantial: FFT and **Spectral Residual** anomaly detection, seasonal decomposition (STL), commercial anomaly detectors, log template mining (Drain), and microservice root-cause methods. Spectral methods are weak on isolated one-off spikes and on non-stationary data. Parascope must beat strong simple baselines on public benchmarks to be worth building. See `EXPERIMENTS.md`.

## Documentation map

| File | Purpose |
|---|---|
| `README.md` | This overview |
| `ARCHITECTURE.md` | Pipeline and components |
| `MATH_SPEC.md` | Spectral baselines, scores, coherence, lead/lag |
| `IMPLEMENTATION_PLAN.md` | Build order and Python skeleton |
| `EXPERIMENTS.md` | Datasets, baselines, success criteria |
| `ROADMAP.md` | Phases, risks, future ideas |

## Implemented v0.1 prototype

This repository includes telemetry signalization helpers, STFT log-power spectra, context-aware baseline storage with guarded drift updates, five explainable anomaly components, spectral-residual and rolling-z-score references, coherence and lead/lag analysis, connected-component incident grouping, range-based metrics, report serialization, and tests.

```bash
python -m pip install -e .
python -m pytest -q
```

The implementation is a research baseline. It does not claim benchmark wins until NAB, SMD, SMAP/MSL, and multi-signal fault evaluations are run with fixed splits and range-based metrics.
