"""Regenerate the three poster figure PNGs.

NO unicode / Greek letters anywhere in rendered text. Plain English only.
NO matplotlib mathtext ($...$).

Outputs:
  - transfer_rho.png
  - sigma_dashboard.png
  - pareto_litbench.png
And the corresponding npz archives in figs_data/.
"""
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# -----------------------------------------------------------------------------
# Font registration
# -----------------------------------------------------------------------------
FONT_DIR = Path("/home/aoberoi1/.claude/skills/canvas-design/canvas-fonts")
FONT_FILES = [
    "BricolageGrotesque-Bold.ttf",
    "BricolageGrotesque-Regular.ttf",
    "WorkSans-Bold.ttf",
    "WorkSans-Regular.ttf",
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Bold.ttf",
]
for ff in FONT_FILES:
    p = FONT_DIR / ff
    if p.exists():
        fm.fontManager.addfont(str(p))

DISPLAY_FAM = "Bricolage Grotesque"   # display / titles (Space Grotesk fallback)
BODY_FAM    = "Work Sans"             # body (Inter fallback)
MONO_FAM    = "JetBrains Mono"

mpl.rcParams.update({
    "font.family": BODY_FAM,
    "axes.unicode_minus": False,
    "axes.edgecolor": "#1F2937",
    "axes.linewidth": 1.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": "#FFFFFF",
    "figure.facecolor": "#FFFFFF",
    "savefig.facecolor": "#FFFFFF",
    "grid.color": "#E5E7EB",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.5,
    "xtick.color": "#1F2937",
    "ytick.color": "#1F2937",
    "xtick.major.width": 1.2,
    "ytick.major.width": 1.2,
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "mathtext.default": "regular",
})

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
RUNS_BASE = Path("/project/jevans/avi/novelty_stories/runs")
OUT_DIR   = Path("/home/aoberoi1/novelty_stories/poster/figs")
DATA_DIR  = OUT_DIR / "figs_data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Okabe-Ito assignment by transfer-rank order (best -> worst)
COLOR = {
    "mahalanobis": "#0072B2",
    "euclidean":   "#D55E00",
    "cosine":      "#009E73",
    "lof":         "#CC79A7",
    "diffusion":   "#E69F00",
}
LABEL = {
    "mahalanobis": "Mahalanobis",
    "euclidean":   "Euclidean",
    "cosine":      "Cosine",
    "lof":         "LOF",
    "diffusion":   "Diffusion-map",
}
# Order by transfer-rho descending
ORDER = ["mahalanobis", "euclidean", "cosine", "lof", "diffusion"]


def load_archive(run):
    """Load archive.npz; avoid touching the texts field (pickled numpy._core)."""
    p = RUNS_BASE / f"{run}_s42" / "archive.npz"
    z = np.load(p, allow_pickle=False)  # allow_pickle False -> texts won't be read unless asked
    out = {}
    for k in z.files:
        if k == "texts":
            continue
        try:
            out[k] = z[k]
        except Exception:
            pass
    return out


def load_transfer_rho(run):
    p = RUNS_BASE / f"{run}_s42" / "transfer.npz"
    z = np.load(p, allow_pickle=False)
    return float(z["spearman_rho"])


def load_litbench_scores(run):
    p = RUNS_BASE / f"{run}_s42" / "litbench.npz"
    z = np.load(p, allow_pickle=False)
    return np.asarray(z["scores"], dtype="f4")


def load_novelties(run):
    z = load_archive(run)
    return np.asarray(z["novelties"], dtype="f4")


def load_log_iter_sigma_archive_nov(run):
    z = load_archive(run)
    return (
        np.asarray(z["log_iter"], dtype="i4"),
        np.asarray(z["log_σ"], dtype="f4"),   # key name has σ but we only read it, never render
        np.asarray(z["log_archive"], dtype="i4"),
        np.asarray(z["log_nov"], dtype="f4"),
    )


def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#1F2937")
    ax.spines["left"].set_color("#1F2937")
    ax.spines["bottom"].set_linewidth(1.5)
    ax.spines["left"].set_linewidth(1.5)
    ax.yaxis.grid(True, color="#E5E7EB", linewidth=0.6, alpha=0.5)
    ax.set_axisbelow(True)


