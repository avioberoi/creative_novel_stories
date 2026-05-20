"""Build UMAP + per-metric archive projections for the umap_explorer.html page.

Caches:
  /home/aoberoi1/novelty_stories/report/data/corpus_umap.npy
  /home/aoberoi1/novelty_stories/report/data/corpus_titles.json
  /home/aoberoi1/novelty_stories/report/data/archive_<metric>.json
"""
import json, os
import numpy as np

CORPUS_EMB = '/project/jevans/avi/novelty_stories/embs/qwen3_emb_nyer.npz'
CORPUS_TEXTS = '/project/jevans/avi/novelty_stories/nyer_texts.jsonl'
RUNS = '/project/jevans/avi/novelty_stories/runs'
OUT = '/home/aoberoi1/novelty_stories/report/data'
METRICS = ['euclidean', 'cosine', 'mahalanobis', 'lof', 'diffusion']

os.makedirs(OUT, exist_ok=True)

# --- 1) load corpus, compute UMAP (cache) -------------------------------------
d = np.load(CORPUS_EMB, allow_pickle=True)
X = d['first_chunk_embeddings']     # (5001, 1024) — first-chunk for visual locality
ids = d['ids']                      # ('00001', '00002', ...)
print(f'[corpus] embeddings {X.shape} encoder={d["encoder"]}')

umap_path = os.path.join(OUT, 'corpus_umap.npy')
if os.path.exists(umap_path):
    XY = np.load(umap_path)
    print(f'[umap] cached -> {XY.shape}')
else:
    print('[umap] fitting (this will take a minute)...')
    import umap
    reducer = umap.UMAP(n_components=2, n_neighbors=30, min_dist=0.15,
                        metric='cosine', random_state=42, verbose=False)
    XY = reducer.fit_transform(X).astype('f4')
    np.save(umap_path, XY)
    # also save the fitted reducer's training data for downstream transform
    import pickle
    with open(os.path.join(OUT, 'corpus_umap_reducer.pkl'), 'wb') as f:
        pickle.dump(reducer, f)
    print(f'[umap] fit -> {XY.shape}')

# --- 2) corpus titles ---------------------------------------------------------
titles_path = os.path.join(OUT, 'corpus_titles.json')
if not os.path.exists(titles_path):
    # build id -> first-80-chars index from the jsonl
    id_to_title = {}
    with open(CORPUS_TEXTS) as f:
        for line in f:
            r = json.loads(line)
            txt = r['text'].replace('﻿', '').strip()
            # first line, first 80 chars
            first = txt.split('\n', 1)[0]
            id_to_title[r['id']] = first[:80]
    titles = [id_to_title.get(str(i), str(i)) for i in ids]
    with open(titles_path, 'w') as f:
        json.dump(titles, f)
    print(f'[titles] wrote {len(titles)}')
else:
    print('[titles] cached')

# --- 3) per-metric archive: transform style_embs into the same UMAP ----------
# Use the fitted reducer to transform new points. If reducer pkl not cached,
# refit (this only happens on a clean rebuild).
import pickle
reducer_pkl = os.path.join(OUT, 'corpus_umap_reducer.pkl')
if os.path.exists(reducer_pkl):
    with open(reducer_pkl, 'rb') as f:
        reducer = pickle.load(f)
else:
    print('[umap] refitting for transform...')
    import umap
    reducer = umap.UMAP(n_components=2, n_neighbors=30, min_dist=0.15,
                        metric='cosine', random_state=42, verbose=False)
    reducer.fit(X)
    with open(reducer_pkl, 'wb') as f:
        pickle.dump(reducer, f)

for metric in METRICS:
    arch_path = os.path.join(RUNS, f'{metric}_s42', 'archive.npz')
    if not os.path.exists(arch_path):
        print(f'[skip] {metric}: no archive')
        continue
    a = np.load(arch_path, allow_pickle=True)
    # IMPORTANT: search ran in style space (1024d) which equals the corpus encoder.
    # Archive has both style_embs (search-space, 1024d Qwen3) and emb_bge/e5_mistral.
    style = a['style_embs']
    if style.shape[1] != X.shape[1]:
        # fall back to emb_bge if dims mismatch
        style = a['emb_bge']
    xy = reducer.transform(style).astype('f4')
    texts_full = [str(t) for t in a['texts']]
    texts_trunc = [t[:600] for t in texts_full]
    novelty = a['novelties'].astype(float).tolist()
    coherence = a['coherences'].astype(float).tolist()
    out = {
        'metric': metric,
        'xy': xy.tolist(),
        'texts': texts_trunc,
        'novelty': novelty,
        'coherence': coherence,
    }
    p = os.path.join(OUT, f'archive_{metric}.json')
    with open(p, 'w') as f:
        json.dump(out, f)
    print(f'[archive] {metric}: {len(texts_trunc)} entries -> {p}')

print('done')
