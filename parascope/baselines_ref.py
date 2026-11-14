"""Simple reference detectors for honest comparisons."""
from __future__ import annotations
import numpy as np
from .spectral import spectral_residual


def rolling_zscore(x, window=30, threshold=3.0):
    x=np.asarray(x,float); score=np.zeros(len(x));
    for i in range(len(x)):
        start=max(0,i-window); mu=x[start:i].mean() if i>start else x[i]; sd=x[start:i].std() if i>start else 1.; score[i]=abs(x[i]-mu)/(sd+1e-6)
    return score, score > threshold


def spectral_residual_detector(x, threshold=3.0):
    s=spectral_residual(x); z=(s-s.mean())/(s.std()+1e-8); return z, z > threshold
