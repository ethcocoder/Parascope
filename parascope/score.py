"""Explainable anomaly scoring against a spectral baseline."""
from __future__ import annotations
import numpy as np
from scipy.special import expit
from .spectral import spectral_flatness, dominant_bins


def components(P, mu, sigma, baseline_peaks=None):
    P, mu, sigma = np.asarray(P, float), np.asarray(mu, float), np.maximum(np.asarray(sigma, float), 1e-6)
    z = (P - mu[:, None]) / sigma[:, None]
    power = np.maximum(z, 0).mean(axis=0)
    peaks = dominant_bins(mu[:, None], count=min(5, len(mu))); baseline_peaks = peaks if baseline_peaks is None else np.asarray(baseline_peaks)
    current = np.argmax(P, axis=0); base = int(np.argmax(mu)); shift = np.minimum(np.abs(current - base) / max(1, len(mu) * .25), 1.0)
    loss = np.maximum(-z[baseline_peaks], 0).max(axis=0) if len(baseline_peaks) else np.zeros(P.shape[1])
    flat = spectral_flatness(P); flat_base = float(np.median(spectral_flatness(mu[:, None])))
    flat_score = np.maximum(flat - flat_base, 0)
    new = np.zeros(P.shape[1])
    for i in range(P.shape[1]):
        order = np.argsort(P[:, i])[-5:]; candidates = [b for b in order if np.min(np.abs(b - baseline_peaks)) > 2]
        new[i] = max([z[b, i] for b in candidates], default=0.)
    return {'power': power, 'new_peak': np.maximum(new, 0), 'peak_shift': shift, 'periodicity_loss': loss, 'broadband_noise': flat_score}


def combined_score(parts, weights=None, bias=2.0):
    weights = weights or {'power': .25, 'new_peak': .25, 'peak_shift': .2, 'periodicity_loss': .2, 'broadband_noise': .1}
    raw = sum(weights[k] * np.asarray(v) for k,v in parts.items()) - bias
    return expit(raw)


def score_spectrogram(P, mu, sigma, weights=None, bias=2.0):
    parts = components(P, mu, sigma); return combined_score(parts, weights, bias), parts