# -----------------------------------------------------------------------------
# Figure 1: transfer rank correlation bar chart
# -----------------------------------------------------------------------------
def make_transfer_rho():
    rho = {run: load_transfer_rho(run) for run in ORDER}
    # Order: best at top -> worst at bottom
    runs_sorted = sorted(rho, key=lambda r: rho[r], reverse=True)
    values = [rho[r] for r in runs_sorted]
    colors = [COLOR[r] for r in runs_sorted]
    labels = [LABEL[r] for r in runs_sorted]

    fig, ax = plt.subplots(figsize=(12, 7), dpi=200)
    fig.subplots_adjust(left=0.20, right=0.93, top=0.82, bottom=0.18)

    y = np.arange(len(runs_sorted))
    # Highest on top -> reverse y order
    ax.barh(y[::-1], values, color=colors, edgecolor="#1F2937", linewidth=0.8, height=0.62)

    # Value annotations to the right of each bar
    for yi, v in zip(y[::-1], values):
        ax.text(v + 0.012, yi, f"{v:.2f}", va="center", ha="left",
                fontsize=20, fontfamily=MONO_FAM, color="#1F2937")

    # Reference line at 0.629 (image-paper best)
    REF = 0.629
    ax.axvline(REF, color="#6B7280", linestyle="--", linewidth=1.5)
    ax.text(REF + 0.008, len(runs_sorted) - 0.5 + 0.05,
            "image-paper best: 0.63",
            fontsize=16, fontfamily=MONO_FAM, color="#6B7280",
            ha="left", va="bottom")

    # Y-axis: metric names
    ax.set_yticks(y[::-1])
    ax.set_yticklabels(labels, fontsize=20, fontfamily=BODY_FAM, color="#1F2937")
    ax.tick_params(axis="y", length=0)

    # X-axis
    ax.set_xlim(0, 1.0)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.tick_params(axis="x", labelsize=16)
    for lbl in ax.get_xticklabels():
        lbl.set_fontfamily(BODY_FAM)
    ax.set_xlabel(
        "Rank correlation (1.00 = perfect transfer, 0.00 = no relation)",
        fontsize=22, fontfamily=DISPLAY_FAM, fontweight="bold",
        color="#1F2937", labelpad=14,
    )

    # Title + subtitle (placed in figure coords)
    fig.text(0.04, 0.93,
             "How well do novelty rankings transfer to a held-out encoder?",
             fontsize=28, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937")
    fig.text(0.04, 0.875,
             "Mahalanobis-whitened k-NN gives the strongest signal (0.80)",
             fontsize=18, fontfamily=BODY_FAM, color="#6B7280")

    style_axes(ax)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, alpha=0.5)
    ax.yaxis.grid(False)

    out_png = OUT_DIR / "transfer_rho.png"
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

    # Save panel data
    np.savez(
        DATA_DIR / "transfer_rho.npz",
        runs=np.array(runs_sorted),
        labels=np.array(labels),
        rho=np.array(values, dtype="f4"),
        colors=np.array(colors),
        reference_image_paper=np.float32(REF),
    )
    print(f"wrote {out_png}")


