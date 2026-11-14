from __future__ import annotations
import numpy as np
from .spectral import log_spectrogram
from .baseline import BaselineStore
from .score import score_spectrogram

def scan_signal(x, signal_id='signal', fs=1.0, nperseg=256, baseline=None, context='global'):
    f,t,P=log_spectrogram(x,fs,nperseg); store=baseline or BaselineStore()
    item=store.get(signal_id,context)
    if item is None: item=store.fit(signal_id,P,context)
    scores, parts=score_spectrogram(P,item['mu'],item['sigma'])
    return {'frequency':f,'time':t,'power':P,'score':scores,'parts':parts,'baseline':item}
