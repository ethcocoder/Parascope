from __future__ import annotations
import numpy as np


def ranges(mask):
    mask=np.asarray(mask,bool); starts=np.flatnonzero(mask & ~np.r_[False,mask[:-1]]); ends=np.flatnonzero(mask & ~np.r_[mask[1:],False]); return list(zip(starts,ends))


def range_precision_recall_f1(pred, truth):
    p,t=ranges(pred),ranges(truth)
    def overlap(a,b,c,d): return max(0, min(b,d) - max(a,c) + 1)
    precision=sum(max((overlap(a,b,c,d) / max(1, b-a+1) for c,d in t), default=0.) for a,b in p) / max(1,len(p))
    recall=sum(max((overlap(a,b,c,d) / max(1, d-c+1) for a,b in p), default=0.) for c,d in t) / max(1,len(t))
    return precision, recall, 2*precision*recall/max(1e-12,precision+recall)


def time_to_detect(score, truth, threshold=.5):
    starts=[a for a,_ in ranges(truth)]; hits=np.flatnonzero(np.asarray(score)>threshold); return [int(hits[hits>=s][0]-s) if np.any(hits>=s) else None for s in starts]
