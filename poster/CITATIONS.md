# CITATIONS — Novelty Search in Foundation-Model Embedding Space for Creative-Story Generation

Citation set for the ICLR-style poster. Each entry lists (1) full reference, (2) one-sentence summary, (3) inline-citation string for poster prose, (4) why we cite it. Numerical results from prior work that sit naturally next to our scores are collected in the final section.

All arxiv links and DOIs verified May 2026 (search week).

---

## A. CMA-ES — the search algorithm

### A1. Hansen & Ostermeier (2001) — the original CMA-ES paper
- **Reference**: Hansen, N., & Ostermeier, A. (2001). Completely Derandomized Self-Adaptation in Evolution Strategies. *Evolutionary Computation*, 9(2), 159–195.
- **Link**: https://doi.org/10.1162/106365601750190398
- **One-line**: Introduces CMA-ES, deriving an evolution-strategy that adapts the full covariance of a multivariate Gaussian search distribution using an evolution path.
- **Inline form**: (Hansen & Ostermeier, 2001)
- **Why we cite it**: This is the canonical origin of the optimizer we run on top of the embedding space; it is the foundational reference for any CMA-ES use.

### A2. Hansen (2016) — the CMA-ES Tutorial
- **Reference**: Hansen, N. (2016). The CMA Evolution Strategy: A Tutorial. arXiv:1604.00772.
- **Link**: https://arxiv.org/abs/1604.00772
- **One-line**: A self-contained pedagogical exposition of CMA-ES with the modern hyperparameter defaults and step-size adaptation rule used by every current implementation.
- **Inline form**: (Hansen, 2016)
- **Why we cite it**: This is the artifact people actually read and implement against; we cite it for our choice of population size, sigma_0, and the rank-mu and rank-one updates.

### A3. Ros & Hansen (2008) — sep-CMA-ES (the diagonal variant we actually use)
- **Reference**: Ros, R., & Hansen, N. (2008). A Simple Modification in CMA-ES Achieving Linear Time and Space Complexity. In *Parallel Problem Solving from Nature — PPSN X*, LNCS 5199, 296–305. Springer.
- **Link**: https://doi.org/10.1007/978-3-540-87700-4_30 (HAL: https://inria.hal.science/inria-00287367)
- **One-line**: Constrains CMA-ES's covariance matrix to be diagonal, reducing per-step cost from O(n^2) to O(n) and enabling search in high-dimensional embedding spaces.
- **Inline form**: (Ros & Hansen, 2008)
- **Why we cite it**: We run sep-CMA-ES, not full CMA-ES, because the search space is a 768-dim Qwen3-Embedding vector; sep-CMA-ES is what makes that tractable.

---

## B. Novelty search — the methodology lineage

### B1. Lehman & Stanley (2008) — the original conference paper
- **Reference**: Lehman, J., & Stanley, K. O. (2008). Exploiting Open-Endedness to Solve Problems Through the Search for Novelty. In *Proceedings of the Eleventh International Conference on Artificial Life (ALIFE XI)*, 329–336. MIT Press.
- **Link**: https://www.cs.swarthmore.edu/~meeden/DevelopmentalRobotics/lehman_alife08.pdf
- **One-line**: First proposes that selecting purely for behavioral novelty — ignoring the fitness signal entirely — can outperform objective-driven search on deceptive problems.
- **Inline form**: (Lehman & Stanley, 2008)
- **Why we cite it**: It is the original statement of the idea that the poster's method literally implements; we credit the founding move.

### B2. Lehman & Stanley (2011) — the journal article (the canonical citation)
- **Reference**: Lehman, J., & Stanley, K. O. (2011). Abandoning Objectives: Evolution Through the Search for Novelty Alone. *Evolutionary Computation*, 19(2), 189–223.
- **Link**: https://doi.org/10.1162/EVCO_a_00025
- **One-line**: Extended treatment of novelty search showing that an archive-based k-NN sparseness measure produces sustained exploration that objective-driven search cannot.
- **Inline form**: (Lehman & Stanley, 2011)
- **Why we cite it**: This is the paper everyone cites for novelty search; the k-NN sparseness formula we use to score every candidate story is the formula from this paper, just with foundation-model embeddings instead of hand-coded behavior characterizations.

---

## C. Quality-diversity — the broader field

