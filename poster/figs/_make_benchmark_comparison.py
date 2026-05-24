"""Benchmark comparison chart for the poster.

Two stacked panels:
  Panel A — Chakrabarty TTCW pass rates (horizontal bars, New Yorker vs LLMs)
  Panel B — "Our search, in context" text callout with key numbers

NO Greek letters or unicode arrows in titles, axis labels, or annotations.
Output: poster/figs/benchmark_comparison.png
"""
import os
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.gridspec import GridSpec

REPO_ROOT = Path(__file__).resolve().parents[2]

# -----------------------------------------------------------------------------
# Fonts
# -----------------------------------------------------------------------------
FONT_DIR = Path(os.environ.get("FONT_DIR", REPO_ROOT / "fonts"))
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

MAROON     = "#800000"
CHARCOAL   = "#1F2937"
SECONDARY  = "#6B7280"
GRAY_BAR   = "#9CA3AF"
GRID       = "#E5E7EB"
WHITE      = "#FFFFFF"

mpl.rcParams.update({
    "font.family": BODY,
    "axes.unicode_minus": False,
    "axes.edgecolor": CHARCOAL,
    "axes.linewidth": 1.2,
    "axes.facecolor": WHITE,
    "figure.facecolor": WHITE,
    "savefig.facecolor": WHITE,
})

OUT = REPO_ROOT / "poster" / "figs" / "benchmark_comparison.png"


# -----------------------------------------------------------------------------
# Data — Chakrabarty et al. (2024), TTCW (36 items)
# -----------------------------------------------------------------------------
#   entry: (label, passed, total, color)
# Order: top-to-bottom in order of pass rate (highest at top).
TTCW = [
    ("The New Yorker", 32, 36, MAROON),
    ("Claude v1.3",    21, 36, GRAY_BAR),
    ("GPT-4",          12, 36, GRAY_BAR),
    ("GPT-3.5",         1, 36, GRAY_BAR),
]


