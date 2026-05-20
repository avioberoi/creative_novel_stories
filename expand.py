"""Top-N snippet expansion: pick Pareto-best by novelty + LitBench score, continue each to ~4K words."""
import argparse, json, os
from pathlib import Path
import numpy as np
import yaml
from openai import OpenAI

import viz


CONT_SYS = ("You are a literary fiction writer. Below is the opening of a short "
            "story. Continue it into a complete ~3500–4500-word New Yorker-style "
            "short story. Maintain voice, register, and tone. End the story with a "
            "clear, resonant final image — not a moral, not a recap.")


def main(args):
    cfg = yaml.safe_load(open(args.config))
    url = os.environ.get('VLLM_URL', cfg['gen']['vllm_url'])
    client = OpenAI(base_url=url, api_key='none', timeout=300.0)
    model = cfg['models'][cfg['gen']['model']]
    top_n = cfg['eval']['human_top_n']
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)

    pool = []
    for d in args.runs:
        a = np.load(Path(d) / 'archive.npz', allow_pickle=True)
        lp = Path(d) / 'litbench.npz'
        q = np.load(lp)['scores'] if lp.exists() else np.zeros(len(a['novelties']), 'f4')
        for i in range(len(a['texts'])):
            pool.append({'run': Path(d).name, 'i': i,
                         'nov': float(a['novelties'][i]), 'q': float(q[i]),
                         'text': str(a['texts'][i])})

    pts = np.array([[p['nov'], p['q']] for p in pool])
    idx = viz._pareto_front(pts)
    front = [pool[i] for i in idx]
    # rank front by (nov + q), z-scored
    nz = (pts[idx, 0] - pts[idx, 0].mean()) / (pts[idx, 0].std() + 1e-9)
    qz = (pts[idx, 1] - pts[idx, 1].mean()) / (pts[idx, 1].std() + 1e-9)
    order = np.argsort(-(nz + qz))[:top_n]
    chosen = [front[k] for k in order]

    meta = []
    for r, p in enumerate(chosen):
        out_path = out_dir / f'expand_{r:02d}.txt'
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": CONT_SYS},
                          {"role": "user", "content": p['text']}],
                temperature=0.85, top_p=0.95, max_tokens=cfg['eval']['expand_max_tokens'],
                seed=42 + r)
            full = resp.choices[0].message.content.strip()
        except Exception as e:
            print(f'fail {r}: {e}'); continue
        out_path.write_text(full)
        meta.append({**p, 'rank': r, 'out': str(out_path), 'n_words': len(full.split())})
        print(f'[{r:02d}] {p["run"]}/{p["i"]} nov={p["nov"]:.2f} q={p["q"]:.2f} -> {out_path.name}')
    (out_dir / 'expand_index.json').write_text(json.dumps(meta, indent=1))
    print(f'wrote {len(meta)} expanded stories to {out_dir}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--runs', nargs='+', required=True)
    ap.add_argument('--out', default='/project/jevans/avi/novelty_stories/expanded')
    main(ap.parse_args())
