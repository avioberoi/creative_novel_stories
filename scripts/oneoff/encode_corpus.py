"""One-shot: encode NEWCORPUS_CLEANED with one encoder. Chunked mean-pool for long docs.
Run once per encoder. Outputs npz with keys: embeddings, ids, first_chunk_embeddings."""
import os, json, argparse, yaml
from pathlib import Path
import numpy as np
from tqdm import tqdm
import encoders


def chunks(text, words_per_chunk=380, overlap=48):
    w = text.split()
    if len(w) <= words_per_chunk:
        return [text]
    out, i = [], 0
    while i < len(w):
        out.append(' '.join(w[i:i + words_per_chunk]))
        i += words_per_chunk - overlap
    return out


def main(args):
    cfg = yaml.safe_load(open(args.config))
    enc, dim = encoders.load(args.encoder, cfg)
    text_dir = Path(cfg['corpus']['text_dir'])
    out_dir = Path(cfg['corpus']['emb_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(text_dir.glob('*.txt'))
    ids = [p.stem for p in paths]
    full, first = np.zeros((len(paths), dim), 'f4'), np.zeros((len(paths), dim), 'f4')
    for i, p in enumerate(tqdm(paths, desc=args.encoder)):
        txt = p.read_text(encoding='utf-8', errors='ignore').strip()
        cs = chunks(txt)
        ce = enc(cs)
        m = ce.mean(0)
        full[i] = m / (np.linalg.norm(m) + 1e-9)
        first[i] = ce[0]
    out_path = out_dir / f'{args.encoder}_nyer.npz'
    np.savez(out_path, embeddings=full, first_chunk_embeddings=first,
             ids=np.array(ids), encoder=args.encoder)
    print(f'wrote {out_path}  shape={full.shape}')

    # also dump first-600-words jsonl for the generator's retrieval prompt
    if args.encoder == cfg['search']['encoder']:
        jl = Path(cfg['corpus']['texts_jsonl'])
        jl.parent.mkdir(parents=True, exist_ok=True)
        with open(jl, 'w') as f:
            for p, i in zip(paths, ids):
                txt = p.read_text(encoding='utf-8', errors='ignore').strip()
                w600 = ' '.join(txt.split()[:600])
                f.write(json.dumps({'id': i, 'text': w600}) + '\n')
        print(f'wrote {jl}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--encoder', required=True,
                    choices=['qwen3_emb', 'bge', 'e5_mistral', 'nv_embed', 'emb_gemma'])
    main(ap.parse_args())
