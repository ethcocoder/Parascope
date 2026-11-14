"""Convert common telemetry records into evenly sampled signals."""
from __future__ import annotations
from collections import Counter
import numpy as np


def resample(values, timestamps, step: float, start=None, end=None, fill=0.0):
    timestamps, values = np.asarray(timestamps, float), np.asarray(values, float)
    start = timestamps.min() if start is None else start; end = timestamps.max() if end is None else end
    grid = np.arange(start, end + step * .5, step); out = np.full(grid.shape, fill, float)
    if values.size: out = np.interp(grid, timestamps, values, left=fill, right=fill)
    return grid, out


def count_log_templates(timestamps, template_ids, step: float, start=None, end=None):
    timestamps = np.asarray(timestamps, float); template_ids = np.asarray(template_ids)
    ids = list(dict.fromkeys(template_ids.tolist())); start = timestamps.min() if start is None else start; end = timestamps.max() if end is None else end
    grid = np.arange(start, end + step * .5, step); result = {}
    bins = np.floor((timestamps - start) / step).astype(int)
    for template in ids:
        counts = np.bincount(bins[template_ids == template], minlength=len(grid)).astype(float)
        result[str(template)] = counts[:len(grid)]
    return grid, result


def trace_edge_signals(timestamps, edges, step: float):
    timestamps = np.asarray(timestamps, float); edges = np.asarray(edges)
    start, end = timestamps.min(), timestamps.max(); grid = np.arange(start, end + step * .5, step); bins = np.floor((timestamps-start)/step).astype(int)
    output = {}
    for edge in dict.fromkeys(map(tuple, edges.tolist())):
        mask = np.array([tuple(e) == edge for e in edges]); counts = np.bincount(bins[mask], minlength=len(grid)).astype(float)
        output[f'{edge[0]}->{edge[1]}/call_rate'] = counts[:len(grid)]
    return grid, output


def standardize(x, eps=1e-8):
    x = np.asarray(x, float); return (x - x.mean()) / max(x.std(), eps)
