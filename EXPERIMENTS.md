# Parascope Experiments

Goal: find out whether spectral, context-aware detection plus coherence grouping beats strong simple baselines. Record negative results.

## Hypotheses

| ID | Hypothesis | Falsified if |
|---|---|---|
| A1 | The spectral scorer matches or beats standard detectors on public time-series benchmarks | Worse than Spectral Residual and STL baselines on range-based metrics |
| A2 | Context-conditioned baselines reduce false alarms | Context ablation shows no difference |
| A3 | Coherence grouping cuts alerts per incident without losing recall | Recall drops more than 5% or alert count is not meaningfully lower |
| A4 | Phase lead/lag identifies the originating service better than chance | Top-3 root-cause accuracy not above a random or simple baseline |
| A5 | Logs converted to signals detect anomalies competitively | Much worse than log-sequence methods on LogHub |
| A6 | Unified metrics + logs + traces beats any single source | Combined detection or root-cause accuracy not better than best single source |

## Datasets (public)
- **Time-series anomaly:** Numenta Anomaly Benchmark (NAB), Server Machine Dataset (SMD), SMAP/MSL, benchmarks collected in TSB-UAD
- **Logs:** LogHub (e.g. HDFS, BGL)
- **Microservice faults (metrics, logs, traces):** public fault-injection datasets from microservice benchmark systems such as Online Boutique or Train-Ticket

Check each dataset's license and labeling quality before use; several popular benchmarks have known labeling flaws.

## Baselines
1. Rolling z-score threshold
2. STL decomposition + residual threshold
3. Spectral Residual
4. Isolation Forest on windowed features
5. One deep baseline if time permits (a published reconstruction-based model)
6. For grouping: no grouping (each alert separate), and grouping by service-graph neighbors only
7. For root cause: random ranking, "highest anomaly score first", and "earliest anomaly onset first"

## Metrics
- Detection: **range-based precision/recall/F1** and **VUS-PR**; report point-adjusted F1 only as a secondary number with a warning
- **Time to detect** relative to labeled start
- **False alarms per day**
- **Alerts per incident** (with recall at the same time)
- **Root cause:** Top-1 / Top-3 accuracy
- **Cost:** CPU-seconds and memory per 1,000 signals
- Seeds/splits: fixed train/test splits; for any learned weights use cross-validation

## Experiments

**X1: Single-signal detection.** Compare Parascope (spectral, no context, no grouping) to baselines 1 to 5 on NAB, SMD, SMAP/MSL. Tests A1.

**X2: Context ablation.** With and without hour-of-week and deploy context; also continuous geometry mixing. Tests A2.

**X3: Component ablation.** Drop each score component (power, new peak, shift, loss, flatness) in turn.

**X4: Grouping.** On multi-signal fault datasets, run with and without coherence grouping; report alerts per incident and recall. Tests A3.

**X5: Lead/lag root cause.** On fault-injection data with known origin service; compare to baseline rankings. Tests A4.

**X6: Logs as signals.** Template-count signals on HDFS and BGL; compare to a standard log-sequence anomaly method. Tests A5.

**X7: Unified detection.** Metrics only vs. logs only vs. traces only vs. combined on microservice faults. Tests A6.

**X8: Robustness.** Missing data, clock skew between sources (±5 s), sampling-rate mismatch, concept drift (baseline staleness).

**X9: Cost.** Throughput per CPU core, scaling with number of signals; effect of pruning in coherence grouping.

## Success criteria for v0.1

| Level | Criterion |
|---|---|
| Minimum | X1 within 5% of the best simple baseline (Spectral Residual or STL) on range-based F1 |
| Good | X1 beats all simple baselines on at least two datasets; X4 ≥ 20% fewer alerts per incident at equal recall |
| Great | X5 Top-3 accuracy clearly above the "earliest onset" baseline and X7 shows combined > best single source |

## Stop / pivot conditions
- If X1 loses to Spectral Residual everywhere, drop the standalone detector claim and keep only coherence grouping as a layer on top of any detector.
- If X4 shows no alert reduction, the product is just another detector; pivot to the logs-as-signals angle (X6) if it is competitive.
- If coherence stays high between unrelated signals even after removing baseline cycles, the grouping method needs a different dependence measure (e.g. Granger-style tests).

## Report template

```
Run ID:
Dataset / split:
Config (window, hop, context, weights):
Baselines compared:
Range-F1 / VUS-PR:
Time to detect / false alarms per day:
Alerts per incident / recall:
Root cause Top-1 / Top-3:
CPU and memory:
Notes:
```