def main():
    fig = plt.figure(figsize=(12, 10), dpi=200)
    gs = GridSpec(
        nrows=2, ncols=1,
        height_ratios=[3, 2],
        left=0.14, right=0.97,
        top=0.86, bottom=0.06,
        hspace=0.42,
    )

    # =========================================================================
    # Panel A — TTCW pass rates
    # =========================================================================
    axA = fig.add_subplot(gs[0, 0])

    # y positions: row 0 is the highest pass rate, drawn at the top.
    n = len(TTCW)
    y_positions = list(range(n))[::-1]  # [3, 2, 1, 0] => top row at y=3

    # Compute pass-rate percentages, with a small floor so GPT-3.5 stays visible.
    rendered_pcts = []
    for (label, passed, total, color), y in zip(TTCW, y_positions):
        pct = 100.0 * passed / total
        # Floor for visibility — 1/36 = 2.78% which is fine, but to be safe
        # at this resolution we leave it as-is. The 0.5/36 fallback isn't needed.
        rendered_pcts.append(pct)
        axA.barh(y, pct, color=color, height=0.62,
                 edgecolor=CHARCOAL, linewidth=0.6)

    # Annotate each bar with "count   percentage".
    # For the longest (maroon NewYorker) bar, place annotation INSIDE the bar
    # in white so we don't overflow the axes. Others get annotated to the right.
    for (label, passed, total, color), y, pct in zip(TTCW, y_positions, rendered_pcts):
        count_str = f"{passed} / {total}"
        if passed == 1:
            pct_str = "3%"
        elif passed == 32:
            pct_str = "88.9%"
        elif passed == 21:
            pct_str = "58.3%"
        elif passed == 12:
            pct_str = "33.3%"
        else:
            pct_str = f"{pct:.1f}%"

        text = f"{count_str}   {pct_str}"

        if pct >= 70:
            # Inside the bar, white text, right-aligned just before the bar end.
            axA.text(
                pct - 1.5, y, text,
                va="center", ha="right",
                fontsize=16, fontfamily=MONO,
                fontweight="bold",
                color=WHITE,
            )
        else:
            # Outside the bar, charcoal text, just to the right.
            x_text = max(pct + 1.5, 4.0)
            axA.text(
                x_text, y, text,
                va="center", ha="left",
                fontsize=16, fontfamily=MONO,
                fontweight="normal",
                color=CHARCOAL,
            )

    # Axes setup
    axA.set_xlim(0, 100)
    axA.set_ylim(-0.7, n - 0.3)
    axA.set_yticks(y_positions)
    axA.set_yticklabels(
        [t[0] for t in TTCW],
        fontsize=15, fontfamily=BODY, color=CHARCOAL,
    )
    axA.set_xticks([0, 25, 50, 75, 100])
    axA.set_xticklabels(["0%", "25%", "50%", "75%", "100%"],
                        fontsize=11, fontfamily=BODY, color=CHARCOAL)
    axA.set_xlabel(
        "TTCW pass rate (Torrance Test of Creative Writing, 36 items)",
        fontsize=12, fontfamily=BODY, color=CHARCOAL, labelpad=10,
    )

    # Spines + grid
    axA.spines["top"].set_visible(False)
    axA.spines["right"].set_visible(False)
    axA.spines["left"].set_visible(False)
    axA.tick_params(axis="y", length=0)
    axA.tick_params(axis="x", length=4, color=CHARCOAL)
    axA.xaxis.grid(True, color=GRID, linewidth=0.5, alpha=0.5)
    axA.set_axisbelow(True)

    # Panel A title + subtitle (placed in figure coords for clean alignment)
    # Title sits just above the axes.
    posA = axA.get_position()
    fig.text(
        posA.x0, posA.y1 + 0.045,
        "The gap creativity benchmarks expose",
        fontsize=30, fontfamily=DISPLAY, fontweight="bold",
        color=CHARCOAL, ha="left", va="bottom",
    )
    fig.text(
        posA.x0, posA.y1 + 0.018,
        "Chakrabarty et al. (2024). LLMs pass 3 to 58 percent of items. "
        "Human-written New Yorker stories pass 89 percent.",
        fontsize=12, fontfamily=BODY, fontstyle="italic",
        color=SECONDARY, ha="left", va="bottom",
    )

    # =========================================================================
    # Panel B — "Our search, in context" text callout
    # =========================================================================
    axB = fig.add_subplot(gs[1, 0])
    axB.set_xlim(0, 1)
    axB.set_ylim(0, 1)
    axB.set_xticks([])
    axB.set_yticks([])
    for s in axB.spines.values():
        s.set_visible(False)

    posB = axB.get_position()

    # Panel B title
    fig.text(
        posB.x0, posB.y1 + 0.010,
        "Our search, in context",
        fontsize=24, fontfamily=DISPLAY, fontweight="bold",
        color=CHARCOAL, ha="left", va="bottom",
    )

    # Maroon hairline rule at left margin to anchor the block.
    # 0.4mm at 200 dpi ~= 3.15 pt. matplotlib axvline width is in points.
    # Draw it slightly inside the axes left edge.
    rule_x = 0.012  # axes-frac
    axB.plot(
        [rule_x, rule_x], [0.05, 0.95],
        transform=axB.transAxes,
        color=MAROON, linewidth=1.1, solid_capstyle="butt",
        clip_on=False,
    )

    # Layout: each "data callout" has a label line (Work Sans) and a numbers
    # line below it (JetBrains Mono, maroon). This avoids any x-axis collision
    # between long labels and long number strings.
    text_left = 0.035  # axes-frac, just past the maroon rule
    num_indent = 0.060  # numbers slightly indented from label

    # Block 1 — Mahalanobis archive
    axB.text(
        text_left, 0.92,
        "Our Mahalanobis archive",
        transform=axB.transAxes,
        fontsize=18, fontfamily=BODY, color=CHARCOAL,
        fontweight="bold",
        ha="left", va="center",
    )
    axB.text(
        text_left + num_indent, 0.79,
        "distinct-2 = 0.73     transfer-rho = 0.80",
        transform=axB.transAxes,
        fontsize=22, fontfamily=MONO, color=MAROON,
        fontweight="bold",
        ha="left", va="center",
    )
    axB.text(
        text_left + num_indent, 0.69,
        "(held-out encoder we never saw during search)",
        transform=axB.transAxes,
        fontsize=14, fontfamily=BODY, fontstyle="italic",
        color=SECONDARY, ha="left", va="center",
    )

    # Block 2 — Baseline LLM samples
    axB.text(
        text_left, 0.54,
        "Baseline LLM samples in our pipeline",
        transform=axB.transAxes,
        fontsize=18, fontfamily=BODY, color=CHARCOAL,
        fontweight="bold",
        ha="left", va="center",
    )
    axB.text(
        text_left + num_indent, 0.41,
        "distinct-2 = 0.47 to 0.54",
        transform=axB.transAxes,
        fontsize=22, fontfamily=MONO, color=MAROON,
        fontweight="bold",
        ha="left", va="center",
    )

    # Block 3 — Ismayilzada paragraph
    para_lines = [
        ("Ismayilzada (2024) reports humans > LLMs on",       "bold",   CHARCOAL),
        ("novelty (p < 1e-7), surprise (p < 1e-3), diversity (p < 1e-4).",
                                                              "normal", CHARCOAL),
        ("We don't claim to close that gap.",                 "normal", SECONDARY),
        ("We move the LLM's output distribution toward the periphery.",
                                                              "bold",   CHARCOAL),
    ]
    para_top = 0.24
    para_dy  = 0.07
    for i, (line, weight, color) in enumerate(para_lines):
        axB.text(
            text_left, para_top - i * para_dy, line,
            transform=axB.transAxes,
            fontsize=15, fontfamily=BODY, color=color,
            fontweight=weight, ha="left", va="center",
        )

    fig.savefig(OUT, dpi=200, bbox_inches=None, facecolor=WHITE)
    plt.close(fig)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
