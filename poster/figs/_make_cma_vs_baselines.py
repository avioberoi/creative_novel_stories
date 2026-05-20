"""Comparison plot: CMA-ES (5 metrics) vs baselines (random / divbeam / greedy).

NO unicode / Greek letters anywhere.
Outputs: /home/aoberoi1/novelty_stories/poster/figs/cma_vs_baselines.png
"""
from pathlib import Path
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle

# Fonts
FONT_DIR = Path("/home/aoberoi1/.claude/skills/canvas-design/canvas-fonts")
for ff in [
    "BricolageGrotesque-Bold.ttf",
    "BricolageGrotesque-Regular.ttf",
    "WorkSans-Bold.ttf",
    "WorkSans-Regular.ttf",
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Bold.ttf",
]:
    p = FONT_DIR / ff
    if p.exists():
        fm.fontManager.addfont(str(p))

DISPLAY = "Bricolage Grotesque"
BODY    = "Work Sans"
MONO    = "JetBrains Mono"

mpl.rcParams.update({
    "font.family": BODY,
    "axes.unicode_minus": False,
    "axes.edgecolor": "#1F2937",
    "axes.linewidth": 1.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": "#FFFFFF",
    "figure.facecolor": "#FFFFFF",
    "savefig.facecolor": "#FFFFFF",
})

RUNS = Path("/project/jevans/avi/novelty_stories/runs")
OUT  = Path("/home/aoberoi1/novelty_stories/poster/figs/cma_vs_baselines.png")

# CMA-ES (top group) — Okabe-Ito
CMA = [
    ("mahalanobis_s42", "Mahalanobis",   "#0072B2"),
    ("euclidean_s42",   "Euclidean",     "#D55E00"),
    ("cosine_s42",      "Cosine",        "#009E73"),
    ("lof_s42",         "LOF",           "#CC79A7"),
    ("diffusion_s42",   "Diffusion-map", "#E69F00"),
]
# Baselines (bottom group) — gray scale
BASELINES = [
    ("baseline_random",  "Random-LLM",      "#6B7280"),
    ("baseline_greedy",  "Greedy-farthest", "#9CA3AF"),
    ("baseline_divbeam", "Diverse-beam",    "#D1D5DB"),
]

METRICS = [
    ("transfer", "Transfer rank correlation"),
    ("litbench", "LitBench mean reward"),
    ("d1",       "Distinct-1 (lexical)"),
    ("d2",       "Distinct-2 (bigram)"),
]


def load_row(run_dir):
    """Return dict with values for each metric, or None entry if file missing."""
    base = RUNS / run_dir
    row = {"transfer": None, "litbench": None, "d1": None, "d2": None,
           "incomplete": False}
    tp = base / "transfer.npz"
    lp = base / "litbench.npz"
    sp = base / "sun_metrics.json"
    if tp.exists():
        row["transfer"] = float(np.load(tp, allow_pickle=False)["spearman_rho"])
    if lp.exists():
        s = np.load(lp, allow_pickle=False)["scores"]
        row["litbench"] = float(np.asarray(s, dtype="f4").mean())
    if sp.exists():
        sm = json.loads(sp.read_text())
        row["d1"] = float(sm.get("distinct_1", np.nan))
        row["d2"] = float(sm.get("distinct_2", np.nan))
    row["incomplete"] = not (tp.exists() and lp.exists() and sp.exists())
    return row


