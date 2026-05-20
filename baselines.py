"""Three baselines: random_llm | greedy_farthest | diverse_beam.
Each produces an archive.npz matching novelty.py's schema (subset)."""
import argparse, time, json, hashlib
from pathlib import Path
import numpy as np
import yaml

import encoders, scorers, coherence, generator


def _setup(cfg, name):
    out = Path(cfg['corpus']['out_dir']) / name
    (out / 'texts').mkdir(parents=True, exist_ok=True)
    enc_name = cfg['search']['encoder']
    corpus = np.load(Path(cfg['corpus']['emb_dir']) / f'{enc_name}_nyer.npz')['embeddings']
    obs = []
    for n in cfg['search']['observers']:
        enc, dim = encoders.load(n, cfg)
        oc = np.load(Path(cfg['corpus']['emb_dir']) / f'{n}_nyer.npz')['embeddings']
        obs.append({'name': n, 'enc': enc, 'dim': dim,
                    'scorer': scorers.make('euclidean', oc, k=cfg['search']['k'])})
    coh_score, τ = coherence.build(cfg)
    gen = generator.build(cfg)
    return out, corpus, obs, gen, coh_score, τ


def _record(text, path, x, obs, coh_score, τ, floor):
    short = len(text.split()) < floor
    c = coh_score(text) if not short else 0.0
    if not (not short and c >= τ):
        return None
    embs = {o['name']: o['enc'](text)[0] for o in obs}
    raws = [o['scorer'].score(embs[o['name']]) for o in obs]
    return {'x': x, 'path': str(path), 'text': text, 'coh': c,
            'nov': float(np.mean(raws)),
            **{f"emb_{k}": v for k, v in embs.items()}}


def random_llm(cfg, N, name):
    out, corpus, obs, gen, coh, τ = _setup(cfg, name)
    σ0 = cfg['cma']['σ0']
    arch = []
    for i in range(N):
        idx = np.random.randint(len(corpus))
        # match the search's per-dim step size for a fair comparison
        x = corpus[idx] + σ0 * np.random.randn(corpus.shape[1]).astype('f4')
        p = out / 'texts' / f'r{i:04d}.txt'
        try: txt, _ = gen(x, p, seed=42 + i)
        except Exception as e: print(f'gen fail {i}: {e}'); continue
        rec = _record(txt, p, x, obs, coh, τ, cfg['coherence']['length_floor_words'])
        if rec:
            arch.append(rec)
            for o in obs: o['scorer'].add(rec[f"emb_{o['name']}"])
        if i % 10 == 0: print(f'[random] {i}/{N} archive={len(arch)}')
    _save(out, arch, name)


def greedy_farthest(cfg, n_steps, batch, name):
    out, corpus, obs, gen, coh, τ = _setup(cfg, name)
    σ0 = cfg['cma']['σ0']
    arch = []
    μ = corpus.mean(0)
    x_cur = corpus[np.argmin(np.linalg.norm(corpus - μ, axis=1))]
    for step in range(n_steps):
        best = None
        for j in range(batch):
            x = x_cur + σ0 * np.random.randn(corpus.shape[1]).astype('f4')
            p = out / 'texts' / f'g{step:04d}_{j:02d}.txt'
            try: txt, _ = gen(x, p, seed=42 + step * 100 + j)
            except Exception: continue
            rec = _record(txt, p, x, obs, coh, τ, cfg['coherence']['length_floor_words'])
            if rec and (best is None or rec['nov'] > best['nov']):
                best = rec
        if best is not None:
            arch.append(best)
            for o in obs: o['scorer'].add(best[f"emb_{o['name']}"])
            x_cur = best['x']
        print(f'[greedy] step {step} archive={len(arch)} cur_nov={(best or {}).get("nov", 0):.3f}')
    _save(out, arch, name)


def diverse_beam(cfg, N, name):
    """High-temp / sampling fallback: vLLM beam search is unstable; we just sample at T=1.2."""
    import copy
    cfg2 = copy.deepcopy(cfg)
    cfg2['gen']['temperature'] = 1.2
    cfg2['gen']['top_p'] = 0.95
    out, corpus, obs, gen2, coh, τ = _setup(cfg2, name)
    arch = []
    μ = corpus.mean(0); μ /= np.linalg.norm(μ) + 1e-9
    for i in range(N):
        p = out / 'texts' / f'd{i:04d}.txt'
        x = μ + 0.05 * np.random.randn(corpus.shape[1]).astype('f4')
        try: txt, _ = gen2(x, p, seed=42 + i)
        except Exception: continue
        rec = _record(txt, p, x, obs, coh, τ, cfg['coherence']['length_floor_words'])
        if rec:
            arch.append(rec)
            for o in obs: o['scorer'].add(rec[f"emb_{o['name']}"])
        if i % 10 == 0: print(f'[divbeam] {i}/{N} archive={len(arch)}')
    _save(out, arch, name)


def _save(out, arch, name):
    if not arch:
        print(f'[{name}] empty archive — nothing to save'); return
    names = [k[len('emb_'):] for k in arch[0] if k.startswith('emb_')]
    np.savez(out / 'archive.npz',
             style_embs=np.stack([a['x'] for a in arch]),
             paths=np.array([a['path'] for a in arch]),
             texts=np.array([a['text'] for a in arch], dtype=object),
             novelties=np.array([a['nov'] for a in arch], 'f4'),
             coherences=np.array([a['coh'] for a in arch], 'f4'),
             observer_names=np.array(names),
             **{f"emb_{n}": np.stack([a[f"emb_{n}"] for a in arch]) for n in names})
    print(f'[{name}] saved archive={len(arch)} -> {out/"archive.npz"}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--mode', required=True, choices=['random', 'greedy', 'divbeam'])
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--batch', type=int, default=16)
    ap.add_argument('--name', default=None)
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    name = a.name or f"baseline_{a.mode}_{time.strftime('%m%d_%H%M')}"
    if a.mode == 'random':       random_llm(cfg, a.n, name)
    elif a.mode == 'greedy':     greedy_farthest(cfg, a.n, a.batch, name)
    elif a.mode == 'divbeam':    diverse_beam(cfg, a.n, name)