### C1. Mouret & Clune (2015) — MAP-Elites
- **Reference**: Mouret, J.-B., & Clune, J. (2015). Illuminating search spaces by mapping elites. arXiv:1504.04909.
- **Link**: https://arxiv.org/abs/1504.04909
- **One-line**: Introduces MAP-Elites, which tessellates a behavior space into discrete cells and keeps the best solution per cell, illuminating an entire performance landscape rather than seeking a single optimum.
- **Inline form**: (Mouret & Clune, 2015)
- **Why we cite it**: This is the dominant cousin algorithm to what we run; we contrast it in METHOD/INTRO to motivate why a continuous k-NN archive in foundation-embedding space avoids the cell-discretization problem.

### C2. Cully & Demiris (2018) — Quality-Diversity framework
- **Reference**: Cully, A., & Demiris, Y. (2018). Quality and Diversity Optimization: A Unifying Modular Framework. *IEEE Transactions on Evolutionary Computation*, 22(2), 245–259.
- **Link**: https://doi.org/10.1109/TEVC.2017.2704781 (arXiv: https://arxiv.org/abs/1708.09251)
- **One-line**: Unifies novelty search, MAP-Elites, and their variants into a single modular framework, naming the broader field "quality-diversity."
- **Inline form**: (Cully & Demiris, 2018)
- **Why we cite it**: When the poster says "the QD literature," this is the citation that defines that field; useful in a single broad reference in BACKGROUND.

---

## D. Foundation-model embedding spaces — the search space

### D1. Qwen3-Embedding (2025) — our primary search-space encoder
- **Reference**: Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models. arXiv:2506.05176.
- **Link**: https://arxiv.org/abs/2506.05176
- **One-line**: A family of decoder-LLM-derived text embeddings (0.6B–8B) achieving SOTA on MTEB and multilingual retrieval benchmarks, distributed under Apache 2.0.
- **Inline form**: (Zhang et al., 2025) — or "Qwen3-Embedding (Zhang et al., 2025)" in METHOD prose
- **Why we cite it**: Qwen3-Embedding-0.6B (768d) is our search space; this is what CMA-ES proposes points in.

### D2. Xiao et al. (2024) — BGE (committee observer 1)
- **Reference**: Xiao, S., Liu, Z., Zhang, P., Muennighoff, N., Lian, D., & Nie, J.-Y. (2024). C-Pack: Packed Resources For General Chinese Embeddings. In *Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '24)*, 641–649.
- **Link**: https://doi.org/10.1145/3626772.3657878 (arXiv: https://arxiv.org/abs/2309.07597)
- **One-line**: Releases BGE (BAAI General Embedding), a family of widely used contrastively-trained text embeddings backed by a curated training corpus and benchmark.
- **Inline form**: (Xiao et al., 2024)
- **Why we cite it**: BGE-large is one of our two committee observers; required reference for that choice.

### D3. Wang et al. (2024) — E5-Mistral (committee observer 2)
- **Reference**: Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Improving Text Embeddings with Large Language Models. arXiv:2401.00368. (Also: ACL 2024.)
- **Link**: https://arxiv.org/abs/2401.00368
- **One-line**: Fine-tunes Mistral-7B into a text embedding model using purely synthetic LLM-generated supervision, producing the E5-Mistral family.
- **Inline form**: (Wang et al., 2024)
- **Why we cite it**: E5-Mistral-7B is our second committee observer; this is the methodological citation for it.

