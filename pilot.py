"""Pre-launch calibration. Cheap (CPU-only after corpus load). Diagnoses three risks:
  A. Encoder correlation (committee independence).
  B. Retrieval K-set Jaccard stability under σ-perturbations (CMA-ES smoothness).
  C. Length-regime divergence (chunked-mean vs first-chunk corpus).
Reports JSON to stdout + saves pilot.json. Run before any search."""
import argparse, json
from pathlib import Path
import numpy as np
import faiss, yaml


def load_emb(cfg, encoder, key='first_chunk_embeddings'):
    z = np.load(Path(cfg['corpus']['emb_dir']) / f'{encoder}_nyer.npz')
    return z[key] if key in z.files else z['embeddings']


def encoder_correlations(cfg, names, sample=500, seed=0):
    rng = np.random.default_rng(seed)
    # use the same row indices across encoders so pairwise distances align
    Es = {n: load_emb(cfg, n) for n in names}
    N = min(len(v) for v in Es.values())
    idx = rng.choice(N, size=min(sample, N), replace=False)
    out = {}
    pair_dists = {}
    for n, E in Es.items():
        sub = E[idx]
        D = 1 - sub @ sub.T                                             # cosine distance
        pair_dists[n] = D[np.triu_indices(len(idx), k=1)]
    from scipy.stats import spearmanr
    for a in names:
        for b in names:
            if a >= b: continue
            ρ, _ = spearmanr(pair_dists[a], pair_dists[b])
            out[f'{a}__vs__{b}'] = float(ρ)
    return out


def jaccard_smoothness(cfg, encoder='qwen3_emb', K=5, n_probes=40, sigma_frac=0.25, seed=0):
    """For random anchor points, perturb by σ·sigma_frac and check K-set Jaccard."""
    rng = np.random.default_rng(seed)
    E = load_emb(cfg, encoder)
    σ = cfg['cma']['σ0']
    idx = faiss.IndexFlatIP(E.shape[1])
    idx.add(E.astype('f4'))
    D = E.shape[1]
    jaccs = []
    anchors = rng.choice(len(E), size=n_probes, replace=False)
    for ai in anchors:
        a = E[ai].copy()
        a /= np.linalg.norm(a) + 1e-9
        _, I0 = idx.search(a[None].astype('f4'), K)
        for trial in range(4):
            δ = rng.standard_normal(D).astype('f4') * (σ * sigma_frac)
            b = a + δ; b /= np.linalg.norm(b) + 1e-9
            _, I1 = idx.search(b[None].astype('f4'), K)
            j = len(set(I0[0]) & set(I1[0])) / len(set(I0[0]) | set(I1[0]))
            jaccs.append(j)
    j = np.array(jaccs)
    return {'mean_jaccard': float(j.mean()), 'std': float(j.std()),
            'p10': float(np.percentile(j, 10)), 'p90': float(np.percentile(j, 90)),
            'n': int(len(j)), 'σ': σ, 'sigma_frac': sigma_frac}


def length_regime(cfg, encoder='bge'):
    """Compare chunked-mean vs first-chunk corpus distributions."""
    z = np.load(Path(cfg['corpus']['emb_dir']) / f'{encoder}_nyer.npz')
    if 'first_chunk_embeddings' not in z.files:
        return {'note': 'first_chunk_embeddings missing'}
    A = z['embeddings'];     A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-9)
    B = z['first_chunk_embeddings']                       # already unit-norm from encoder
    rng = np.random.default_rng(0)
    idx = rng.choice(len(A), size=min(1000, len(A)), replace=False)
    Da = A[idx]; Db = B[idx]
    # mean cosine to corpus centroid (in each space)
    μa = Da.mean(0); μa /= np.linalg.norm(μa) + 1e-9
    μb = Db.mean(0); μb /= np.linalg.norm(μb) + 1e-9
    dist_a = 1 - Da @ μa; dist_b = 1 - Db @ μb
    return {'chunked_mean_to_centroid': float(dist_a.mean()),
            'first_chunk_to_centroid': float(dist_b.mean()),
            'ratio_first/mean': float(dist_b.mean() / max(dist_a.mean(), 1e-9))}


def main(args):
    cfg = yaml.safe_load(open(args.config))
    available = []
    for n in ('qwen3_emb', 'bge', 'e5_mistral', 'nv_embed'):
        p = Path(cfg['corpus']['emb_dir']) / f'{n}_nyer.npz'
        if p.exists(): available.append(n)
    print(f'[pilot] encoders available: {available}')
    report = {'encoders_available': available}
    if len(available) >= 2:
        report['encoder_correlations'] = encoder_correlations(cfg, available)
    if 'qwen3_emb' in available:
        report['jaccard_smoothness'] = jaccard_smoothness(cfg, encoder='qwen3_emb')
    if 'bge' in available:
        report['length_regime_bge'] = length_regime(cfg, encoder='bge')
    out = Path(args.out)
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f'[pilot] wrote {out}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--out', default='/project/jevans/avi/novelty_stories/pilot.json')
    main(ap.parse_args())
