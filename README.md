# novelty_stories

CMA-ES novelty search for creative-story generation. Port of the image-domain novelty search
(`/home/aoberoi1/novelty_search`) to text.

- **Corpus**: 5,001 New Yorker stories (`/project/jevans/maxzhuyt/narrative_project/NEWCORPUS_CLEANED`).
- **Search space**: Qwen3-Embedding-0.6B (768d).
- **Generator**: retrieval-conditioned Qwen3-32B via vLLM.
- **Committee**: BGE-large + E5-Mistral-7B. Held-out: NV-Embed-v2.
- **Metrics**: euclidean, cosine, mahalanobis, LOF, diffusion-map.
- **Eval**: LitBench BT reward + Sun et al. 2411.02316 + Gemma-2-27B CoT judge + human top-20.

## Run

```bash
# 1. Encode the corpus with all observers (one-shot, ~35 min on H200)
sbatch slurm/encode.sbatch

# 2. Launch vLLM Qwen3-32B server
sbatch slurm/vllm.sbatch

# 3. Run search for each distance metric
sbatch --array=0-4 slurm/search.sbatch

# 4. Eval pass (transfer + LitBench + Gemma judge + Sun et al.)
sbatch --dependency=afterok:<search_ids> slurm/evals.sbatch
```

## Files

| File | Purpose | LOC budget |
|---|---|---|
| `novelty.py` | CMA-ES loop + MAD + archive | ≤200 |
| `scorers.py` | 5 distance metrics | ≤200 |
| `encoders.py` | text encoder loaders | ≤100 |
| `generator.py` | retrieval-conditioned LLM | ≤120 |
| `coherence.py` | negative-prompt + length gate | ≤60 |
| `encode_corpus.py` | corpus → .npz | ≤80 |
| `eval.py` | transfer + LitBench + judges | ≤180 |
| `baselines.py` | 3 baselines | ≤150 |
| `viz.py` | UMAP, σ, Pareto | ≤150 |
| `expand.py` | snippet → full story | ≤80 |

See `STYLE.md` for the style rules. The image-domain reference is `/home/aoberoi1/novelty_search`.
