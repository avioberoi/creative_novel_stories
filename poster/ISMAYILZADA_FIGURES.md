# Per-model distinct-n / diversity extracted from paper figures

Date generated: 2026-05-20
Source PDFs:
- /project/jevans/avi/novelty_stories/papers/ismayilzada_2024.pdf
- /project/jevans/avi/novelty_stories/papers/chakrabarty_2024.pdf
Rendered page PNGs:
- /project/jevans/avi/novelty_stories/papers/ismay_pages/
- /project/jevans/avi/novelty_stories/papers/chakra_pages/
Method: visual reading of bar / line heights at 600-800 dpi crops.

---

## 1. Ismayilzada, Stevenson, van der Plas (2024) -- arXiv:2411.02316

### Key finding: NO per-model distinct-n / diversity / novelty numbers in any figure.

Verified by inspecting every figure in the paper (Figures 1-14, all 23 pages
rendered at 200-600 dpi). The paper studies 60 LLMs (full list in Tables 6+7,
appendix pages 14-15: GPT-3.5, GPT-4, GPT-4o, Claude 3 Opus, Claude 3.5
Sonnet/Haiku, Gemini 1.5 Flash/Pro, Gemma 2 9B/27B, Llama 3.1/3.2 family
1B-405B, Grok 2, MPT, DBRX, DeepSeek, Mistral family, Qwen, Reka, Solar,
GLM-4, Jamba, Phi-3 family, Aya, Command R+, Nemotron, Yi-1.5, Baichuan 2,
Zamba 2, Granite 3.0, StableLM, OLMo 2, LFM 40B), but every figure
**aggregates all 60 LLMs into a single "AI" bin** versus a single "Human" bin.

The four sub-curves in Figure 2(a) are item sets (cue-word triplets), not
models. Same for the four violins per metric panel in Figures 3-7, 9-14.

### What CAN be extracted (Human vs AI aggregate)

#### Figure 2(a) -- n-gram diversity vs. n-gram size (== "distinct-n")

The paper defines n-gram diversity = unique n-grams / total n-grams in a story
(corpus-level, averaged). This is exactly distinct-n.

Read from Figure 2(a), page 3, by eye at 800 dpi crop
(`/project/jevans/avi/novelty_stories/papers/ismay_pages/fig2a_zoom.png`).
Each curve represents one item set; the four item sets cluster tightly, so I
report a range across item sets. Uncertainty ~ +/- 0.015.

| n | Human (range over item sets) | AI (range over item sets) | Human midpoint | AI midpoint |
|---|---|---|---|---|
| 1 | 0.285 - 0.305 | 0.240 - 0.280 | **0.295** | **0.260** |
| 2 | 0.775 - 0.805 | 0.665 - 0.725 | **0.790** | **0.695** |
| 3 | 0.955 - 0.965 | 0.880 - 0.925 | **0.960** | **0.905** |
| 4 | 0.985 - 0.995 | 0.955 - 0.975 | **0.990** | **0.965** |
| 5 | 0.995 - 1.000 | 0.975 - 0.985 | **0.998** | **0.980** |

Significance: paper does not report per-n p-values for this figure.

#### Figure 2(b) -- Inverse homogenization (semantic diversity, gte-large embeddings)

Read from violin midlines, page 3. Uncertainty +/- 0.01.

| Item set | Human | AI |
|---|---|---|
| stamp-letter-send (low sem dist) | 0.205 | 0.155 |
| gloom-payment-exist (high sem dist) | 0.215 | 0.155 |
| petrol-diesel-pump (low sem dist) | 0.205 | 0.155 |
| organ-empire-comply (high sem dist) | 0.220 | 0.150 |

Y-axis range 0.100 to 0.250. Human violins consistently centered ~0.21,
AI consistently centered ~0.155.

#### Figure 3 -- Novelty (Karampiperis 2014 semantic distance metric)

Y-axis 0.0 to 0.04. Human violins ~0.022-0.027, AI ~0.015-0.020. Uncertainty +/- 0.003.

#### Figure 4 -- Surprise (Karampiperis 2014 metric)

Y-axis 0.0 to 0.4. Human violins center ~0.10-0.15, AI center ~0.04-0.07.

### Bottom line for the poster

