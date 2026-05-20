"""Eval dispatcher: transfer (held-out encoder Spearman) + LitBench BT + Sun et al. metrics + Gemma CoT judge."""
import argparse, json, re
from pathlib import Path
import numpy as np
import yaml
from scipy.stats import spearmanr

import encoders


def load_archive(run_dir):
    return dict(np.load(Path(run_dir) / 'archive.npz', allow_pickle=True))


def transfer(cfg, run_dir, held_out='nv_embed'):
    """Re-encode archive texts with held-out encoder; LOO-kNN; Spearman to original novelties.
    Use sklearn pairwise_distances to avoid the O(N²·D) intermediate."""
    from sklearn.metrics import pairwise_distances
    a = load_archive(run_dir)
    enc, _ = encoders.load(held_out, cfg)
    texts = list(a['texts'])
    z = enc(texts)
    N = len(z)
    k = min(cfg['search']['k'], N - 1)
    d = pairwise_distances(z, metric='euclidean').astype('f4')
    np.fill_diagonal(d, np.inf)
    knn = np.sort(d, axis=1)[:, :k]
    nov_t = knn.mean(axis=1)
    rho, p = spearmanr(a['novelties'], nov_t)
    out = Path(run_dir) / 'transfer.npz'
    np.savez(out, nov_transfer=nov_t, nov_original=a['novelties'],
             spearman_rho=float(rho), spearman_p=float(p),
             held_out=held_out)
    print(f'{run_dir}  ρ={rho:.3f}  p={p:.3g}  N={N}')
    return float(rho)


def sun_metrics(cfg, run_dir):
    """Distinct-1/2 + self-BLEU-ish (mean pairwise distinct-bigram overlap)."""
    a = load_archive(run_dir)
    texts = [t.lower() for t in a['texts']]
    tokens = [re.findall(r"\b\w+\b", t) for t in texts]
    def distinct_n(toks, n):
        all_ng, uniq_ng = 0, set()
        for ws in toks:
            ngs = list(zip(*[ws[i:] for i in range(n)]))
            all_ng += len(ngs); uniq_ng |= set(ngs)
        return len(uniq_ng) / max(all_ng, 1)
    d1 = distinct_n(tokens, 1); d2 = distinct_n(tokens, 2)
    # pairwise inverse-homogenization on bigram sets
    bgs = [set(zip(ws, ws[1:])) for ws in tokens]
    if len(bgs) >= 2:
        sims = []
        rng = np.random.default_rng(0)
        idx = rng.choice(len(bgs), size=min(100, len(bgs)), replace=False)
        for i in idx:
            for j in idx:
                if i >= j: continue
                u, v = bgs[i], bgs[j]
                sims.append(len(u & v) / max(len(u | v), 1))
        sim = float(np.mean(sims)) if sims else 0.0
    else:
        sim = 0.0
    out = Path(run_dir) / 'sun_metrics.json'
    out.write_text(json.dumps({'distinct_1': d1, 'distinct_2': d2,
                               'pairwise_bigram_jaccard': sim,
                               'diversity_1_minus_sim': 1 - sim}))
    print(f'{run_dir}  distinct_1={d1:.3f} distinct_2={d2:.3f} div={1-sim:.3f}')


JUDGE_SYS = ("You are an expert literary critic. Rate the following ~500-word "
             "story opening on four dimensions on a 1–5 scale: "
             "coherence, imagery, voice, surprise. Think briefly inside <thinking> "
             "tags, then output a single JSON line with integer scores: "
             "{\"coherence\":..,\"imagery\":..,\"voice\":..,\"surprise\":..}.")


