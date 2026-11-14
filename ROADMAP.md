# Parascope Roadmap

## Phase 0: Baselines and data (weeks 1 to 2)
- Data loaders, reference detectors, evaluation harness with range-based metrics
- Deliverable: baseline results table

## Phase 1: Spectral detector (weeks 3 to 4)
- STFT scorer, five components, hand-set then fitted weights
- Deliverable: X1, X3 results

## Phase 2: Geometry / context (week 5)
- Hour-of-week and deploy-aware baselines, then continuous mixing
- Deliverable: X2 results

## Phase 3: Coherence grouping (weeks 6 to 7)
- Coherence graph, lead/lag, incident reports
- Deliverable: X4, X5 results (the make-or-break pair)

## Phase 4: Logs and traces (weeks 8 to 10)
- Template mining, trace signals, unified detection
- Deliverable: X6, X7 results

## Phase 5: Release (weeks 11 to 14)
- Python package and CLI, example notebooks, honest benchmark write-up
- Optional: Prometheus and OpenTelemetry readers

## Product directions (after results)
- Alert-grouping layer that sits on top of any existing detector or alert manager
- Spectrum viewer: a "waterfall" view per service
- Incident summaries in plain language (an LLM reads the structured report)
- Fleet-wide resonance map shared with Parasync

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Simple baselines already as good (Spectral Residual, STL) | High | Report honestly; pivot to grouping layer |
| False coherence between unrelated signals | Medium | Use residuals; significance thresholds; alternative dependence measures |
| Benchmark labels are noisy, results misleading | Medium | Multiple datasets, range-based metrics, manual inspection of samples |
| Non-stationary production data breaks baselines | Medium | Context buckets, drift updates, level-shift detector |
| Pairwise coherence too expensive at scale | Medium | Prune with service graph; only flagged signals |
| Crowded commercial space | High | Open-source, focus on explainability and grouping |

## Future ideas
1. **Learned spectral model:** replace hand-built scores with a small model trained on normal spectra (could reuse Paraphase-style frequency mixing).
2. **Predictive alerts:** detect rising resonance (growing peak amplitude) before thresholds trip.
3. **Causal ordering:** combine phase lag with the service dependency graph for better root cause.
4. **Parasync feed:** use Parascope's spectra as Parasync's resonance detector input.
5. **Privacy-friendly mode:** only share spectra, not raw logs, across teams.

## Next idea in this series
Parapack (adaptive-representation compression), then Paraguard and Paravec.
