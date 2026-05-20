"""Reconstruct baseline_greedy archive.npz from the timed-out run's text files,
then proceed to eval (transfer + litbench + sun)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, '<REPO_ROOT>')

import yaml
import encoders
import scorers

CFG = yaml.safe_load(open('<REPO_ROOT>/config.yaml'))
RUN = Path('<PROJECT_ROOT>/novelty_stories/runs/baseline_greedy')
TEXTS = sorted((RUN / 'texts').glob('*.txt'))
print(f'found {len(TEXTS)} story files')

# load all texts, drop ones below the coherence length floor
floor = CFG['coherence']['length_floor_words']
keep_paths, keep_texts = [], []
for p in TEXTS:
    txt = p.read_text().strip()
    if len(txt.split()) >= floor:
        keep_paths.append(str(p))
        keep_texts.append(txt)
print(f'after length floor ({floor}w): {len(keep_texts)} kept')

# encode with the two observers
emb_bge,    _ = encoders.load('bge', CFG)
emb_e5,     _ = encoders.load('e5_mistral', CFG)

print('encoding bge...')
bge_e  = emb_bge(keep_texts)
print('encoding e5_mistral...')
e5_e   = emb_e5(keep_texts)

# load search-space embedding so we can store it (just bge as a proxy — greedy didn't use a search-space encoder)
style_embs = bge_e.copy()

# compute novelties: mean of MAD-normalized observer kNN distances over the corpus
obs_corpora = {n: np.load(f'<PROJECT_ROOT>/novelty_stories/embs/{n}_nyer.npz')['embeddings']
               for n in ('bge', 'e5_mistral')}
obs_embs = {'bge': bge_e, 'e5_mistral': e5_e}

novs = []
for name in ('bge', 'e5_mistral'):
    sc = scorers.make('euclidean', obs_corpora[name], k=15)
    novs.append(np.array([sc.score(e) for e in obs_embs[name]]))
# MAD normalize
def madn(x):
    m = np.median(x); s = np.median(np.abs(x-m)) + 1e-8
    return (x-m)/s
mad = [madn(n) for n in novs]
novelty = np.mean(np.stack(mad), axis=0)

# coherence — recompute on the texts that survived
import coherence as coh_mod
coh_score, tau = coh_mod.build(CFG)
coh_enc, _ = encoders.load(CFG['coherence']['encoder'], CFG)
coh_arr = []
for t in keep_texts:
    e = coh_enc(t)[0]
    coh_arr.append(coh_score(t, e))
coh_arr = np.array(coh_arr, 'f4')

# save archive in the same schema novelty.py uses
np.savez(RUN / 'archive.npz',
         style_embs=style_embs,
         paths=np.array(keep_paths),
         texts=np.array(keep_texts, dtype=object),
         novelties=novelty.astype('f4'),
         coherences=coh_arr,
         observer_names=np.array(['bge', 'e5_mistral']),
         emb_bge=bge_e, emb_e5_mistral=e5_e,
         metric=np.array('euclidean'), aggregation=np.array('mean'),
         start_idx=np.array(-1),
         log_iter=np.array([]), log_nov=np.array([]),
         log_archive=np.array([]), log_σ=np.array([]),
         log_coh=np.array([]), log_n_incoh=np.array([]))
print(f'wrote {RUN}/archive.npz  N={len(keep_texts)}')