def gemma_judge(cfg, run_dir, n_top=100, n_rand=100):
    """Local vLLM Gemma 27B as CoT judge. Requires JUDGE_URL env var pointing at a Gemma vLLM server.
    Strict JSON: skip items where any of the 4 scores can't be parsed."""
    import os
    from openai import OpenAI
    a = load_archive(run_dir)
    N = len(a['texts'])
    top_idx = np.argsort(-a['novelties'])[:min(n_top, N)]
    rest = np.setdiff1d(np.arange(N), top_idx)
    rng = np.random.default_rng(0)
    rand_idx = rng.choice(rest, size=min(n_rand, len(rest)), replace=False) if len(rest) else np.array([], int)
    pick = np.concatenate([top_idx, rand_idx])
    url = os.environ.get('JUDGE_URL')
    if not url:
        print('JUDGE_URL not set; skipping Gemma judge'); return
    client = OpenAI(base_url=url, api_key='none', timeout=120.0)
    KEYS = ('coherence', 'imagery', 'voice', 'surprise')
    pat = re.compile(r'\{[^{}]*"coherence"[^{}]*\}', re.DOTALL)
    scores = []
    for i in pick:
        try:
            r = client.chat.completions.create(
                model=cfg['models']['gemma2_27b'],
                messages=[{"role": "system", "content": JUDGE_SYS},
                          {"role": "user", "content": str(a['texts'][i])}],
                temperature=0.1, max_tokens=400, seed=42)
            txt = (r.choices[0].message.content or '') if r.choices else ''
            tail = txt.split('</thinking>')[-1]
            m = pat.search(tail) or pat.search(txt)
            if not m: raise ValueError('no JSON')
            d = json.loads(m.group(0))
            vals = [int(d[k]) for k in KEYS]                              # KeyError if missing
            scores.append({'idx': int(i), **{k: v for k, v in zip(KEYS, vals)},
                           'mean': float(np.mean(vals))})
        except Exception as e:
            print(f'judge fail i={i}: {e}'); scores.append({'idx': int(i), 'mean': None})
    out = Path(run_dir) / 'gemma_judge.json'
    out.write_text(json.dumps(scores, indent=1))
    means = [s['mean'] for s in scores if s.get('mean') is not None]
    print(f'{run_dir}  judge_mean={np.mean(means):.2f}  n={len(means)}')


def litbench(cfg, run_dir, batch=4):
    """LitBench Bradley-Terry reward (ConicCat/Litbench-Creative-Writing-RM-3B).
    Input format expected by the RM: 'User:\\n[WP] {prompt}\\n\\nAssistant:\\n{story}'."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    a = load_archive(run_dir)
    repo = cfg['eval']['litbench_repo']
    tok_repo = cfg['eval'].get('litbench_tokenizer', repo)        # ConicCat ships no tokenizer
    wp = cfg['eval'].get('litbench_wp', 'Write a literary short story.')
    tok = AutoTokenizer.from_pretrained(tok_repo)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    m = AutoModelForSequenceClassification.from_pretrained(
        repo, torch_dtype=torch.bfloat16).cuda().eval()
    texts = [f'User:\n[WP] {wp}\n\nAssistant:\n{str(t)}' for t in a['texts']]
    scores = []
    for i in range(0, len(texts), batch):
        b = texts[i:i + batch]
        inp = tok(b, return_tensors='pt', padding=True, truncation=True,
                  max_length=2048).to('cuda')
        with torch.inference_mode():
            s = m(**inp).logits[:, 0].float().cpu().numpy()
        scores.extend(s.tolist())
    out = Path(run_dir) / 'litbench.npz'
    np.savez(out, scores=np.array(scores, 'f4'))
    print(f'{run_dir}  litbench mean={np.mean(scores):.3f}  p90={np.percentile(scores, 90):.3f}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--run_dir', required=True)
    ap.add_argument('--task', required=True,
                    choices=['transfer', 'sun', 'gemma', 'litbench', 'all'])
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    if a.task in ('transfer', 'all'):  transfer(cfg, a.run_dir, cfg['search']['held_out'])
    if a.task in ('sun', 'all'):       sun_metrics(cfg, a.run_dir)
    if a.task in ('litbench', 'all'):  litbench(cfg, a.run_dir)
    if a.task in ('gemma', 'all'):     gemma_judge(cfg, a.run_dir)
