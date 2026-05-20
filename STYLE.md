# Style

Inspired by https://github.com/sakanaai/asal. No file > 200 lines.

1. Functions over classes. Class only when state legitimately needs to live.
2. No premature abstractions. Five scorers live in one file.
3. No try/except for vibes. Only catch known, named failures.
4. No defensive type hints. Use only when the API contract is non-obvious.
5. Top-of-file docstring: 1-3 lines. Function docstrings: only if the math is non-obvious.
6. Single-letter / Greek math vars (σ, λ, μ) are fine — mirror the paper.
7. Config is YAML, parsed once at the top of `main()`.
8. Logging is `print()` with iter prefix. No frameworks.
9. Flat module layout. No `__init__.py`. Every importable lives at top level.
10. `np.ndarray` over OOP. Don't wrap arrays.
11. Imports: one compact block at top, grouped (stdlib / third-party / local).
12. `if __name__ == "__main__":` only when the file is meant to run as a script.

## Good

```python
# encoders.py: text encoder loaders. Each returns (encode_fn, dim).
import torch, numpy as np
from sentence_transformers import SentenceTransformer

_cache = {}

def load(name):
    if name in _cache: return _cache[name]
    m = SentenceTransformer(PATHS[name], device='cuda',
                            model_kwargs={'torch_dtype': torch.bfloat16})
    def enc(texts):
        if isinstance(texts, str): texts = [texts]
        return m.encode(texts, normalize_embeddings=True).astype('f4')
    _cache[name] = (enc, m.get_sentence_embedding_dimension())
    return _cache[name]
```

## Bad

```python
class TextEncoderRegistry:
    """A registry for text encoder loaders, mapping encoder names
    to factory functions that lazily load the underlying model."""
    _encoders: dict[str, tuple[Callable, int]] = {}

    @classmethod
    def register(cls, name: str, loader: Callable) -> None:
        cls._encoders[name] = loader
    ...
```