# -----------------------------------------------------------------------------
# Figure 2: step-size / archive / novelty dashboard (3 panels)
# -----------------------------------------------------------------------------
def make_sigma_dashboard():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=200)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.78, bottom=0.16, wspace=0.28)

    data = {}
    for run in ORDER:
        iters, sig, arch, nov = load_log_iter_sigma_archive_nov(run)
        c = COLOR[run]
        axes[0].plot(iters, sig, color=c, linewidth=2.2, label=LABEL[run])
        axes[1].plot(iters, arch, color=c, linewidth=2.2, label=LABEL[run])
        axes[2].plot(iters, nov,  color=c, linewidth=2.2, label=LABEL[run])
        data[f"{run}__iter"]     = iters
        data[f"{run}__sigma"]    = sig
        data[f"{run}__archive"]  = arch
        data[f"{run}__max_nov"]  = nov

    # Panel 1: step size
    ax0 = axes[0]
    ax0.set_title("Step size stays small", fontsize=22, fontfamily=DISPLAY_FAM,
                  fontweight="bold", color="#1F2937", pad=12, loc="left")
    ax0.set_xlabel("Search iteration", fontsize=18, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937", labelpad=10)
    ax0.set_ylabel("Step size (starting value 0.18)", fontsize=18, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937", labelpad=10)
    # Reference line at 0.18
    ax0.axhline(0.18, color="#6B7280", linestyle="--", linewidth=1.3)
    xlim = ax0.get_xlim()
    ax0.text(xlim[1], 0.18 + 0.005, "starting step size",
             fontsize=14, fontfamily=BODY_FAM, color="#6B7280",
             ha="right", va="bottom")
    # Legend in panel 1 upper-right
    leg = ax0.legend(
        loc="upper right",
        fontsize=14,
        frameon=False,
        labelspacing=0.4,
        handlelength=1.6,
    )
    for txt in leg.get_texts():
        txt.set_fontfamily(BODY_FAM)
        txt.set_color("#1F2937")

    # Panel 2: archive growth
    ax1 = axes[1]
    ax1.set_title("Archive grows then saturates", fontsize=22, fontfamily=DISPLAY_FAM,
                  fontweight="bold", color="#1F2937", pad=12, loc="left")
    ax1.set_xlabel("Search iteration", fontsize=18, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937", labelpad=10)
    ax1.set_ylabel("Number of accepted stories", fontsize=18, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937", labelpad=10)

    # Panel 3: novelty per batch
    ax2 = axes[2]
    ax2.set_title("Max novelty climbs then plateaus", fontsize=22, fontfamily=DISPLAY_FAM,
                  fontweight="bold", color="#1F2937", pad=12, loc="left")
    ax2.set_xlabel("Search iteration", fontsize=18, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937", labelpad=10)
    ax2.set_ylabel("Max novelty per batch (z-score)", fontsize=18, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937", labelpad=10)

    for ax in axes:
        style_axes(ax)
        ax.tick_params(axis="both", labelsize=14)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            lbl.set_fontfamily(BODY_FAM)

    # Suptitle
    fig.text(0.02, 0.93, "What the search does over iterations",
             fontsize=28, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937")

    out_png = OUT_DIR / "sigma_dashboard.png"
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

    np.savez(DATA_DIR / "sigma_dashboard.npz", **data)
    print(f"wrote {out_png}")


# -----------------------------------------------------------------------------
# Figure 3: Pareto novelty vs LitBench quality
# -----------------------------------------------------------------------------
def _pareto_front(pts):
    """Return indices of non-dominated points (maximize both axes)."""
    keep = np.ones(len(pts), bool)
    for i, p in enumerate(pts):
        if not keep[i]:
            continue
        dominated = (pts >= p).all(1) & (pts > p).any(1)
        keep &= ~dominated
        keep[i] = True
    return np.where(keep)[0]


def make_pareto_litbench():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=200)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.84, bottom=0.16)

    data = {}
    total = 0
    for run in ORDER:
        nov = load_novelties(run)
        q   = load_litbench_scores(run)
        c   = COLOR[run]
        ax.scatter(nov, q, s=80, c=c, alpha=0.7,
                   edgecolors="#1F2937", linewidths=0.4,
                   label=LABEL[run])
        idx = _pareto_front(np.stack([nov, q], axis=1))
        ax.scatter(nov[idx], q[idx], s=150,
                   facecolors="none", edgecolors=c, linewidths=1.5)
        data[f"{run}__novelty"] = nov.astype("f4")
        data[f"{run}__litbench"] = q.astype("f4")
        data[f"{run}__pareto_idx"] = idx.astype("i4")
        total += len(nov)

    ax.set_xlabel("Novelty score (more unusual ->)",
                  fontsize=22, fontfamily=DISPLAY_FAM, fontweight="bold",
                  color="#1F2937", labelpad=12)
    ax.set_ylabel("Quality (LitBench reward score)",
                  fontsize=22, fontfamily=DISPLAY_FAM, fontweight="bold",
                  color="#1F2937", labelpad=12)
    ax.tick_params(axis="both", labelsize=14)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontfamily(BODY_FAM)

    style_axes(ax)
    ax.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, alpha=0.5)

    # Legend bottom-right
    leg = ax.legend(
        loc="lower right",
        fontsize=18,
        frameon=False,
        labelspacing=0.4,
        handlelength=1.4,
        scatterpoints=1,
        markerscale=0.9,
    )
    for txt in leg.get_texts():
        txt.set_fontfamily(BODY_FAM)
        txt.set_color("#1F2937")

    # Title + subtitle
    fig.text(0.06, 0.93, "Are novel stories also good stories?",
             fontsize=28, fontfamily=DISPLAY_FAM, fontweight="bold", color="#1F2937")
    fig.text(0.06, 0.885, f"Each point is one of {total} generated stories",
             fontsize=16, fontfamily=BODY_FAM, color="#6B7280")

    out_png = OUT_DIR / "pareto_litbench.png"
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

    np.savez(DATA_DIR / "pareto_litbench.npz", **data)
    print(f"wrote {out_png}  (total stories: {total})")


if __name__ == "__main__":
    make_transfer_rho()
    make_sigma_dashboard()
    make_pareto_litbench()
    print("done")
