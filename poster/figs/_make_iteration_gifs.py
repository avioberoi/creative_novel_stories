"""Three iteration GIFs for the report website.

Outputs (final):
  <REPO_ROOT>/report/figs/sigma_evolution.gif
  <REPO_ROOT>/report/figs/archive_growth.gif
  <REPO_ROOT>/report/figs/acceptance_dropoff.gif

All English labels — NO Greek letters.
Style locked to poster aesthetic: white bg, Okabe-Ito series colors,
UChicago Maroon accents, Bricolage / Work Sans / JetBrains Mono fonts.
"""
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.animation import FuncAnimation, PillowWriter

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
FONT_DIR = Path("<FONT_DIR>")
for ff in [
    "BricolageGrotesque-Bold.ttf",
    "BricolageGrotesque-Regular.ttf",
    "WorkSans-Bold.ttf",
    "WorkSans-Regular.ttf",
    "WorkSans-Italic.ttf",
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Bold.ttf",
]:
    p = FONT_DIR / ff
    if p.exists():
        fm.fontManager.addfont(str(p))

DISPLAY = "Bricolage Grotesque"
BODY    = "Work Sans"
MONO    = "JetBrains Mono"

# Palette
INK       = "#1F2937"
INK_SOFT  = "#6B7280"
GRID      = "#E5E7EB"
WHITE     = "#FFFFFF"
MAROON    = "#800000"

mpl.rcParams.update({
    "font.family": BODY,
    "axes.unicode_minus": False,
    "axes.edgecolor": INK,
    "axes.linewidth": 1.2,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": WHITE,
    "figure.facecolor": WHITE,
    "savefig.facecolor": WHITE,
    "savefig.edgecolor": WHITE,
})

# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------
RUNS_DIR = Path("<PROJECT_ROOT>/novelty_stories/runs")
OUT_DIR  = Path("<REPO_ROOT>/report/figs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# (key, label, color) — same order as the CMA-ES group in the poster.
METRICS = [
    ("mahalanobis", "Mahalanobis",   "#0072B2"),
    ("euclidean",   "Euclidean",     "#D55E00"),
    ("cosine",      "Cosine",        "#009E73"),
    ("lof",         "LOF",           "#CC79A7"),
    ("diffusion",   "Diffusion-map", "#E69F00"),
]

POPSIZE = 16
ACCEPT_THRESHOLD = 0.25


def load_metric(key):
    p = RUNS_DIR / f"{key}_s42" / "archive.npz"
    d = np.load(p, allow_pickle=True)
    return {
        "iter":    np.asarray(d["log_iter"]),
        "sigma":   np.asarray(d["log_σ"]),
        "archive": np.asarray(d["log_archive"]),
        "nov":     np.asarray(d["log_nov"]),
    }


def moving_avg(x, w):
    """Trailing moving average of width w; first (w-1) entries are partial."""
    x = np.asarray(x, dtype=float)
    out = np.empty_like(x)
    for i in range(len(x)):
        lo = max(0, i - w + 1)
        out[i] = np.mean(x[lo:i + 1])
    return out


DATA = {k: load_metric(k) for k, _, _ in METRICS}
MAX_ITER = max(len(DATA[k]["iter"]) for k in DATA)
print(f"max iterations across runs: {MAX_ITER}")
for k, lbl, _ in METRICS:
    print(f"  {lbl:14s} n_iter={len(DATA[k]['iter']):3d}  "
          f"sigma_range=[{DATA[k]['sigma'].min():.3f},{DATA[k]['sigma'].max():.3f}]  "
          f"archive_final={DATA[k]['archive'][-1]}")


# ---------------------------------------------------------------------------
# Shared frame chrome
# ---------------------------------------------------------------------------
def _style_axes(ax, *, ylabel, title, xmax, ymin, ymax, mono_ticks=True):
    ax.set_xlim(-0.5, xmax + 0.5)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("iteration", fontsize=12, fontfamily=BODY, color=INK)
    ax.set_ylabel(ylabel,      fontsize=12, fontfamily=BODY, color=INK)
    ax.set_title(title, fontsize=15, fontfamily=DISPLAY, fontweight="bold",
                 color=INK, loc="left", pad=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=1.0)
    ax.set_axisbelow(True)
    if mono_ticks:
        for tl in ax.get_xticklabels() + ax.get_yticklabels():
            tl.set_fontname(MONO)
            tl.set_fontsize(9)
            tl.set_color(INK_SOFT)


def _legend(ax):
    leg = ax.legend(
        loc="upper left", bbox_to_anchor=(1.01, 1.0),
        frameon=False, fontsize=10, handlelength=2.4,
        labelcolor=INK,
    )
    for txt in leg.get_texts():
        txt.set_fontfamily(BODY)


# ---------------------------------------------------------------------------
# GIF 1 — sigma evolution
# ---------------------------------------------------------------------------
def make_sigma_gif():
    out = OUT_DIR / "sigma_evolution.gif"
    sigma_all = np.concatenate([DATA[k]["sigma"] for k, _, _ in METRICS])
    ymin = max(0.0, float(sigma_all.min()) - 0.02)
    ymax = float(sigma_all.max()) + 0.02
    ymax = max(ymax, 0.30)  # spec says 0..0.3 range
    ymin = min(ymin, 0.10)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    fig.subplots_adjust(left=0.10, right=0.78, top=0.86, bottom=0.13)

    _style_axes(ax,
                ylabel="step size",
                title="Step size trajectory (CMA-ES)",
                xmax=MAX_ITER - 1, ymin=ymin, ymax=ymax)

    # one line + one head marker per metric
    lines = {}
    heads = {}
    for k, lbl, color in METRICS:
        (ln,) = ax.plot([], [], color=color, linewidth=2.0,
                        label=lbl, solid_capstyle="round")
        (hd,) = ax.plot([], [], "o", color=color, markersize=7,
                        markeredgecolor=WHITE, markeredgewidth=1.2)
        lines[k] = ln
        heads[k] = hd

    _legend(ax)

    iter_txt = ax.text(0.99, 1.02, "", transform=ax.transAxes,
                       ha="right", va="bottom", fontfamily=MONO,
                       fontsize=10, color=INK_SOFT)

    def update(t):
        for k, _, _ in METRICS:
            xs = DATA[k]["iter"]
            ys = DATA[k]["sigma"]
            n = len(xs)
            cut = min(t + 1, n)
            lines[k].set_data(xs[:cut], ys[:cut])
            if cut > 0:
                heads[k].set_data([xs[cut - 1]], [ys[cut - 1]])
            else:
                heads[k].set_data([], [])
        iter_txt.set_text(f"iter {t:02d} / {MAX_ITER - 1:02d}")
        return list(lines.values()) + list(heads.values()) + [iter_txt]

    anim = FuncAnimation(fig, update, frames=MAX_ITER, interval=120, blit=False)
    writer = PillowWriter(fps=7)
    anim.save(out, writer=writer)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# GIF 2 — archive growth
# ---------------------------------------------------------------------------
def make_archive_gif():
    out = OUT_DIR / "archive_growth.gif"
    arc_all = np.concatenate([DATA[k]["archive"] for k, _, _ in METRICS])
    ymax = max(90.0, float(arc_all.max()) + 3)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    fig.subplots_adjust(left=0.10, right=0.78, top=0.86, bottom=0.13)

    _style_axes(ax,
                ylabel="archive size",
                title="Archive growth (CMA-ES)",
                xmax=MAX_ITER - 1, ymin=0, ymax=ymax)

    lines = {}
    heads = {}
    for k, lbl, color in METRICS:
        (ln,) = ax.step([], [], where="post", color=color, linewidth=2.0,
                        label=lbl, solid_capstyle="round")
        (hd,) = ax.plot([], [], "o", color=color, markersize=7,
                        markeredgecolor=WHITE, markeredgewidth=1.2)
        lines[k] = ln
        heads[k] = hd

    _legend(ax)

    iter_txt = ax.text(0.99, 1.02, "", transform=ax.transAxes,
                       ha="right", va="bottom", fontfamily=MONO,
                       fontsize=10, color=INK_SOFT)

    def update(t):
        for k, _, _ in METRICS:
            xs = DATA[k]["iter"]
            ys = DATA[k]["archive"]
            n = len(xs)
            cut = min(t + 1, n)
            lines[k].set_data(xs[:cut], ys[:cut])
            if cut > 0:
                heads[k].set_data([xs[cut - 1]], [ys[cut - 1]])
            else:
                heads[k].set_data([], [])
        iter_txt.set_text(f"iter {t:02d} / {MAX_ITER - 1:02d}")
        return list(lines.values()) + list(heads.values()) + [iter_txt]

    anim = FuncAnimation(fig, update, frames=MAX_ITER, interval=120, blit=False)
    writer = PillowWriter(fps=7)
    anim.save(out, writer=writer)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# GIF 3 — acceptance dropoff
# ---------------------------------------------------------------------------
def make_acceptance_gif():
    """Acceptance rate per iteration = diff(archive)/popsize, 5-iter trailing avg.

    We treat iteration 0 as the seed (no acceptance yet); the first
    delta is between log_archive[0] and log_archive[1], plotted at x=1.
    """
    out = OUT_DIR / "acceptance_dropoff.gif"

    # Precompute per-metric smoothed acceptance over their own iteration grid.
    accept_xy = {}
    early_stop_x = None  # diffusion crosses below threshold
    for k, lbl, color in METRICS:
        arc = DATA[k]["archive"].astype(float)
        delta = np.diff(arc)
        rate = delta / POPSIZE
        smooth = moving_avg(rate, w=5)
        xs = DATA[k]["iter"][1:]  # delta indexed at the post-iter
        accept_xy[k] = (xs, smooth)
        if k == "diffusion":
            below = np.where(smooth < ACCEPT_THRESHOLD)[0]
            if len(below) > 0:
                early_stop_x = int(xs[below[0]])

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    fig.subplots_adjust(left=0.10, right=0.78, top=0.86, bottom=0.13)

    _style_axes(ax,
                ylabel="acceptance rate (5-iter avg)",
                title="Acceptance rate with early-stop threshold",
                xmax=MAX_ITER - 1, ymin=0.0, ymax=1.05)

    # Threshold line
    ax.axhline(ACCEPT_THRESHOLD, linestyle=(0, (4, 3)),
               color=MAROON, linewidth=1.3, alpha=0.85)
    ax.text(MAX_ITER - 1, ACCEPT_THRESHOLD + 0.02,
            f"early-stop threshold ({ACCEPT_THRESHOLD:.2f})",
            ha="right", va="bottom", color=MAROON,
            fontfamily=BODY, fontsize=9, fontstyle="italic")

    lines = {}
    heads = {}
    for k, lbl, color in METRICS:
        (ln,) = ax.plot([], [], color=color, linewidth=2.0,
                        label=lbl, solid_capstyle="round")
        (hd,) = ax.plot([], [], "o", color=color, markersize=7,
                        markeredgecolor=WHITE, markeredgewidth=1.2)
        lines[k] = ln
        heads[k] = hd

    _legend(ax)

    iter_txt = ax.text(0.99, 1.02, "", transform=ax.transAxes,
                       ha="right", va="bottom", fontfamily=MONO,
                       fontsize=10, color=INK_SOFT)

    # Pre-build the early-stop annotation (added once triggered).
    annot = None
    if early_stop_x is not None:
        diff_xs, diff_ys = accept_xy["diffusion"]
        idx_at = int(np.where(diff_xs == early_stop_x)[0][0])
        y_at = float(diff_ys[idx_at])
        annot = ax.annotate(
            "early stop",
            xy=(early_stop_x, y_at),
            xytext=(early_stop_x + 1.0, y_at + 0.22),
            fontsize=10, fontfamily=BODY, color=MAROON,
            arrowprops=dict(arrowstyle="->", color=MAROON, lw=1.0,
                            connectionstyle="arc3,rad=-0.15"),
        )
        annot.set_visible(False)

    def update(t):
        triggered = False
        for k, _, _ in METRICS:
            xs, ys = accept_xy[k]
            # show points whose x <= t
            mask = xs <= t
            lines[k].set_data(xs[mask], ys[mask])
            if mask.any():
                last_i = int(np.where(mask)[0][-1])
                heads[k].set_data([xs[last_i]], [ys[last_i]])
            else:
                heads[k].set_data([], [])
        if annot is not None and t >= early_stop_x:
            annot.set_visible(True)
        iter_txt.set_text(f"iter {t:02d} / {MAX_ITER - 1:02d}")
        artists = list(lines.values()) + list(heads.values()) + [iter_txt]
        if annot is not None:
            artists.append(annot)
        return artists

    anim = FuncAnimation(fig, update, frames=MAX_ITER, interval=120, blit=False)
    writer = PillowWriter(fps=7)
    anim.save(out, writer=writer)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Verification — save first frame as PNG sidecar
# ---------------------------------------------------------------------------
def save_first_frame_check(gif_path):
    """Extract frame 0 from the GIF as PNG so we can eyeball alignment."""
    from PIL import Image, ImageSequence
    im = Image.open(gif_path)
    frame0 = next(ImageSequence.Iterator(im)).convert("RGB")
    sidecar = gif_path.with_suffix(".frame0.png")
    frame0.save(sidecar)
    return sidecar


if __name__ == "__main__":
    print("=" * 60)
    print("Generating sigma_evolution.gif ...")
    p1 = make_sigma_gif()
    print(f"  -> {p1}  ({p1.stat().st_size / 1024:.1f} KB)")

    print("Generating archive_growth.gif ...")
    p2 = make_archive_gif()
    print(f"  -> {p2}  ({p2.stat().st_size / 1024:.1f} KB)")

    print("Generating acceptance_dropoff.gif ...")
    p3 = make_acceptance_gif()
    print(f"  -> {p3}  ({p3.stat().st_size / 1024:.1f} KB)")

    print("=" * 60)
    print("Saving first-frame PNG sidecars for verification ...")
    for p in [p1, p2, p3]:
        s = save_first_frame_check(p)
        print(f"  {s}")
    print("done.")
