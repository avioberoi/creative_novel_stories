"""Retrieval-conditioned story generator. v ∈ R^768 → kNN(corpus) → vLLM Qwen3-32B → .txt.
Stable seed = base + iter*1000 + j keeps G(v) deterministic in (it, j), not in random md5(v)."""
import os, json
from pathlib import Path
import numpy as np
import faiss
from openai import OpenAI


SYS = ("You are a literary fiction writer. You will be shown several short "
       "story openings that share a stylistic and thematic neighborhood. Your task "
       "is to write a new ~500-word story opening that lives in the SAME "
       "neighborhood — same emotional register, comparable prose style, related "
       "(but not identical) subject matter — while being clearly its OWN piece, "
       "not a pastiche of any single example. Do not mention or refer to the "
       "examples. Just write the story.")


def build(cfg):
    embs = np.load(Path(cfg['corpus']['emb_dir']) / f"{cfg['search']['encoder']}_nyer.npz")
    corpus, ids = embs['embeddings'], embs['ids']
    texts = {}
    with open(cfg['corpus']['texts_jsonl']) as f:
        for line in f:
            r = json.loads(line)
            texts[r['id']] = r['text']
    idx = faiss.IndexFlatIP(corpus.shape[1])
    idx.add(corpus.astype('f4'))
    url = os.environ.get('VLLM_URL', cfg['gen']['vllm_url'])
    client = OpenAI(base_url=url, api_key="none", timeout=120.0)
    model = cfg['models'][cfg['gen']['model']]
    K, T, top_p, mx, mn = (cfg['gen']['K'], cfg['gen']['temperature'],
                           cfg['gen']['top_p'], cfg['gen']['max_tokens'],
                           cfg['gen']['min_tokens'])
    ctx_w = cfg['gen']['ctx_words']

    def gen(v, out_path, seed=42):
        q = v.astype('f4').reshape(1, -1)
        q /= np.linalg.norm(q) + 1e-9
        _, ii = idx.search(q, K)
        retrieved = [ids[i] for i in ii[0]]
        ex = []
        for j, rid in enumerate(retrieved):
            t = texts.get(rid, '')
            t = ' '.join(t.split()[:ctx_w])
            ex.append(f"--- Example {j+1} ---\n{t}")
        user = ("Here are {} story openings from the neighborhood:\n\n{}\n\n"
                "Now write a new ~500-word story opening in this neighborhood. "
                "Begin immediately with the story prose — no title, no preamble, "
                "no commentary.").format(K, "\n\n".join(ex))
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYS},
                      {"role": "user", "content": user}],
            temperature=T, top_p=top_p, max_tokens=mx,
            seed=int(seed) & 0x7FFFFFFF,
            extra_body={"min_tokens": mn, "repetition_penalty": 1.05})
        if not r.choices:
            txt = ''
        else:
            txt = (r.choices[0].message.content or '').strip()
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt)
        p.with_suffix('.meta.json').write_text(json.dumps(
            {"retrieved": retrieved, "seed": int(seed), "n_words": len(txt.split())}))
        return txt, retrieved

    return gen
