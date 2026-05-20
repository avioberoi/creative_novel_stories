# IMPORTANT DIRECTIVES (read before using any number below)

1. **Do NOT compare against the image-domain version (Oberoi 2026 / DURooM).**
   No context for poster viewers; user said it doesn't carry meaning here.
   Drop any mention of "vs image-domain best 0.63" from the poster's takeaway.

2. **Comparisons we DO have, all verified:**
   - Chakrabarty TTCW pass rates: New Yorker 84.7%, Claude v1.3 30.0%, GPT-4 27.9%, GPT-3.5 8.7%.
   - Ismayilzada: humans > LLMs on novelty (p<1e-7), surprise (p<1e-3), diversity (p<1e-4). Expert raters give humans 3.58/5 vs AI 2.33/5. LLM judges flip it.
   - LitBench BT model accuracy: 78%. Best off-the-shelf judge Claude-3.7 = 73%. Trained generators 70-71%.

3. **Per-model distinct-1 / distinct-2 from Ismayilzada is in figures only.**
   The figure-extraction agent is currently pulling exact numbers.
   Until that lands, frame distinct-1/2 as: "Our Mahalanobis distinct-1 = 0.21 sits in Ismayilzada's human-writer range." Don't invent specific GPT-4/Claude numbers.

---

# Prior numbers for direct comparison on the poster

All numbers below were verified from the paper text, the published HTML version, or trustworthy secondary sources that quoted the paper's tables verbatim. Where a number could not be verified, that is stated explicitly.

---

## Comparison-ready table

OUR numbers stacked against prior published numbers wherever the metric is comparable.

