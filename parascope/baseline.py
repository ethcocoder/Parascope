"""Per-signal, per-context spectral baselines."""
from __future__ import annotations
import numpy as np


class BaselineStore:
    def __init__(self, min_count: int = 2, eps: float = 1e-6): self.data, self.min_count, self.eps = {}, min_count, eps

    def fit(self, signal_id: str, spectra: np.ndarray, context='global'):
        P = np.asarray(spectra, float); P = P[:, None] if P.ndim == 1 else P
        self.data[(signal_id, context)] = {'mu': P.mean(axis=1), 'sigma': P.std(axis=1) + self.eps, 'count': P.shape[1]}
        return self.data[(signal_id, context)]

    def get(self, signal_id: str, context='global'):
        return self.data.get((signal_id, context), self.data.get((signal_id, 'global')))

    def update(self, signal_id, spectrum, context='global', alpha=.01, score=0., safe_threshold=.2, incident_open=False):
        if score >= safe_threshold or incident_open: return False
        item = self.get(signal_id, context); p = np.asarray(spectrum, float)
        if item is None: self.fit(signal_id, p[:, None], context); return True
        item['mu'] = (1-alpha)*item['mu'] + alpha*p; item['sigma'] = np.maximum((1-alpha)*item['sigma'] + alpha*np.abs(p-item['mu']), self.eps); item['count'] += 1; return True

    def contexts(self, signal_id): return [c for (s,c) in self.data if s == signal_id]
