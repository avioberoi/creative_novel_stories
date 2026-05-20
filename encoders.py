"""Text encoder registry. load(name, cfg) -> (encode_fn, dim).
encode_fn(list[str]) -> np.ndarray (N, D), unit-norm float32."""
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

_cache = {}


def load(name, cfg):
    if name in _cache:
        return _cache[name]
    path = cfg['models'][name]
    if name == 'emb_gemma':
        # SentenceTransformer wrapper handles EmbeddingGemma directly
        out = _load_st(path, prefix="task: search result | query: ", bs=32)
    elif name == 'nv_embed':
        out = _load_nv_embed(path)
    elif name == 'e5_mistral':
        out = _load_st(path, prefix=("Instruct: Represent this short story passage "
                                     "for stylistic and thematic similarity.\nQuery: "),
                       bs=8)
    else:
        out = _load_st(path, prefix="", bs=32)
    _cache[name] = out
    return out


def _load_st(path, prefix, bs):
    m = SentenceTransformer(path, device='cuda',
                            model_kwargs={'torch_dtype': torch.bfloat16})
    def enc(texts):
        if isinstance(texts, str):
            texts = [texts]
        if prefix:
            texts = [prefix + t for t in texts]
        x = m.encode(texts, normalize_embeddings=True, convert_to_numpy=True,
                     batch_size=bs, show_progress_bar=False)
        return x.astype('f4')
    return enc, m.get_sentence_embedding_dimension()


def _load_nv_embed(path):
    from transformers import AutoModel
    m = AutoModel.from_pretrained(path, trust_remote_code=True,
                                  torch_dtype=torch.bfloat16).cuda().eval()
    def enc(texts):
        if isinstance(texts, str):
            texts = [texts]
        with torch.inference_mode():
            x = m.encode(texts, instruction="", max_length=4096)
        x = torch.nn.functional.normalize(x, p=2, dim=1).float().cpu().numpy()
        return x.astype('f4')
    return enc, 4096
