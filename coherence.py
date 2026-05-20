"""Text coherence gate: length floor + negative-prompt cosine."""
import numpy as np
import encoders


def build(cfg):
    enc, _ = encoders.load(cfg['coherence']['encoder'], cfg)
    negs = enc(cfg['coherence']['negatives'])
    z_neg = negs.mean(0)
    z_neg /= np.linalg.norm(z_neg) + 1e-9
    τ = cfg['coherence']['threshold']
    floor = cfg['coherence']['length_floor_words']
    def score(text, text_emb=None):
        if len(text.split()) < floor:
            return 0.0
        if text_emb is None:
            text_emb = enc(text)[0]
        return float(1.0 - text_emb @ z_neg)
    return score, τ
