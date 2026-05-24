"""Plots: UMAP, σ-trajectory + archive growth, Pareto novelty-vs-quality.
Run after eval.py — reads archive.npz, transfer.npz, litbench.npz.
Every panel also writes its exact plotted arrays to figs_data/<panel>.npz
so the figure is reproducible from the data alone."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import yaml


def _save_panel_data(out_dir, name, **arrays):
    """Persist the exact arrays a panel plots. Loadable via np.load(...)."""
    d = Path(out_dir) / 'figs_data'
    d.mkdir(parents=True, exist_ok=True)
    np.savez(d / f'{name}.npz', **arrays)


def σ_dashboard(run_dirs, out_path):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    data = {}
    for d in run_dirs:
        a = np.load(Path(d) / 'archive.npz', allow_pickle=True)
        label = Path(d).name
        axes[0].plot(a['log_iter'], a['log_σ'], label=label)
        axes[1].plot(a['log_iter'], a['log_archive'], label=label)
        axes[2].plot(a['log_iter'], a['log_nov'], label=label)
        data[f'{label}__iter'] = np.asarray(a['log_iter'])
        data[f'{label}__sigma'] = np.asarray(a['log_σ'])
        data[f'{label}__archive_size'] = np.asarray(a['log_archive'])
        data[f'{label}__max_nov'] = np.asarray(a['log_nov'])
    axes[0].set(xlabel='iter', ylabel='σ', title='step size')
    axes[1].set(xlabel='iter', ylabel='archive size', title='growth')
    axes[2].set(xlabel='iter', ylabel='max novelty (feasible)', title='novelty')
    for ax in axes: ax.legend(fontsize=7); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140); plt.close(fig)
    _save_panel_data(Path(out_path).parent, 'sigma_dashboard', **data)
    print(f'wrote {out_path}')


def umap_archive(cfg, run_dirs, out_path, observer='bge'):
    import umap
    obs = np.load(Path(cfg['corpus']['emb_dir']) / f'{observer}_nyer.npz')['embeddings']
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='cosine', random_state=0)
    u_obs = reducer.fit_transform(obs)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(u_obs[:, 0], u_obs[:, 1], s=3, c='lightgray', label='corpus')
    cmap = plt.get_cmap('tab10')
    data = {'corpus_xy': u_obs.astype('f4')}
    for k, d in enumerate(run_dirs):
        a = np.load(Path(d) / 'archive.npz', allow_pickle=True)
        e = a[f'emb_{observer}']
        u_a = reducer.transform(e).astype('f4')
        ax.scatter(u_a[:, 0], u_a[:, 1], s=14, c=[cmap(k)],
                   label=Path(d).name, alpha=0.85, edgecolors='black', linewidths=0.3)
        data[f'{Path(d).name}__xy'] = u_a
    ax.legend(fontsize=8); ax.set_title(f'UMAP in {observer} space')
    fig.savefig(out_path, dpi=140); plt.close(fig)
    _save_panel_data(Path(out_path).parent, f'umap_{observer}', **data)
    print(f'wrote {out_path}')


def pareto(run_dirs, out_path, quality_key='litbench'):
    fig, ax = plt.subplots(figsize=(7, 5))
    cmap = plt.get_cmap('tab10')
    data = {}
    for k, d in enumerate(run_dirs):
        a = np.load(Path(d) / 'archive.npz', allow_pickle=True)
        nov = np.asarray(a['novelties'])
        qpath = Path(d) / f'{quality_key}.npz'
        if not qpath.exists():
            print(f'skip {d} (no {qpath.name})'); continue
        q = np.asarray(np.load(qpath)['scores'])
        ax.scatter(nov, q, s=12, c=[cmap(k)], label=Path(d).name, alpha=0.7)
        idx = _pareto_front(np.stack([nov, q], 1))
        ax.scatter(nov[idx], q[idx], s=40, facecolors='none',
                   edgecolors=cmap(k), linewidths=1.2)
        name = Path(d).name
        data[f'{name}__nov'] = nov.astype('f4')
        data[f'{name}__quality'] = q.astype('f4')
        data[f'{name}__pareto_idx'] = idx.astype('i4')
    ax.set(xlabel='novelty (committee mean)', ylabel=f'{quality_key} score')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.savefig(out_path, dpi=140); plt.close(fig)
    _save_panel_data(Path(out_path).parent, f'pareto_{quality_key}', **data)
    print(f'wrote {out_path}')


def _pareto_front(pts):
    """Return indices of non-dominated points (maximize both axes)."""
    keep = np.ones(len(pts), bool)
    for i, p in enumerate(pts):
        if not keep[i]: continue
        dominated = (pts >= p).all(1) & (pts > p).any(1)
        keep &= ~dominated
        keep[i] = True
    return np.where(keep)[0]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--runs', nargs='+', required=True)
    ap.add_argument('--out', default='figs')
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    σ_dashboard(a.runs, out / 'sigma_dashboard.png')
    umap_archive(cfg, a.runs, out / 'umap_archive.png')
    pareto(a.runs, out / 'pareto_litbench.png', quality_key='litbench')