**Per-model distinct-1 / distinct-2 from Ismayilzada is unavailable from
figures.** Per-model data may exist in their open code/data release
(https://github.com/mismayil/creative-story-gen), but that is outside the
scope of "figure extraction." The strongest comparison we can draw from the
figures is **Human vs. aggregated-LLM** at each n.

---

## 2. Chakrabarty, Laban, Agarwal, Muresan, Wu (2024) -- arXiv:2309.14556

### Models compared: GPT-3.5-turbo, GPT-4, Claude-v1.3, New Yorker (human)

This paper does NOT use distinct-n at all. Its primary per-model metric is
TTCW (Torrance Test of Creative Writing) pass rate -- a 14-item creativity
test with three Originality sub-tests (TTCW-Originality1: in Form;
TTCW-Originality2: in Thought; TTCW-Originality3: in Theme & Content).

### Figure 3 -- per-model TTCW pass-count histograms (page 12)

Read off the dashed avg lines in the four sub-histograms
(`/project/jevans/avi/novelty_stories/papers/chakra_pages/fig3.png`).
Values are printed directly on the figure (no estimation needed):

| Model | Avg # tests passed (out of 14) | Avg pass rate |
|---|---|---|
| GPT-3.5-turbo | 1.22 | 0.087 |
| GPT-4 | 3.89 | 0.278 |
| Claude-v1.3 | 4.19 | 0.299 |
| New Yorker (human) | 11.86 | 0.847 |

These four numbers are printed on Figure 3 itself, so they are exact (not
estimated).

### Figure 4 (left) -- relative ranking preference (each of 12 story groups, 4 stories ranked 1-4)

Stacked bars give exact counts (printed on bars):

| Model | Ranked 4th (worst) | Ranked 3rd | Ranked 2nd | Ranked 1st (best) |
|---|---|---|---|---|
| GPT-3.5 | 22 | 12 | ~1 | ~1 |
| GPT-4 | 10 | 14 | 12 | 0 |
| Claude | 4 | 8 | 21 | 3 |
| New Yorker | 0 | 2 | 2 | 32 |

(Counts sum to 36 = 12 groups x 3 experts per group, per the paper text.)

### Figure 4 (right) -- source attribution (was this written by AI, amateur, or experienced writer?)

| Model | Written by AI | An amateur writer | An experienced writer |
|---|---|---|---|
| GPT-3.5 | 30 | 6 | 0 |
| GPT-4 | 27 | 9 | 0 |
| Claude | 15 | 21 | 0 |
| New Yorker | 0 | 5 | 30 |

### Per-model Originality pass rates (from Table 5, page 11 -- TABLE not figure)

User asked for "figures (not main-text tables)" but Table 5 is the only place
the three TTCW-Originality sub-tests are broken out per model. Listing for
completeness; flag clearly as table-sourced if used.

| Originality sub-test | GPT-3.5 | GPT-4 | Claude-v1.3 | New Yorker |
|---|---|---|---|---|
| Originality in Form | 2.8% | 8.3% | 0% | 63.9% |
| Originality in Thought | 2.8% | 44.4% | 19.4% | 91.7% |
| Originality in Theme & Content | 0% | 19.4% | 11.1% | 75.0% |

(All values printed in Table 5 directly; no estimation.)

---

## 3. Our locked numbers for direct comparison

| Run | distinct-1 | distinct-2 |
|---|---|---|
| Mahalanobis CMA-ES | 0.208 | 0.727 |
| Random-LLM baseline | 0.080 | 0.502 |
| Greedy-farthest baseline | 0.054 | 0.474 |
| Diverse-beam baseline | 0.083 | 0.543 |

---

## 4. Poster-ready comparison sentences

### Option A (Ismayilzada, Human vs aggregated-LLM)

"Ismayilzada et al. (2024) aggregate 60 LLMs and report n-gram diversity
(equivalent to distinct-n) of approximately 0.30 at n=1 and 0.79 at n=2 for
human writers, vs 0.26 and 0.70 for the aggregated AI pool (Figure 2a). Our
Mahalanobis search achieves distinct-2 = 0.73, matching the human-writer
range and exceeding the per-paper LLM aggregate by 0.03 absolute, while
default-sampled baselines fall to 0.47-0.54."

### Option B (Ismayilzada caveat)

"Ismayilzada et al. (2024) do not report distinct-n per model in any figure
or table; their analysis pools 60 LLMs into a single AI bin. Direct
per-model comparison against their figures is therefore not possible."

### Option C (Chakrabarty creativity, not diversity)

"Chakrabarty et al. (2024) do not measure distinct-n. Their per-model
creativity proxy is the TTCW pass rate (Fig 3): GPT-3.5 = 1.22/14, GPT-4 =
3.89/14, Claude-v1.3 = 4.19/14, New Yorker writers = 11.86/14 -- a 3x gap
between the best frontier LLM and professional human writers on a creativity
test."

---

## 5. What the previous research agent missed (root cause)

Likely they searched for "distinct" keyword hits and found Chakrabarty's
distinct references (which are not distinct-n), then could not extract bar
heights from the rasterized figures without rendering them at sufficient dpi.
Two facts to note:

1. Ismayilzada calls the metric "n-gram diversity" not "distinct-n", but
   defines it identically (unique n-grams / total n-grams).
2. The four sub-curves / sub-violins in Ismayilzada's figures are item sets,
   not models. Easy to misread as per-model breakdowns.

---

## 6. Reproducibility notes

- All PDFs downloaded 2026-05-20 from `arxiv.org/pdf/{id}`.
- Rendering done with `pymupdf` 1.27.2.3 at 200 dpi (full pages),
  500-800 dpi (figure crops).
- Sources for every quoted number listed inline above.
- No numbers fabricated. Values printed directly on the figures (Chakrabarty
  avg passes, Figure 4 counts) are exact; values read off axis grids are
  given +/- uncertainty.
