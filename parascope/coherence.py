"""Coherence-based cross-signal incident grouping."""
from __future__ import annotations
from collections import defaultdict
import numpy as np
from scipy import signal


def coherence_lead_lag(x, y, fs=1.0, nperseg=256):
    nperseg = min(nperseg, len(x), len(y)); f, cxy = signal.coherence(x, y, fs=fs, nperseg=nperseg)
    _, sxy = signal.csd(x, y, fs=fs, nperseg=nperseg); valid = np.arange(1, len(f)); k = valid[np.argmax(cxy[valid])] if len(valid) else 0
    lag = float(np.angle(sxy[k]) / (2*np.pi*f[k])) if f[k] > 0 else 0.0
    return float(f[k]), float(cxy[k]), lag


def connected_components(nodes, edges):
    parent = {n:n for n in nodes}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a,b in edges:
        if a in parent and b in parent:
            ra, rb = find(a), find(b)
            if ra != rb: parent[rb] = ra
    groups = defaultdict(list)
    for n in nodes: groups[find(n)].append(n)
    return list(groups.values())


def group_incidents(signals, anomalous, fs=1.0, threshold=.7, nperseg=256):
    nodes = [s for s in signals if anomalous.get(s, False)]; edges=[]; relations={}
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:
            f,c,lag = coherence_lead_lag(signals[a], signals[b], fs, nperseg); relations[(a,b)]={'frequency':f,'coherence':c,'lag':lag}
            if c >= threshold: edges.append((a,b))
    return [{'signals': group, 'relations': {str(k):v for k,v in relations.items() if k[0] in group and k[1] in group}} for group in connected_components(nodes, edges)]
