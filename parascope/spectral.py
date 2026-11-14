"""Spectral transforms used by Parascope."""
from __future__ import annotations
import numpy as np
from scipy import signal


def log_spectrogram(x, fs=1.0, nperseg=256, noverlap=None):
    x = np.asarray(x, float); noverlap = nperseg // 2 if noverlap is None else noverlap
    f, t, z = signal.stft(x - x.mean(), fs=fs, window='hann', nperseg=min(nperseg, len(x)), noverlap=min(noverlap, max(0, min(nperseg, len(x))-1)), boundary=None)
    return f, t, np.log1p(np.abs(z) ** 2)


def spectral_flatness(P):
    S = np.exp(np.asarray(P)); return np.exp(np.log(S + 1e-12).mean(axis=0)) / (S.mean(axis=0) + 1e-12)


def dominant_bins(P, count=5):
    P = np.asarray(P); mean = P.mean(axis=-1) if P.ndim == 2 else P; return np.argsort(mean)[-count:]


def spectral_residual(x, window=3):
    x = np.asarray(x, float); X = np.fft.fft(x - x.mean()); log_amp = np.log(np.abs(X) + 1e-8); kernel = np.ones(2*window+1)/(2*window+1)
    residual = log_amp - np.convolve(log_amp, kernel, mode='same'); saliency = np.abs(np.fft.ifft(np.exp(residual + 1j*np.angle(X))))
    return saliency