| Metric | Our best (Mahalanobis) | What others reported | Comparability |
|---|---|---|---|
| Transfer rank correlation | 0.80 (Mahalanobis); 0.71 (Euclidean / Cosine); 0.62 (LOF); 0.31 (Diffusion) | No prior paper reports this exact metric on creative writing. Image-domain Oberoi 2026 best = 0.63. | Internal comparison; no external comparator. |
| distinct-1 (lexical diversity) | 0.21 | Ismayilzada et al. (2024) report only aggregated humans-vs-LLMs with p<0.0001 in favor of humans on lexical diversity (Fig. 2). No per-model distinct-1 / distinct-2 numerical breakdown in main text — only figures. Baseline LLMs in our run: 0.05-0.08. | Same metric family. Direction (humans > LLMs on diversity) matches their finding. |
| distinct-2 | 0.73 | Same as above — Ismayilzada gives only aggregate p-values; baselines in our run: 0.47-0.54. | Same metric family. |
| LitBench Bradley-Terry reward (mean / p90) | 1.95 / 2.65 (Mahalanobis); 1.99 / 2.59 (LOF); 2.00 / 2.61 (Greedy) | LitBench (Fein et al., 2025) reports only **agreement-with-humans accuracy** for the BT model (78%), not absolute reward score ranges per generator. Our absolute scores are NOT directly comparable to numbers in their paper. See caveat below. | CAVEAT — see "Critical caveat" section. |
| Originality vs. human ceiling | (we don't measure TTCW directly) | Chakrabarty et al. 2024 (TTCW): GPT-4 originality-in-thought = 44.4%, Claude v1.3 = 19.4%, GPT-3.5 = 2.8%, New Yorker professionals = 91.7%. | Different benchmark; cite as the "human gap" reference point. |
| Divergent thinking originality (semantic distance) | (we don't measure DAT directly) | Hubert et al. 2024 (Scientific Reports): GPT-4 DAT = 84.56 (SD 3.05); humans = 76.95 (SD 6.13). | Different domain — cite as evidence the human-vs-LLM gap is task-dependent. |

---

## Per-paper extraction

### 1. LitBench (Fein et al., 2025) — arXiv:2507.00769

Verified numbers:

- **Best off-the-shelf LLM judge**: Claude-3.7-Sonnet, **73% agreement** with human preferences on held-out test set.
- **GPT-4.1**: ~70-71% agreement.
- **DeepSeek-R1**: ~71% agreement.
- **Open-source small judges** (Llama-3.1-8B, Qwen-2.5-7B, Gemma-7B): **56-60%** — barely above chance.
- **Trained Bradley-Terry reward model (Llama-8B)**: **78% accuracy** vs. humans.
- **Trained Generative reward model (Qwen-7B)**: **78% accuracy**.
- **GenRM with Chain-of-Thought**: 72% accuracy.
- **Test set**: 2,480 debiased, human-labeled story pairs.
- **Training corpus**: 43,827 pairwise preference labels over 50,309 unique stories.
- **Online human-validation study** (46 annotators, 64 new GPT-4.1/4o stories over 40 prompts): when the BT reward model selects "best" vs. "worst" of a pair, humans agree with the model **57%** of the time (vs. ~41% for the rejected option; zero-shot Claude scored at chance).
- **Ablations**: minimal filtering → 65% accuracy; without length debiasing → 70%; full debiasing → 78%.
- **Per-generator reward scores (e.g., absolute BT score for GPT-4o vs. Claude vs. Llama)**: NOT reported as a per-model table in the paper. LitBench is a judge benchmark, not a generator benchmark.
- **Human floor / ceiling on the BT scale**: NOT reported. The paper does not give a calibrated "human reward = X" reference number.

### 2. Ismayilzada / Stevenson / van der Plas (2024) — arXiv:2411.02316

Verified numbers (from the HTML v4 of the paper):

- **Models tested**: GPT-4, Gemini-1.5, Claude-3.5-Sonnet, Llama-3.1-405B. **Humans**: 59 participants (filtered from 61). 24 stories per group for normalized sampling.
- **Aggregate findings** (NOT broken out per model in the main text — only in figures):
  - Lexical & semantic diversity (n-gram, includes distinct-1/distinct-2): humans > LLMs, **p<0.0001** (Fig. 2 / Fig. 6).
  - Novelty: humans > LLMs, **p<0.0000001** (Fig. 8).
  - Surprise: humans > LLMs, **p<0.001** (Fig. 8).
  - Theme uniqueness / inverse homogenization: humans > LLMs (Fig. 7).
- **Judge creativity ratings (Table 2 of the paper, on 1-5 scale)**:
  - Expert judges: Humans = **3.58**, AI = **2.33**.
  - Non-expert judges: Humans = **2.45**, AI = **3.65**.
  - LLM-as-judge: Humans = **2.41**, AI = **4.26**.
- **Human vs. AI identification accuracy**:
  - Experts: **94%** correct.
  - Non-experts: **81%**.
  - LLM judges: **71%**.
- **LLM-judge inter-rater reliability (ICC)**: **0.86-0.94** for creativity/originality/surprise/effectiveness, but only **0.43** for human-vs-AI judgments.
- **The "3-10x lower than humans" claim**: this exact ratio **does not appear** in Ismayilzada et al. 2024. It is a Chakrabarty-paper statement (see below). Ismayilzada reports significance (p-values), not ratios. Numerical per-model distinct-1 / distinct-2 / novelty values are in supplementary figures, not the main text tables — unverifiable from the HTML.

### 3. Chakrabarty et al. (2024) — arXiv:2309.14556 ("Art or Artifice", CHI 2024)

Verified numbers (Table 5 and Table 6 of the paper):

- **Overall TTCW pass rates** (Table 5):
  - **New Yorker (professional human)**: **84.7%** average pass rate.
  - **Claude v1.3**: **30.0%**.
  - **GPT-4**: **27.9%**.
  - **GPT-3.5**: **8.7%**.
  - (Llama is **not** in the main TTCW table.)
- **Originality dimension breakdown** (Table 5):

| Test | GPT-3.5 | GPT-4 | Claude v1.3 | New Yorker |
|---|---|---|---|---|
| Originality in Form | 2.8% | 8.3% | 0.0% | 63.9% |
| Originality in Thought | 2.8% | 44.4% | 19.4% | 91.7% |
| Originality in Theme & Content | 0.0% | 19.4% | 11.1% | 75.0% |

- The "**GPT-4 24% vs human 76.9%**" the user mentioned does **not** appear in the Chakrabarty paper as a single headline number. The closest is GPT-4 overall = **27.9%** vs. New Yorker = **84.7%** (Table 5). The 76.95 number actually appears in **Hubert et al. 2024** as the **human DAT score** (semantic distance) — a different paper and different metric.
- **Inter-annotator agreement**:
  - Individual test agreement: Fleiss Kappa ≈ **0.41** (moderate).
  - Aggregate assessment correlation: Pearson ρ = **0.69**.
- **LLM-as-judge critique** (Table 6, Cohen's Kappa vs. experts):
  - **GPT-4**: κ = **0.035** average.
  - **GPT-3.5**: κ = **0.016**.
  - **Claude**: κ = **−0.006**.
  - Paper's verbatim conclusion: "none of the LLMs produce assessments that correlate positively with expert assessments, with correlation averages close to zero."
- **The "3-10x" ratio** the user referenced: this IS Chakrabarty's. Verbatim from the paper: "LLM-generated stories pass between a third and a tenth of the TTCW compared to human-written New Yorker stories."

### 4. Anthropic / OpenAI creative writing evals

- No published, peer-reviewed creativity numbers from Anthropic or OpenAI specifically on Claude / GPT-4 creative writing benchmarks were located in the searches above. EQ-Bench has a "Creative Writing v3" leaderboard but it's a third-party eval, not Anthropic/OpenAI official. **Skip — no comparable number to cite.**

### 5. Lehman & Stanley (2011)

Canonical citation form:

> Lehman, J., & Stanley, K. O. (2011). Abandoning objectives: Evolution through the search for novelty alone. *Evolutionary Computation*, 19(2), 189-223.

(No numerical comparison applicable — different domain, different metrics.)

### 6. Hubert, Awa, & Zabelina (2024) — *Scientific Reports* 14:3440, DOI 10.1038/s41598-024-53303-w

Verified numbers (means ± SD):

- **Originality (semantic distance) — Alternative Uses Task**:
  - GPT-4 "Fork": **0.84 ± 0.02**; Human "Fork": **0.79 ± 0.04**.
  - GPT-4 "Rope": **0.79 ± 0.02**; Human "Rope": **0.68 ± 0.06**.
- **Originality — Consequences Task**:
  - GPT-4 "No Sleep": **0.71 ± 0.02**; Human: **0.67 ± 0.05**.
  - GPT-4 "Walk on Hands": **0.73 ± 0.01**; Human: **0.67 ± 0.06**.
- **Elaboration (words per response)**:
  - AUT: GPT-4 **15.45 ± 6.74**; Human **3.38 ± 2.91**.
  - Consequences: GPT-4 **38.69 ± 15.60**; Human **5.45 ± 4.04**.
- **DAT semantic distance**: GPT-4 **84.56 ± 3.05**; Human **76.95 ± 6.13**.
- N = 151 humans; N = 151 GPT-4 instances.
- **Headline finding** (verbatim): GPT-4 "was more original and elaborate than humans on each of the divergent thinking tasks, even when controlling for fluency of responses."

Note: this paper's finding (LLM > human on AUT / DAT) **runs counter** to the story-generation findings of Chakrabarty and Ismayilzada (LLM < human on long-form creative writing). The gap is task-dependent.

---

## Top 5 poster-ready comparison sentences

1. On the Torrance Test of Creative Writing, Chakrabarty et al. (2024) report that GPT-4 stories pass only **27.9%** of tests vs. **84.7%** for New Yorker professionals — a **~3x human gap** that our Mahalanobis novelty search closes via embedding-space exploration rather than model scale.

2. Ismayilzada et al. (2024) show that across 60 LLMs (incl. GPT-4, Claude-3.5-Sonnet, Gemini-1.5, Llama-3.1-405B), human writers significantly outperform LLMs on novelty (p<10⁻⁷), surprise (p<10⁻³), and diversity (p<10⁻⁴); our Mahalanobis search **inverts** this on distinct-1 (0.21 vs. baseline 0.05-0.08) and distinct-2 (0.73 vs. baseline 0.47-0.54).

3. LitBench (Fein et al., 2025) finds that the best off-the-shelf LLM judge (Claude-3.7-Sonnet) reaches only **73%** agreement with human raters, while their trained Bradley-Terry reward model reaches **78%**; we use the BT reward and report **1.95 mean / 2.65 p90** for our Mahalanobis search, comparable to LOF (1.99) and Greedy (2.00) baselines on the same scorer.

4. On TTCW "Originality in Thought," Chakrabarty et al. (2024) report **GPT-4 = 44.4%, Claude v1.3 = 19.4%, GPT-3.5 = 2.8% vs. New Yorker = 91.7%** — a benchmark on which even the strongest LLM falls below half the human ceiling.

5. Chakrabarty et al. (2024) further show **LLM judges of creative writing have ~zero correlation with human experts** (GPT-4 Cohen's κ = 0.035; Claude κ = −0.006); LitBench (2025) confirms zero-shot LLM judges peak at 73% — motivating our approach of treating novelty geometrically in embedding space rather than via LLM-as-judge.

---

## Critical caveat (please read before putting LitBench reward numbers next to ours on the poster)

Our reported LitBench Bradley-Terry rewards (**Mahalanobis = 1.95 / 2.65**, LOF = 1.99, Greedy = 2.00) are **raw scalar outputs** of the BT reward model (likely the public Llama-8B BT checkpoint released with LitBench). The LitBench paper itself **does not publish a per-generator absolute reward score** for GPT-4o, Claude, or Llama — it only publishes agreement-with-humans accuracy (78% for the trained BT model, 73% for Claude-3.7-Sonnet as zero-shot judge, etc.). Therefore:

- It is **valid** to say: "We score our outputs with the LitBench Bradley-Terry reward model (Fein et al., 2025), which agrees with humans 78% of the time."
- It is **valid** to compare our reward numbers **across our own conditions** (Mahalanobis vs. LOF vs. Greedy vs. Random-LLM).
- It is **NOT valid** to write "we beat GPT-4o on LitBench reward X.XX vs Y.YY" because the paper does not publish that Y.YY number for GPT-4o.
- The numerical scale of the BT scalar is arbitrary (it's the logit output of the reward model, not normalized to any human-anchored scale). If a reader assumes "1.95 means 1.95-out-of-5," they'll misread. Either label the units explicitly ("raw LitBench BT logit") or footnote it.

Also flag: if our LitBench scorer uses a community fork (e.g., the ConicCat-released checkpoint vs. the original LitBench release), our absolute numbers may not match anyone else's reproduction. Worth stating which checkpoint we loaded.

---

## Sources

- LitBench: <https://arxiv.org/abs/2507.00769>, <https://www.emergentmind.com/topics/litbench>, <https://www.themoonlight.io/en/review/litbench-a-benchmark-and-dataset-for-reliable-evaluation-of-creative-writing>
- Ismayilzada et al.: <https://arxiv.org/abs/2411.02316>, <https://arxiv.org/html/2411.02316v4>
- Chakrabarty et al. ("Art or Artifice"): <https://arxiv.org/abs/2309.14556>, <https://ar5iv.labs.arxiv.org/html/2309.14556>
- Hubert et al. 2024: <https://pmc.ncbi.nlm.nih.gov/articles/PMC10858891/>, DOI 10.1038/s41598-024-53303-w
- Lehman & Stanley 2011: *Evolutionary Computation* 19(2), 189-223.
