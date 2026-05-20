# Poster design notes — constraints for next-wave fixes

Three things still wrong after the current in-flight fix wave (v4):

## 1. The pipeline diagram is too schematic / naive

Boxes-and-arrows inline-SVG looks amateur on a printed conference poster. Replace
with a **visual-first** representation of the same idea, using REAL data:

**Option A (recommended): "Where the search lives"**
- A 2D UMAP scatterplot of the 5,001-story corpus (light gray dots), drawn at
  about 40% of column width, with the 87 euclidean archive points overlaid in
  the metric's accent color and a CMA-ES trajectory line (the search's μ over
  iterations) drawn as a connected polyline from start to last iter.
- Beside it: a single story snippet (the top-novelty one) with one or two
  hand-drawn annotation arrows pointing from the UMAP point to phrases in the
  story.
- Below: a tiny vertical strip showing the 5 retrieved neighbors as small text
  labels.

**Option B: side-by-side "naive LLM vs novelty-search" comparison**
- Left column: 3 paragraphs of what a vanilla Qwen3-32B produces when asked
  "write a New Yorker story opening" (from baseline_random archive).
- Right column: 3 paragraphs from the mahalanobis search archive at matched
  word count.
- Caption: "What changes when the search asks for the *periphery* of the corpus."

Either is fine. Both replace the box-and-arrow naivety with real visual artifact.

## 2. NO unicode / Greek letters in axis labels, titles, plot annotations

- `σ` → `step size` (or `sigma` written out only if absolutely necessary)
- `ρ` → `rank correlation` (or `rho` written out only if absolutely necessary)
- `λ` → `population size`
- `μ` → `mean`
- `τ` → `coherence threshold`
- `≈` → `~` or `about`
- `≥`, `≤` → `at least`, `at most`
- Math notation belongs in the paper, not on a poster. KaTeX-rendered math is
  fine WITHIN body text (e.g., "the population size $\lambda = 16$") but axis
  labels and chart titles should be plain English so they survive print + font
  fallback.

## 3. Text-heavy cards need to become visual

Cards that are currently walls of text and should be replaced with annotated
visual artifacts where possible:

- **Motivation** ("The middle of the distribution"): replace with a tiny labelled
  KDE/histogram showing where typical LLM outputs sit in corpus space (peaked
  near the centroid) and where the periphery is.
- **Process highlights** ("Three things we learned the hard way"): keep as text
  but add a tiny screenshot or before/after example beside each vignette (e.g.,
  the broken `<think>...</think>` output vs the clean prose after the fix).
- **Reflection**: collapse to one sentence + a hairline rule.

## Locked design system (do not alter)

- Orientation: landscape 36"×24" = 914mm × 610mm
- Background: pure white `#FFFFFF`
- Display: Space Grotesk Bold
- Body: Inter
- Mono (labels): JetBrains Mono
- Accent: single `#1E40AF` deep blue
- Data viz palette: Okabe-Ito subset assigned to metrics by transfer-rho order
- Plot axis labels: 24pt bold; tick labels: 20pt; legend: 22pt; title: 30pt
- The headline number is the transfer rank correlation = 0.80

## Locked data (do not invent)

| Metric | N | Transfer rank-corr | LitBench mean | LitBench p90 | distinct-1 | distinct-2 |
|---|---|---|---|---|---|---|
| Mahalanobis | 62 | 0.799 | 1.950 | 2.653 | 0.208 | 0.727 |
| Euclidean | 87 | 0.714 | 1.907 | 2.591 | 0.182 | 0.699 |
| Cosine | 89 | 0.713 | 1.960 | 2.628 | 0.181 | 0.702 |
| LOF | 78 | 0.623 | 1.995 | 2.594 | 0.183 | 0.700 |
| Diffusion-map | 65 | 0.424 | 1.728 | 2.309 | 0.150 | 0.640 |

Final step sizes (starting step = 0.18): Mahalanobis 0.20, Diffusion 0.18,
LOF 0.25, Euclidean 0.26, Cosine 0.23. None drifted off-manifold.

Image-paper baseline rank correlation: best 0.629 (Frontier-Euclidean).
Our best (Mahalanobis) beats it by 0.17 in absolute terms.

## Locked story examples (top-novelty from euclidean archive)

Use these three stories verbatim (first ~80 words each) in the hero card:

1. "THE HORSE WHO WANTED TO SING" (novelty 6.70) — euclidean archive index 11
2. (second-rank novelty) — euclidean archive index 76
3. (third-rank novelty) — euclidean archive index 69

LitBench scores from `runs/euclidean_s42/litbench.npz` at those indices were
2.14, 1.34, 1.94 respectively. Use them in the chips.
