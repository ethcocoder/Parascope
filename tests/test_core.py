import numpy as np
from parascope import log_spectrogram, score_spectrogram, coherence_lead_lag, group_incidents
from parascope.baseline import BaselineStore
from eval.metrics import range_precision_recall_f1


def test_spectrogram_and_baseline_scores():
    rng=np.random.default_rng(0); x=np.sin(2*np.pi*.05*np.arange(1024))+0.05*rng.normal(size=1024); f,t,P=log_spectrogram(x,nperseg=128)
    store=BaselineStore(); item=store.fit('x',P[:,:-1]); scores,parts=score_spectrogram(P,item['mu'],item['sigma']); assert P.shape[0]==len(f); assert scores.shape[0]==P.shape[1]; assert 'new_peak' in parts


def test_coherence_lag_synthetic():
    n=2048; d=12; x=np.sin(2*np.pi*.03*np.arange(n)); y=np.r_[np.zeros(d),x[:-d]]; f,c,lag=coherence_lead_lag(x,y,nperseg=256); assert c>.8; assert abs(abs(lag)-d)<4


def test_grouping_and_metrics():
    n=1024; x=np.sin(2*np.pi*.04*np.arange(n)); signals={'a':x,'b':x.copy(),'c':np.random.default_rng(1).normal(size=n)}; groups=group_incidents(signals,{'a':True,'b':True,'c':True},threshold=.7,nperseg=128); assert any(set(g['signals'])=={'a','b'} for g in groups)
    assert range_precision_recall_f1([0,1,1,0],[0,1,1,0])[-1] == 1.
