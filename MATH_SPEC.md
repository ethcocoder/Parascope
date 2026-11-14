# Parascope Math Specification

## 1. Signals

Signal `s` sampled every Δ seconds: `x_s[k]`, `k = 0..T-1`. Detrend by subtracting the window mean.

## 2. Short-time spectrum

```
X_s[n, f] = Σ_{k} x_s[k] · w[k - nH] · e^{-2πi f (k - nH)/W}
P_s[n, f] = log(1 + |X_s[n, f]|²)
```
- `W`: window length (samples), `H`: hop, `w`: Hann window.
- Frequency resolution `Δf = 1/(WΔ)`; time resolution about `WΔ`. Longer `W` resolves slow cycles but smears short events. Use two scales (short and long) by default.

## 3. Baseline by context

Context bucket `c` (e.g. hour-of-week × deploy flag). Training windows in that bucket give:
```
μ_c[f] = mean_n P_s[n, f]
σ_c[f] = std_n  P_s[n, f] + ε
```
**Continuous geometry version:** mix `M` baselines with weights from the geometry vector `g`:
```
π(g)   = softmax(W_g g)  ∈ R^M
μ(g)[f] = Σ_m π_m(g) · μ_m[f]
σ(g)[f] = Σ_m π_m(g) · σ_m[f]
```
Learned by minimizing the average anomaly score on normal data (or by simple clustering of contexts).

**Drift update:** `μ ← (1-α) μ + α P` only when the window's score is below a safe threshold and no incident is open.

## 4. Anomaly score components

Standardized deviation: `z[n,f] = (P[n,f] - μ[f]) / σ[f]`.

- **Excess power:** `a_pow[n] = mean_f max(0, z[n,f])`
- **New peak:** peaks of `P[n,·]` not within `±δ` bins of any baseline peak, weighted by height above baseline:
  `a_new[n] = max over new peaks of z at that peak`
- **Peak shift:** dominant frequency `f*[n] = argmax_f P[n,f]`; `a_shift[n] = |f*[n] - f*_base| / Δf` capped
- **Periodicity loss:** `a_loss[n] = max_f max(0, -z[n,f])` restricted to baseline peak bins
- **Broadband noise:** spectral flatness `SF = exp(mean_f log S) / mean_f S` where `S = e^P`; `a_flat[n] = max(0, (SF - SF_base)/σ_SF)`

**Combined:**
```
a[n] = σ_sig( w_1 a_pow + w_2 a_new + w_3 a_shift + w_4 a_loss + w_5 a_flat - b )
```
Weights start hand-set and can be fit on a labeled validation set (logistic regression). Alert when `a[n] > τ` for `m` consecutive windows.

## 5. Spectral Residual baseline (for comparison)

Hou and Zhang's Spectral Residual: with `A = |FFT(x)|`, `Φ = arg FFT(x)`, `L = log A`, residual `R = L - avg_filter(L)`, saliency map `S = |IFFT(exp(R + iΦ))|`. Score points by how much `S` exceeds its local mean. Included as a required baseline.

## 6. Coherence between signals

Welch estimates over a window of both signals:
```
S_xx[f], S_yy[f]: power spectra
S_xy[f]: cross-spectrum
C_xy[f] = |S_xy[f]|² / ( S_xx[f] · S_yy[f] )        ∈ [0, 1]
```
- `C_xy[f] ≈ 1`: signals move together in band `f`; `≈ 0`: unrelated.
- **Edge rule:** connect `x` and `y` if `max_{f in B_anom} C_xy[f] > γ` where `B_anom` is the band where both are anomalous (default `γ = 0.7`).
- **Lead/lag from phase:** `lag(f) = arg(S_xy[f]) / (2π f)`. Sign convention depends on the library (SciPy's `csd` uses conj(X)·Y); **verify with a synthetic test** where `y` is `x` delayed by a known amount.
- Caveat: coherence needs enough averaged segments to be reliable; short incidents give noisy estimates (use a significance threshold, e.g. `C > 1 - 0.05^{1/(L-1)}` for `L` segments).

## 7. Incident grouping

Graph `G = (V, E)`: `V` = anomalous signals in the time range, `E` from the edge rule. Incidents = connected components (or Louvain communities if components are too large). Incident score = max or mean of member scores. Order members by lead/lag to suggest the origin.

## 8. Log and trace signalization

- **Logs:** template id `τ` for each line; `x_τ[k] = count of lines with template τ in sample k`. Rare templates (very low counts) are pooled into an "other" series to avoid noise.
- **Traces:** for edge `(a → b)`: call rate, `p95` latency, error fraction per sample.
- All series are standardized (z-score by training window) so scores are comparable.

## 9. Complexity

| Stage | Cost |
|---|---|
| STFT per signal | O(T log W) |
| Scoring | O(N_windows · F) |
| Coherence (flagged `k` signals) | O(k² · W log W) |

## 10. Known risks in the math
- Single spikes are broadband; spectral scores catch them as noise bursts but weakly. Combine with a simple time-domain residual detector.
- Non-stationary signals (trends, level shifts) violate the stationarity assumption; detrend and handle level shifts separately.
- Coherence between two signals driven by a common clock (e.g. both daily-cyclic) is high but meaningless; remove baseline-explained components before computing coherence (use residual signals).
