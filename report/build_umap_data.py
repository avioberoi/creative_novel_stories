"""Build UMAP + per-metric archive projections + trajectory data for umap_explorer.html.

Strategy:
  - Reuse the poster's already-fit UMAP cache (poster/figs/figs_data/umap_bge.npz)
    so the interactive view is pixel-aligned with the static figure.
  - Inline FULL generated-story text for every archive entry (read from disk).
  - Derive a per-iteration CMA-ES-mean proxy: parse iteration index from each
    archive entry's saved path (filenames look like iNNNN_JJ.txt), group archive
    points by iteration, and emit the per-iter UMAP centroid as a polyline.

Outputs (relative to repo root):
  report/data/corpus_umap.npy
  report/data/corpus_titles.json
  report/data/archive_<metric>.json

Override CORPUS_TEXTS / RUNS via env vars if your data lives outside the repo.
"""
import json, os, re
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POSTER_UMAP = REPO_ROOT / 'poster' / 'figs' / 'figs_data' / 'umap_bge.npz'
CORPUS_TEXTS = os.environ.get('CORPUS_TEXTS', str(REPO_ROOT / 'nyer_texts.jsonl'))
RUNS = os.environ.get('NS_RUNS', str(REPO_ROOT / 'runs'))
OUT = str(REPO_ROOT / 'report' / 'data')
METRICS = ['euclidean', 'cosine', 'mahalanobis', 'lof', 'diffusion']

os.makedirs(OUT, exist_ok=True)
ITER_RE = re.compile(r'i(\d+)_\d+\.txt$')


def parse_iter(path):
    # start.txt is the seed (iter 0 baseline); iNNNN_JJ.txt encodes iter NNNN.
    m = ITER_RE.search(str(path))
    if m: return int(m.group(1))
    return 0  # start.txt and any fallback


def read_text(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''


# 1) corpus UMAP from poster cache --------------------------------------------
d = np.load(POSTER_UMAP, allow_pickle=True)
corpus_xy = d['corpus_xy']  # (5001, 2) float32
print(f'[corpus] poster cache xy {corpus_xy.shape}')
np.save(os.path.join(OUT, 'corpus_umap.npy'), corpus_xy)
with open(os.path.join(OUT, 'corpus_xy.json'), 'w') as f:
    json.dump(corpus_xy.tolist(), f)

# 2) corpus titles (first line, ~80 chars) ------------------------------------
titles_path = os.path.join(OUT, 'corpus_titles.json')
ids_in_order = None
if not os.path.exists(titles_path):
    titles = []
    with open(CORPUS_TEXTS) as f:
        for line in f:
            r = json.loads(line)
            txt = r['text'].replace('﻿', '').strip()
            first = txt.split('\n', 1)[0]
            titles.append(first[:80])
    with open(titles_path, 'w') as f:
        json.dump(titles, f)
    print(f'[titles] wrote {len(titles)}')
else:
    print('[titles] cached')

# 3) per-metric archives ------------------------------------------------------
for metric in METRICS:
    arch_path = os.path.join(RUNS, f'{metric}_s42', 'archive.npz')
    if not os.path.exists(arch_path):
        print(f'[skip] {metric}: no archive')
        continue
    a = np.load(arch_path, allow_pickle=True)

    # poster-cached UMAP xy for THIS metric's archive — pixel-matches the figure
    xy_key = f'{metric}_s42__xy'
    if xy_key not in d.files:
        print(f'[skip] {metric}: no xy in poster cache')
        continue
    xy = d[xy_key].astype('f4')  # (N, 2)

    paths = [str(p) for p in a['paths']]
    n = xy.shape[0]
    if len(paths) != n:
        print(f'[warn] {metric}: paths {len(paths)} != xy {n}; truncating to xy length')
        paths = paths[:n]

    # Read full story text from each path
    texts_full = [read_text(p) for p in paths]

    # Parse iteration per entry
    iters = np.array([parse_iter(p) for p in paths], dtype=int)

    # Per-iteration centroid in UMAP space → trajectory polyline
    uniq_iters = sorted(set(iters.tolist()))
    traj = []
    for it in uniq_iters:
        mask = iters == it
        cx, cy = xy[mask].mean(axis=0)
        traj.append({'iter': int(it), 'x': float(cx), 'y': float(cy), 'n': int(mask.sum())})

    # Optional metadata — keep what's safe to inline (no embeddings)
    novelty = a['novelties'].astype(float).tolist() if 'novelties' in a.files else [0.0] * n
    coherence = a['coherences'].astype(float).tolist() if 'coherences' in a.files else [0.0] * n
    novelty = novelty[:n]
    coherence = coherence[:n]

    # short titles for hover labels
    titles = []
    for t in texts_full:
        first = t.split('\n', 1)[0] if t else ''
        titles.append(first[:80] if first else '(no text)')

    out = {
        'metric': metric,
        'xy': xy.tolist(),
        'titles': titles,
        'texts': texts_full,
        'iters': iters.tolist(),
        'novelty': novelty,
        'coherence': coherence,
        'trajectory': traj,
    }
    p = os.path.join(OUT, f'archive_{metric}.json')
    with open(p, 'w') as f:
        json.dump(out, f)
    print(f'[archive] {metric}: {n} entries, {len(uniq_iters)} iters, traj points {len(traj)}')

print('done')
