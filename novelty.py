"""CMA-ES novelty search for stories. Entry point.
Usage: python novelty.py --config config.yaml --metric euclidean --seed 42"""
import os, sys, argparse, time
from pathlib import Path
import numpy as np
import yaml, cma

import encoders, scorers, coherence, generator


class MAD:
    def __init__(self): self.v = []
    def update(self, x): self.v.append(float(x))
    def norm(self, x):
        if len(self.v) < 2: return float(x)
        m = np.median(self.v); s = np.median(np.abs(np.array(self.v) - m)) + 1e-8
        return (x - m) / s


def pick_start(corpus, method='p90'):
    μ = corpus.mean(0)
    d = np.linalg.norm(corpus - μ, axis=1)
    if method == 'centroid': i = int(d.argmin())
    elif method == 'boundary': i = int(d.argmax())
    else:                                                # 'p90' etc.
        pct = int(method[1:]) if method.startswith('p') else 90
        i = int(np.argmin(np.abs(d - np.percentile(d, pct))))
    return i, corpus[i]


def run(cfg, metric, seed, run_name):
    out = Path(cfg['corpus']['out_dir']) / run_name
    (out / 'texts').mkdir(parents=True, exist_ok=True)
    np.random.seed(seed)

    enc_name = cfg['search']['encoder']
    search_embs = np.load(Path(cfg['corpus']['emb_dir']) / f'{enc_name}_nyer.npz')
    # use first_chunk_embeddings so corpus & 500w candidate are in the same variance regime
    key = 'first_chunk_embeddings' if 'first_chunk_embeddings' in search_embs.files else 'embeddings'
    search_corpus = search_embs[key]
    start_idx, x0 = pick_start(search_corpus, method=cfg['search'].get('start', 'p90'))

    obs = []
    for name in cfg['search']['observers']:
        enc, dim = encoders.load(name, cfg)
        z = np.load(Path(cfg['corpus']['emb_dir']) / f'{name}_nyer.npz')
        oc = z[key if key in z.files else 'embeddings']
        obs.append({'name': name, 'enc': enc, 'dim': dim,
                    'scorer': scorers.make(metric, oc, k=cfg['search']['k'],
                                           rank=cfg['search']['whitening_rank']),
                    'mad': MAD()})

    coh_score, τ = coherence.build(cfg)
    coh_enc, _ = encoders.load(cfg['coherence']['encoder'], cfg)
    gen = generator.build(cfg)

    # generate start sample (retry up to 3 times); seed archive only if we got a real story
    start_path = out / 'texts' / 'start.txt'
    start_txt = ''
    for attempt in range(3):
        try:
            start_txt, _ = gen(x0, start_path, seed=seed + attempt)
            if len(start_txt.split()) >= cfg['coherence']['length_floor_words']:
                break
        except Exception as ex:
            print(f'[start] attempt {attempt} failed: {ex}')
    if not start_txt or len(start_txt.split()) < cfg['coherence']['length_floor_words']:
        print('[start] all attempts failed; proceeding with empty start')
    archive = []
    if start_txt:
        start_emb_coh = coh_enc(start_txt)[0]
        entry = {'x': x0, 'path': str(start_path), 'text': start_txt,
                 'coh': coh_score(start_txt, start_emb_coh)}
        for o in obs:
            e = o['enc'](start_txt)[0]
            entry[f"emb_{o['name']}"] = e
            raw = o['scorer'].score(e); o['mad'].update(raw); o['scorer'].add(e)
        entry['nov'] = 0.0
        archive.append(entry)
    else:
        start_emb_coh = np.zeros(coh_enc(['probe'])[0].shape, 'f4')

    es = cma.CMAEvolutionStrategy(x0.tolist(), cfg['cma']['σ0'], {
        'popsize': cfg['cma']['λ'], 'CMA_diagonal': cfg['cma']['diagonal'],
        'maxiter': cfg['cma']['maxiter'], 'seed': seed,
        'tolfun': 1e-11, 'tolx': 1e-11, 'verbose': -9})

    log = {k: [] for k in ('iter','nov','archive','σ','coh','n_incoh')}
    threshold_p = cfg['search']['threshold_percentile']
    agg = cfg['search']['agg']
    patience, min_accept = cfg['cma']['patience'], cfg['cma']['min_accept']
    accept_hist = []
    σ_explode_limit = 3.0 * cfg['cma']['σ0']

    t0 = time.time()
    σ_hist = []
    for it in range(cfg['cma']['maxiter']):
        sols = es.ask()
        cand = []
        for j, s in enumerate(sols):
            s = np.asarray(s, 'f4')
            p = out / 'texts' / f'i{it:04d}_{j:02d}.txt'
            try:
                txt, _ = gen(s, p, seed=seed + it * 1000 + j)
            except Exception as ex:
                print(f'[i{it} j{j}] gen fail: {ex}'); txt = ''
            short = len(txt.split()) < cfg['coherence']['length_floor_words']
            ec = coh_enc(txt)[0] if not short else np.zeros_like(start_emb_coh)
            c = coh_score(txt, ec) if not short else 0.0
            feasible = (not short) and c >= τ
            embs = ({o['name']: o['enc'](txt)[0] for o in obs} if feasible
                    else {o['name']: np.zeros(o['dim'], 'f4') for o in obs})
            raws = [o['scorer'].score(embs[o['name']]) for o in obs] if feasible else [0.0]*len(obs)
            for o, r in zip(obs, raws):
                if feasible: o['mad'].update(r)
            normed = [o['mad'].norm(r) for o, r in zip(obs, raws)]
            nov = (min(normed) if agg == 'min' else float(np.mean(normed))) if feasible else 0.0
            cand.append({'x': s, 'path': str(p), 'text': txt, 'coh': c, 'feasible': feasible,
                         'nov': nov, **{f"emb_{k}": v for k, v in embs.items()}})

        feasible = [c for c in cand if c['feasible']]
        fmed = float(np.median([c['nov'] for c in feasible])) if feasible else 0.0
        fits = []
        for c in cand:
            if c['feasible']: fits.append(-c['nov'])
            # stronger penalty: 5× coherence gap, anchored above feasible median, plus
            # a small Tikhonov nudge so all-infeasible iters still give CMA-ES a gradient
            else:
                d = float(np.linalg.norm(np.asarray(c['x']) - np.asarray(es.mean)))
                fits.append(-fmed + 5.0 * (τ - c['coh']) ** 2 + 0.01 * d)
        es.tell(sols, fits)

        accepted = 0
        # threshold from existing archive only (exclude start entry and current iter)
        nov_pool = [a['nov'] for a in archive[1:]] if len(archive) > 1 else []
        thr = np.percentile(nov_pool, threshold_p) if len(nov_pool) >= 4 else -np.inf
        for c in feasible:
            if c['nov'] >= thr:
                archive.append(c)
                for o in obs: o['scorer'].add(c[f"emb_{o['name']}"])
                accepted += 1
        accept_hist.append(accepted)

        log['iter'].append(it)
        log['nov'].append(max((c['nov'] for c in feasible), default=0.0))
        log['archive'].append(len(archive))
        log['σ'].append(float(es.sigma))
        log['coh'].append(float(np.mean([c['coh'] for c in cand])))
        log['n_incoh'].append(sum(1 for c in cand if not c['feasible']))
        print(f'[{it:03d}] nov={log["nov"][-1]:.3f} arch={len(archive)} '
              f'σ={es.sigma:.3f} coh={log["coh"][-1]:.3f} incoh={log["n_incoh"][-1]} '
              f'+{accepted}  ({time.time()-t0:.0f}s)')

        _save(out, archive, log, start_idx, metric, agg, [o['name'] for o in obs])
        σ_hist.append(float(es.sigma))
        if len(accept_hist) >= patience and \
           np.mean(accept_hist[-patience:]) < min_accept * cfg['cma']['λ']:
            print(f'early stop (low accept) at iter {it}'); break
        if len(σ_hist) >= 5 and all(s > σ_explode_limit for s in σ_hist[-5:]):
            print(f'early stop (σ explosion: σ>{σ_explode_limit:.2f} for 5 iters) at iter {it}'); break

    print(f'done. archive={len(archive)} in {time.time()-t0:.0f}s')


def _save(out, archive, log, start_idx, metric, agg, names):
    obs_keys = [f"emb_{n}" for n in names]
    np.savez(out / 'archive.npz',
             style_embs=np.stack([a['x'] for a in archive]),
             paths=np.array([a['path'] for a in archive]),
             texts=np.array([a['text'] for a in archive], dtype=object),
             novelties=np.array([a['nov'] for a in archive], 'f4'),
             coherences=np.array([a['coh'] for a in archive], 'f4'),
             start_idx=start_idx, metric=metric, aggregation=agg,
             observer_names=np.array(names),
             **{k: np.stack([a[k] for a in archive]) for k in obs_keys},
             **{f'log_{k}': np.array(v) for k, v in log.items()})


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--metric', default=None)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--name', default=None)
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    m = a.metric or cfg['search']['metric']
    name = a.name or f"{m}_s{a.seed}_{time.strftime('%m%d_%H%M')}"
    run(cfg, m, a.seed, name)
