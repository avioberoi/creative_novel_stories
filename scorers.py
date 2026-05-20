"""Five novelty scorers, one interface: .add(x), .score(x). x is (D,) float32 unit-norm.
- euclidean, cosine, mahalanobis: kNN mean distance in transformed space (FAISS).
- lof: sklearn LocalOutlierFactor, refit on archive every R iters.
- diffusion: Coifman-Lafon diffusion map + Nyström extension."""
import numpy as np
import faiss
from sklearn.neighbors import LocalOutlierFactor


def make(metric, corpus, k=15, rank=256, refit_every=5):
    if metric == 'lof':       return LOFScorer(corpus, k, refit_every)
    if metric == 'diffusion': return DiffusionScorer(corpus, k)
    return KNNScorer(corpus, metric, k, rank)


class KNNScorer:
    """euclidean | cosine | mahalanobis kNN scorer over an evolving archive."""
    def __init__(self, corpus, metric, k, rank):
        self.metric, self.k = metric, k
        D = corpus.shape[1]
        if metric == 'mahalanobis':
            self.L = _whitening(corpus, rank)
            ref = corpus @ self.L.T
            self.idx = faiss.IndexFlatL2(rank)
        elif metric == 'cosine':
            self.L = None
            ref = _unit(corpus)
            self.idx = faiss.IndexFlatIP(D)
        else:                                              # euclidean
            self.L = None
            ref = corpus.astype('f4')
            self.idx = faiss.IndexFlatL2(D)
        self.idx.add(ref.astype('f4'))

    def _t(self, x):
        if self.L is not None: return (x @ self.L.T).astype('f4')
        if self.metric == 'cosine': return _unit(x[None])[0].astype('f4')
        return x.astype('f4')

    def add(self, x):
        self.idx.add(self._t(x).reshape(1, -1))

    def score(self, x):
        q = self._t(x).reshape(1, -1)
        D, _ = self.idx.search(q, self.k)
        if self.metric == 'cosine': return float((1 - D).mean())  # IP→1-sim
        return float(np.sqrt(np.maximum(D, 0)).mean())            # L2² → L2


def _unit(X):
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    return X / n


def _whitening(corpus, rank):
    """Low-rank Mahalanobis whitening: L s.t. (Lx)ᵀ(Lx) ≈ xᵀΣ⁻¹x.
    Use right singular vectors of X-X̄ (eigvecs of Σ); L = Σ^{-1/2} via Vᵀ."""
    Xc = corpus - corpus.mean(0)
    _, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    r = min(rank, len(S))
    return Vt[:r] / (S[:r, None] / np.sqrt(len(Xc)) + 1e-6)   # (r, D)


class LOFScorer:
    """Local Outlier Factor. Higher = more anomalous = more novel."""
    def __init__(self, corpus, k, refit_every):
        self.k, self.refit_every = k, refit_every
        self.corpus = corpus.astype('f4')
        self.archive = []
        self._refit()
        self._since = 0

    def _refit(self):
        data = self.corpus if not self.archive else np.vstack([self.corpus, np.stack(self.archive)])
        self.lof = LocalOutlierFactor(novelty=True, n_neighbors=self.k).fit(data)

    def add(self, x):
        self.archive.append(x.astype('f4'))
        self._since += 1
        if self._since >= self.refit_every:
            self._refit(); self._since = 0

    def score(self, x):
        return float(-self.lof.score_samples(x.reshape(1, -1).astype('f4'))[0])


class DiffusionScorer:
    """Coifman-Lafon diffusion map. kNN-Gaussian kernel → anisotropic α=1 → symmetric
    eigendecomp via Ps = D^{-1/2} K~ D^{-1/2} → Nyström for queries. k-NN against
    corpus∪archive in diffusion coords to match the other scorers' reference set."""
    def __init__(self, corpus, k, n_eigs=64, knn=50):
        from sklearn.neighbors import NearestNeighbors
        from scipy.sparse import csr_matrix
        from scipy.sparse.linalg import eigsh
        self.k = k
        self.X = corpus.astype('f4')
        nn = NearestNeighbors(n_neighbors=knn).fit(self.X)
        d, ii = nn.kneighbors(self.X)
        ε = np.median(d[:, knn // 2]) ** 2 + 1e-9
        N = len(self.X)
        rows = np.repeat(np.arange(N), knn)
        K = csr_matrix((np.exp(-d.ravel() ** 2 / ε), (rows, ii.ravel())), shape=(N, N))
        K = csr_matrix((K + K.T) / 2)
        q = np.asarray(K.sum(1)).ravel() + 1e-9
        Kt = csr_matrix(K.multiply(1 / q[:, None]).multiply(1 / q[None, :]))   # α=1
        d2 = np.asarray(Kt.sum(1)).ravel() + 1e-9
        Dh = 1.0 / np.sqrt(d2)
        Ps = csr_matrix(Kt.multiply(Dh[:, None]).multiply(Dh[None, :]))         # symmetric
        λ, ψs = eigsh(Ps, k=n_eigs + 1, which='LM')
        order = np.argsort(-λ)[1:n_eigs + 1]                                    # drop trivial
        self.λ = λ[order]
        self.ψ = ψs[:, order] * Dh[:, None]                                     # right eigvecs of P
        self.ε, self._nn = ε, nn
        # initialize "archive" with corpus in diffusion coords for parity with KNNScorer
        self.archive = [self.ψ[i] * self.λ for i in range(N)]

    def _embed(self, x):
        d, ii = self._nn.kneighbors(x.reshape(1, -1).astype('f4'))
        w = np.exp(-d[0] ** 2 / self.ε)
        w /= w.sum() + 1e-9
        return (w @ self.ψ[ii[0]]) * self.λ                                      # Nyström

    def add(self, x):
        self.archive.append(self._embed(x))

    def score(self, x):
        e = self._embed(x)
        A = np.stack(self.archive)
        d = np.linalg.norm(A - e, axis=1)
        d.sort()
        return float(d[:self.k].mean())