### D4. EmbeddingGemma (2025) — alternative observer / candidate held-out
- **Reference**: Vera, H. S., et al. (2025). EmbeddingGemma: Powerful and Lightweight Text Representations. arXiv:2509.20354. (Plus the model card: https://ai.google.dev/gemma/docs/embeddinggemma/model_card.)
- **Link**: https://arxiv.org/abs/2509.20354
- **One-line**: A 300M-parameter encoder distilled from Gemma3, topping MTEB for sub-500M-parameter models with 768d outputs and Matryoshka truncation.
- **Inline form**: (Vera et al., 2025) — or "EmbeddingGemma (model card, 2025)"
- **Why we cite it**: It is one of the candidate held-out transfer encoders; readers will ask why we chose what we chose, and this anchors the alternative.

### D5. Reimers & Gurevych (2019) — Sentence-BERT (the older foundation)
- **Reference**: Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *Proceedings of EMNLP-IJCNLP 2019*, 3982–3992.
- **Link**: https://aclanthology.org/D19-1410/ (arXiv: https://arxiv.org/abs/1908.10084)
- **One-line**: Establishes the now-standard recipe of fine-tuning BERT with a Siamese contrastive objective to get semantically meaningful sentence embeddings comparable via cosine similarity.
- **Inline form**: (Reimers & Gurevych, 2019)
- **Why we cite it**: Foundational reference for "modern text embedding space"; cite once in METHOD or BACKGROUND to ground why distance in such a space is meaningful at all.

---

## E. Creativity evaluation in LLMs — the scoring half

### E1. Chakrabarty et al. (2024) — Art or Artifice / TTCW
- **Reference**: Chakrabarty, T., Laban, P., Agarwal, D., Muresan, S., & Wu, C.-S. (2024). Art or Artifice? Large Language Models and the False Promise of Creativity. In *Proceedings of the 2024 CHI Conference on Human Factors in Computing Systems (CHI '24)*.
- **Link**: https://doi.org/10.1145/3613904.3642731 (arXiv: https://arxiv.org/abs/2309.14556)
- **One-line**: Operationalizes the Torrance Test of Creative Writing (TTCW) as 14 binary expert judgments and shows LLM-written stories pass 3–10x fewer TTCW tests than New Yorker professionals.
- **Inline form**: (Chakrabarty et al., 2024)
- **Why we cite it**: This is the benchmark people in the LLM-creativity world point at for "do humans still beat models on story writing?"; we anchor our novelty-vs-creativity discussion against it.

### E2. Sun / Ismayilzada et al. (2024) — creative-short-story evaluation (60 models, 60 humans)
- **Reference**: Ismayilzada, M., Stevenson, C., & van der Plas, L. (2024). Evaluating Creative Short Story Generation in Humans and Large Language Models. arXiv:2411.02316.
- **Link**: https://arxiv.org/abs/2411.02316
- **One-line**: Benchmarks 60 LLMs against 60 humans on a 5-sentence cue-word story task, finding LLMs lag humans on novelty/surprise/diversity while non-expert raters prefer LLM output.
- **Inline form**: (Ismayilzada et al., 2024) — note: the README's "Sun et al." appears to refer to this paper; verified first author is Ismayilzada
- **Why we cite it**: The README lists this as one of the evaluations we plug our outputs into; it is also the closest prior art on automated story-creativity measurement.

### E3. Fein et al. (2025) — LitBench
- **Reference**: Fein, D., Russo, S., Xiang, V., Jolly, K., Rafailov, R., & Haber, N. (2025). LitBench: A Benchmark and Dataset for Reliable Evaluation of Creative Writing. arXiv:2507.00769.
- **Link**: https://arxiv.org/abs/2507.00769
- **One-line**: Releases the first standardized pairwise creative-writing benchmark — 2,480 human-labeled Reddit story comparisons and a 43k-pair training set — and trains a Bradley-Terry reward model on top.
- **Inline form**: (Fein et al., 2025)
- **Why we cite it**: LitBench BT scores are one of the four eval signals listed in our README; we cite it whenever we mention LitBench quality scores.

### E4. Hubert, Awa & Zabelina (2024) — "How creative is GPT-4?"
- **Reference**: Hubert, K. F., Awa, K. N., & Zabelina, D. L. (2024). The current state of artificial intelligence generative language models is more creative than humans on divergent thinking tasks. *Scientific Reports*, 14, 3440.
- **Link**: https://doi.org/10.1038/s41598-024-53303-w (https://www.nature.com/articles/s41598-024-53303-w)
- **One-line**: Compares GPT-4 against 151 humans on the Alternative Uses Task, Consequences Task, and Divergent Associations Task, finding GPT-4 more original and elaborate across measures.
- **Inline form**: (Hubert et al., 2024)
- **Why we cite it**: This is the most-cited "GPT-4 is creative on divergent-thinking tests" result; the user's brief asked for the "How Creative is GPT-4?" paper and this is the closest verified Nature/Sci-Rep version of that claim. (There is a separately titled arxiv paper "How Creative Is GPT-4?" but it is much less established; this is the canonical version of the headline.) If the user wants the literal "How Creative Is GPT-4?" paper, replace with: Franceschelli & Musolesi (2023), "On the Creativity of Large Language Models," arXiv:2304.00008.
- **Note on verifiability**: The exact title "How Creative is GPT-4?" matches multiple secondary writeups but no single canonical paper carries that title in 2024 venues; we recommend the Hubert et al. (2024) Scientific Reports paper as the strongest substitute. Also acceptable alternative: Bellemare-Pepin et al. (2024), arXiv:2411.02980 ("Divergent Creativity in Humans and Large Language Models").

### E5. Li et al. (2016) — distinct-n metric
- **Reference**: Li, J., Galley, M., Brockett, C., Gao, J., & Dolan, B. (2016). A Diversity-Promoting Objective Function for Neural Conversation Models. In *Proceedings of NAACL-HLT 2016*, 110–119.
- **Link**: https://aclanthology.org/N16-1014/ (arXiv: https://arxiv.org/abs/1510.03055)
- **One-line**: Introduces the distinct-1 / distinct-2 metric — the ratio of unique n-grams to total n-grams — as a lightweight diversity score for generated text.
- **Inline form**: (Li et al., 2016)
- **Why we cite it**: Whenever the poster reports distinct-n as a sanity-check on lexical diversity, this is the source.

---

## F. Foundation-model-guided discovery — closest related work

### F1. Kumar et al. (2024) — ASAL (the closest methodological cousin)
- **Reference**: Kumar, A., Lu, C., Kirsch, L., Tang, Y., Stanley, K. O., Isola, P., & Ha, D. (2024). Automating the Search for Artificial Life with Foundation Models. arXiv:2412.17799.
- **Link**: https://arxiv.org/abs/2412.17799
- **One-line**: Uses vision-language-model embeddings (CLIP, DINOv2) as a measure space for searching ALife simulations, with three modes: target-prompt, temporal-novelty, and illumination.
- **Inline form**: (Kumar et al., 2024)
- **Why we cite it**: ASAL is the methodological mirror of our work in a different domain (simulations of life vs. stories); it validates "use foundation-model embeddings as the novelty geometry" — exactly our move.

### F2. Faldor et al. (2024) — OMNI-EPIC
- **Reference**: Faldor, M., Zhang, J., Cully, A., & Clune, J. (2024). OMNI-EPIC: Open-endedness via Models of human Notions of Interestingness with Environments Programmed in Code. arXiv:2405.15568. (Also: ICLR 2025.)
- **Link**: https://arxiv.org/abs/2405.15568
- **One-line**: Uses LLMs both to generate new RL environments as code and to judge which are interesting, combining foundation-model evaluation with procedural environment generation.
- **Inline form**: (Faldor et al., 2024)
- **Why we cite it**: An example of "foundation models judging foundation-model-generated artifacts," structurally similar to our coherence and quality gates around the search.

### F3. Zhang et al. (2023) — OMNI
- **Reference**: Zhang, J., Lehman, J., Stanley, K. O., & Clune, J. (2023). OMNI: Open-endedness via Models of human Notions of Interestingness. arXiv:2306.01711. (Also: NeurIPS 2023.)
- **Link**: https://arxiv.org/abs/2306.01711
- **One-line**: Proposes using LLMs as a model of what humans find "interesting," letting open-ended learning systems prioritize tasks that are both learnable and worth doing.
- **Inline form**: (Zhang et al., 2023)
- **Why we cite it**: Cited alongside ASAL/OMNI-EPIC as part of the lineage of FM-judged discovery; useful in CAVEATS/Future Work when contrasting our distance-based novelty against LLM-judged "interestingness."

---

## G. The image-domain self-citation

### G1. Oberoi (2025/2026) — DURooM (image-domain precursor)
- **Reference**: Oberoi, A. (2026). DURooM: Discovering Unexplored Regions On/Off the Manifold — Novelty search in foundation-model embedding space for visual artifacts. Manuscript / project paper; image-domain precursor to the present work. (Reference: WikiArt experiments at `<REPO_ROOT_OLD>/extra/paper_sections/`.)
- **Inline form**: (Oberoi, 2026) or "image-domain version of this work, Oberoi 2026"
- **One-line**: Image-domain instantiation of the same framework: CMA-ES novelty search in SCFlow's 768d style space over WikiArt (173,337 artworks), with CLIP + DINOv3 committee observers and SigLIP held out.
- **Why we cite it**: This is the prior work whose technical machinery we port to text; the headline result we carry over is held-out Spearman rho between 0.34 and 0.63 across metrics, which establishes that the embedding-novelty signal transfers across architecturally distinct encoders. (Note: the user's brief referenced "Frontier-Euclidean rho = 0.629"; this matches the upper end of the rho = 0.34–0.63 range reported in the image-domain abstract.)
- **Verifiability note**: Not yet a public preprint at the time of citation set assembly; treat as in-prep self-cite. If a public arxiv ID is assigned before poster print, swap in.

---

## H. Held-out-encoder transfer evaluation — the theoretical hook

### H1. Huh et al. (2024) — The Platonic Representation Hypothesis
- **Reference**: Huh, M., Cheung, B., Wang, T., & Isola, P. (2024). The Platonic Representation Hypothesis. In *Proceedings of the 41st International Conference on Machine Learning (ICML 2024)*.
- **Link**: https://arxiv.org/abs/2405.07987 (proceedings: https://proceedings.mlr.press/v235/huh24a.html)
- **One-line**: Argues — with empirical evidence across vision and language — that as foundation models grow, their representational geometries converge toward a shared, modality-agnostic statistical structure.
- **Inline form**: (Huh et al., 2024)
- **Why we cite it**: Our transfer claim ("novelty discovered in Qwen3-Embedding still ranks as novel under BGE / E5-Mistral / held-out encoder") only makes sense if encoder geometries are non-trivially aligned. Huh et al. give us the theoretical license to expect that alignment.

---

## Where each citation goes — section map

| Citation | Section in poster |
|---|---|
| Lehman & Stanley 2008 (B1) | INTRO (lineage) — single line |
| Lehman & Stanley 2011 (B2) | INTRO + METHOD (k-NN sparseness formula) |
| Mouret & Clune 2015 (C1) | INTRO (lineage), brief METHOD contrast |
| Cully & Demiris 2018 (C2) | INTRO (one "the QD field" reference) |
| Hansen & Ostermeier 2001 (A1) | METHOD (CMA-ES origin) |
| Hansen 2016 (A2) | METHOD (implementation reference) |
| Ros & Hansen 2008 (A3) | METHOD (sep-CMA-ES; 768d justification) |
| Zhang et al. 2025 / Qwen3 (D1) | METHOD (search space) |
| Xiao et al. 2024 / BGE (D2) | METHOD (committee observers) |
| Wang et al. 2024 / E5-Mistral (D3) | METHOD (committee observers) |
| EmbeddingGemma 2025 (D4) | METHOD or CAVEATS (alt observer) |
| Reimers & Gurevych 2019 (D5) | METHOD or BACKGROUND (one-line foundation) |
| Chakrabarty et al. 2024 (E1) | BACKGROUND (creativity scoring landscape) |
| Ismayilzada et al. 2024 (E2) | BACKGROUND + RESULTS (used as eval) |
| Fein et al. 2025 / LitBench (E3) | RESULTS (BT-score eval) |
| Hubert et al. 2024 (E4) | BACKGROUND (prior LLM-creativity numbers) |
| Li et al. 2016 / distinct-n (E5) | RESULTS (distinct-n metric) |
| Kumar et al. 2024 / ASAL (F1) | INTRO or CAVEATS (closest related work) |
| Faldor et al. 2024 / OMNI-EPIC (F2) | CAVEATS / Future Work |
| Zhang et al. 2023 / OMNI (F3) | CAVEATS / Future Work |
| Oberoi 2026 / DURooM (G1) | INTRO + TRANSFER section (self-cite for image-domain precedent) |
| Huh et al. 2024 / Platonic (H1) | TRANSFER section |

---

## Bonus: prior numbers to cite as comparison context

These are concrete numerical results from the cited papers that can be surfaced inside our results section ("for context: prior work reports X on related task Y").

### From Chakrabarty et al. 2024 (TTCW — Art or Artifice)
- Overall TTCW pass rate: New Yorker professionals 84.7%, Claude v1.3 30.0%, GPT-4 27.9%, GPT-3.5 8.7%.
- By Torrance dimension, GPT-4 vs human New Yorker writers:
  - Fluency: 38.9% vs 91.4%
  - Flexibility: 18.5% vs 84.3%
  - Originality: 24.0% vs 76.9%
  - Elaboration: 23.2% vs 81.4%
- Bottom line for the poster: even on the most LLM-favorable dimension (Originality), GPT-4 passes about 1/3 as often as professional writers. Our novelty signal lives in this gap.

### From Ismayilzada et al. 2024 (5-sentence story task, 60 LLMs vs 60 humans)
- Mean creativity rating (5-point Likert):
  - Expert raters: humans 3.58 (sd 0.78), LLMs 2.33 (sd 0.55).
  - Non-expert raters: humans 2.45 (sd 0.77), LLMs 3.65 (sd 0.78).
  - LLM-as-judge: humans 2.41 (sd 0.70), LLMs 4.26 (sd 0.64).
- Turing-test identification accuracy: experts 94%, non-experts 81%, LLM judges 71%.
- Bottom line: humans are still more novel/diverse on automated metrics and expert ratings; LLM judges and lay readers are systematically fooled. Our LitBench-BT and Gemma-judge evals inherit this caveat.

### From Hubert, Awa & Zabelina 2024 (divergent-thinking tests)
- On the Alternative Uses Task, Consequences Task, and Divergent Associations Task, GPT-4 was rated more original and more elaborate than 151 human participants, controlling for fluency.
- A follow-up by Cropley et al. (2025) on the same DAT/AUT: only 0.28% of LLM responses reached the top-10% human creativity bracket — i.e. LLMs are above-average but virtually never produce top-tier creative responses. (arXiv:2504.12320)
- Bottom line for the poster: divergent-thinking-test "creativity" of GPT-class models is real but bounded — they win on means and lose on tails. We exploit this by searching the tails of their own embedding space.

### From LitBench (Fein et al. 2025)
- Best off-the-shelf zero-shot judge: Claude-3.7-Sonnet, 73% agreement with human pairwise preferences.
- BT reward model trained on 43,827 paired preferences, evaluated on 2,480 held-out pairs.
- Bottom line: any reward-model story score has an error floor of ~27% disagreement with humans. We should report our BT scores with that ceiling in mind.

### From the image-domain precursor (Oberoi 2026, DURooM)
- Held-out SigLIP-SO400M Spearman rho range: 0.34–0.63 across distance-metric conditions, with the strongest transfer in the Frontier-Euclidean condition (rho ~ 0.63).
- Archive sizes: Mahalanobis 37 artifacts (tight, on-manifold), Cosine 89, Euclidean 168, Frontier-Euclidean 525.
- Coherence-gate threshold tau = 0.6 on SigLIP image-text similarity.
- Bottom line: same framework, different domain — these are the numbers our text-domain transfer-rho should be benchmarked against.

---

## Sources verified during research

- [Hansen 2016 Tutorial — arxiv 1604.00772](https://arxiv.org/abs/1604.00772)
- [Hansen & Ostermeier 2001 — MIT Press](https://direct.mit.edu/evco/article/9/2/159/892/Completely-Derandomized-Self-Adaptation-in)
- [Ros & Hansen 2008 sep-CMA-ES — HAL](https://inria.hal.science/inria-00287367/document)
- [Lehman & Stanley 2011 — MIT Press](https://direct.mit.edu/evco/article-abstract/19/2/189/1365/Abandoning-Objectives-Evolution-Through-the-Search)
- [Mouret & Clune 2015 — arxiv 1504.04909](https://arxiv.org/abs/1504.04909)
- [Cully & Demiris 2018 — IEEE Xplore](https://ieeexplore.ieee.org/document/7959075/)
- [Qwen3 Embedding — arxiv 2506.05176](https://arxiv.org/abs/2506.05176)
- [BGE / C-Pack — arxiv 2309.07597 / SIGIR 2024](https://dl.acm.org/doi/10.1145/3626772.3657878)
- [E5-Mistral — arxiv 2401.00368](https://arxiv.org/abs/2401.00368)
- [EmbeddingGemma — arxiv 2509.20354](https://arxiv.org/abs/2509.20354)
- [Sentence-BERT — ACL Anthology](https://aclanthology.org/D19-1410/)
- [Art or Artifice (TTCW) — arxiv 2309.14556 / CHI 2024](https://dl.acm.org/doi/10.1145/3613904.3642731)
- [Ismayilzada et al. 2024 — arxiv 2411.02316](https://arxiv.org/abs/2411.02316)
- [LitBench — arxiv 2507.00769](https://arxiv.org/abs/2507.00769)
- [Hubert et al. 2024 — Scientific Reports](https://www.nature.com/articles/s41598-024-53303-w)
- [Li et al. 2016 distinct-n — ACL Anthology](https://aclanthology.org/N16-1014/)
- [ASAL — arxiv 2412.17799](https://arxiv.org/abs/2412.17799)
- [OMNI-EPIC — arxiv 2405.15568](https://arxiv.org/abs/2405.15568)
- [OMNI — arxiv 2306.01711](https://arxiv.org/abs/2306.01711)
- [Platonic Representation Hypothesis — arxiv 2405.07987](https://arxiv.org/abs/2405.07987)