def main():
    cma_rows  = [(rd, lbl, c, load_row(rd)) for rd, lbl, c in CMA]
    base_rows = [(rd, lbl, c, load_row(rd)) for rd, lbl, c in BASELINES]

    # All rows ordered: CMA on top, then visual gap, then baselines.
    all_rows = cma_rows + base_rows
    n_rows = len(all_rows)
    n_metrics = len(METRICS)

    # Figure
    fig, axes = plt.subplots(1, n_metrics, figsize=(12, 6), dpi=200, sharey=True)
    fig.subplots_adjust(left=0.13, right=0.985, top=0.80, bottom=0.10, wspace=0.45)

    # y positions: from top (highest y) -> bottom (lowest y).
    # Add a half-row gap between the two groups.
    gap = 0.7
    y_positions = []
    for i in range(len(cma_rows)):
        y_positions.append(n_rows + gap - i)  # CMA at high y
    for j in range(len(base_rows)):
        y_positions.append(len(base_rows) - j)  # baselines at low y
    y_positions = np.asarray(y_positions, dtype="f4")
    # separator y (between CMA bottom and baseline top)
    sep_y = (y_positions[len(cma_rows) - 1] + y_positions[len(cma_rows)]) / 2.0

    # x-axis ranges per metric
    metric_xlim = {
        "transfer": (0.0, 1.0),
        "litbench": None,   # set after we know values
        "d1":       None,
        "d2":       None,
    }
    metric_xticks = {
        "transfer": [0.0, 0.25, 0.5, 0.75, 1.0],
    }

    # Collect all values for autoscaling
    vals_by_metric = {m: [] for m, _ in METRICS}
    for rd, lbl, c, row in all_rows:
        for m, _ in METRICS:
            v = row[m]
            if v is not None and not (isinstance(v, float) and np.isnan(v)):
                vals_by_metric[m].append(v)

    for m, _ in METRICS:
        if metric_xlim[m] is None:
            vs = vals_by_metric[m]
            if vs:
                lo = 0.0
                hi = max(vs) * 1.25
                if hi <= 0:
                    hi = 1.0
                metric_xlim[m] = (lo, hi)
            else:
                metric_xlim[m] = (0.0, 1.0)

    # Plot each metric
    for col, (m_key, m_label) in enumerate(METRICS):
        ax = axes[col]
        xlim = metric_xlim[m_key]
        for (rd, lbl, c, row), y in zip(all_rows, y_positions):
            v = row[m_key]
            missing = (v is None) or (isinstance(v, float) and np.isnan(v))
            alpha = 0.4 if row["incomplete"] else 1.0
            if missing:
                # placeholder thin bar at zero, with dash annotation
                ax.barh(y, xlim[1] * 0.02, color=c, alpha=0.25,
                        edgecolor="#1F2937", linewidth=0.6, height=0.7)
                ax.text(xlim[1] * 0.04, y, "—",
                        va="center", ha="left",
                        fontsize=12, fontfamily=MONO, color="#6B7280")
            else:
                ax.barh(y, v, color=c, alpha=alpha,
                        edgecolor="#1F2937", linewidth=0.7, height=0.7)
                # number annotation
                # Format depends on metric
                if m_key == "transfer":
                    txt = f"{v:.2f}"
                elif m_key == "litbench":
                    txt = f"{v:.2f}"
                else:
                    txt = f"{v:.3f}"
                # Decide inside vs right of bar
                bar_frac = v / xlim[1] if xlim[1] else 0
                if bar_frac > 0.55:
                    ax.text(v - xlim[1] * 0.02, y, txt,
                            va="center", ha="right",
                            fontsize=10, fontfamily=MONO,
                            color="#FFFFFF", fontweight="bold")
                else:
                    ax.text(v + xlim[1] * 0.02, y, txt,
                            va="center", ha="left",
                            fontsize=10, fontfamily=MONO, color="#1F2937")

        ax.set_xlim(xlim)
        if m_key in metric_xticks:
            ax.set_xticks(metric_xticks[m_key])
        else:
            # nice round ticks
            lo, hi = xlim
            ticks = np.linspace(lo, hi, 4)
            ax.set_xticks(ticks)
            if m_key == "litbench":
                ax.set_xticklabels([f"{t:.1f}" for t in ticks])
            else:
                ax.set_xticklabels([f"{t:.2f}" for t in ticks])

        ax.set_title(m_label, fontsize=12, fontfamily=DISPLAY,
                     fontweight="bold", color="#1F2937", pad=10, loc="left")
        ax.tick_params(axis="x", labelsize=9)
        for lbl in ax.get_xticklabels():
            lbl.set_fontfamily(BODY)
            lbl.set_color("#1F2937")
        # spines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.xaxis.grid(True, color="#E5E7EB", linewidth=0.6, alpha=0.6)
        ax.set_axisbelow(True)
        # hairline separator between the two groups
        ax.axhline(sep_y, color="#1F2937", linewidth=0.6, alpha=0.7)

    # Y-tick labels only on leftmost axis
    axes[0].set_yticks(y_positions)
    axes[0].set_yticklabels(
        [lbl for (_, lbl, _, _) in all_rows],
        fontsize=11, fontfamily=BODY, color="#1F2937",
    )

    # Group labels on far-left margin
    cma_y_center  = np.mean(y_positions[:len(cma_rows)])
    base_y_center = np.mean(y_positions[len(cma_rows):])
    fig.text(0.012, axes[0].transData.transform((0, cma_y_center))[1]
             / fig.bbox.height,
             "CMA-ES",
             fontsize=11, fontfamily=DISPLAY, fontweight="bold",
             color="#374151", rotation=90, va="center", ha="left")
    fig.text(0.012, axes[0].transData.transform((0, base_y_center))[1]
             / fig.bbox.height,
             "Baselines",
             fontsize=11, fontfamily=DISPLAY, fontweight="bold",
             color="#6B7280", rotation=90, va="center", ha="left")

    # Title + subtitle
    fig.text(0.045, 0.945,
             "Does the search add anything over naive baselines?",
             fontsize=20, fontfamily=DISPLAY, fontweight="bold",
             color="#1F2937")
    fig.text(0.045, 0.905,
             "Five distance metrics (top) vs three baselines (bottom) on the same generator.",
             fontsize=12, fontfamily=BODY, color="#6B7280")

    # Headline annotation: CMA mean transfer rho vs baseline mean
    cma_t = [r[3]["transfer"] for r in cma_rows if r[3]["transfer"] is not None]
    base_t = [r[3]["transfer"] for r in base_rows if r[3]["transfer"] is not None]
    cma_mean = float(np.mean(cma_t)) if cma_t else float("nan")
    base_mean = float(np.mean(base_t)) if base_t else float("nan")
    headline = (
        f"CMA-ES mean transfer rank correlation: {cma_mean:.2f}\n"
        f"          (vs baseline {base_mean:.2f})"
        if not np.isnan(base_mean) else
        f"CMA-ES mean transfer rank correlation: {cma_mean:.2f}\n"
        f"          (vs baseline n/a)"
    )
    fig.text(0.985, 0.945, headline,
             fontsize=10, fontfamily=MONO, color="#1F2937",
             ha="right", va="top",
             linespacing=1.4)

    # Footnote if any baseline is incomplete
    incomplete_labels = [lbl for (_, lbl, _, row) in base_rows if row["incomplete"]]
    if incomplete_labels:
        note = "  ".join(f"{lbl.lower()}: still running"
                         for lbl in incomplete_labels)
        fig.text(0.985, 0.04, note,
                 fontsize=9, fontfamily=MONO, color="#9CA3AF",
                 ha="right", va="bottom")

    fig.savefig(OUT, dpi=200)
    plt.close(fig)
    print(f"wrote {OUT}")
    print(f"CMA mean rho:  {cma_mean:.3f}")
    print(f"Base mean rho: {base_mean:.3f}")
    for (rd, lbl, _, row) in all_rows:
        print(f"  {lbl:18s}  t={row['transfer']}  lb={row['litbench']}  "
              f"d1={row['d1']}  d2={row['d2']}  incomp={row['incomplete']}")


if __name__ == "__main__":
    main()
