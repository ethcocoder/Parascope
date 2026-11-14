from __future__ import annotations
import json

def incident_report(incidents, scores=None):
    return {'incident_count': len(incidents), 'incidents': incidents, 'scores': scores or {}}

def save_report(report, path):
    with open(path,'w') as f: json.dump(report,f,indent=2,default=lambda x:x.tolist() if hasattr(x,'tolist') else str(x))

def plot_spectra(P, mu, out):
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(); ax.imshow(P,aspect='auto',origin='lower'); ax.plot(mu,range(len(mu)),color='white',lw=1); fig.tight_layout(); fig.savefig(out,dpi=150); return out
