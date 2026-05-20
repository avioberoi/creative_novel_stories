# REVIEW

Two-pass investigation of `/home/aoberoi1/novelty_stories/` before push to
`github.com/avioberoi/creative_novel_stories`. Read-only — no source files modified.

---

## Pass 1 — Code review of the report website

Files reviewed:
- `/home/aoberoi1/novelty_stories/report/index.html` (741 lines)
- `/home/aoberoi1/novelty_stories/report/style.css` (259 lines)
- `/home/aoberoi1/novelty_stories/report/umap_explorer.html` (386 lines)
- `/home/aoberoi1/novelty_stories/report/build_umap_data.py` (107 lines)
- `/home/aoberoi1/novelty_stories/report/inline_data.py` (41 lines)

Data cross-checked under `/project/jevans/avi/novelty_stories/runs/{mahalanobis_s42, euclidean_s42, cosine_s42, lof_s42, diffusion_s42, baseline_random, baseline_greedy, baseline_divbeam}/` against `transfer.npz`, `litbench.npz`, `archive.npz`, `sun_metrics.json`. Corpus + observer dims cross-checked against `/project/jevans/avi/novelty_stories/embs/*.npz`.

### 1. Factual / numerical errors

The 8x6 ablation table (lines 251-322) reproduces the source data exactly to the rounding shown. Specifically:
- N counts (62/87/89/78/69/200/927/199), `spearman_rho` (rounded), LitBench mean + p90, distinct-1, distinct-2 all match `transfer.npz`, `litbench.npz`, and `sun_metrics.json` for every condition.
- Total CMA archive count = 62+87+89+78+69 = **385**.
- Total baseline count = 200+927+199 = **1326**.

Errors found:

| # | Severity | Line | Issue | Fix |
|---|----------|------|-------|-----|
| F1 | **CRITICAL** | 63, 169, 181, 735 | "768-dim Qwen3-Embedding space" / "C ⊂ R^768". Actual `qwen3_emb_nyer.npz` is **(5001, 1024)**, BGE not Qwen3 — Qwen3-Embedding-0.6B's default `get_sentence_embedding_dimension()` returns 1024 in this pipeline (verified by loading the file and by `encoders.py:40` which returns `m.get_sentence_embedding_dimension()` with no truncation). Replace `768` with `1024` everywhere it refers to the search-space dim. |
| F2 | HIGH | 730 | Pareto caption says "381 search-archive stories". Actual sum = 62+87+89+78+69 = **385**. Off by 4. Fix: "385 search-archive". |
| F3 | HIGH | 95 | Disclosure: "the corpus of 1,326 story openings is *entirely AI* output that the search procedure curated." 1326 is the baseline pool, which the search procedure did **not** curate. Search-curated = 385. Either say "1,711 total AI-generated story openings (385 curated by CMA-ES + 1,326 from naive baselines)" or just "the 385 CMA-ES archive stories". |
| F4 | LOW | 327 | Greedy LitBench "mean reward (2.000)". Actual = 1.9995. Acceptable round; cited again as "Baseline Greedy-farthest ... 2.000" in the table (correctly rounded). No change needed. |
| F5 | LOW | 63, 327 | Prose says "rank correlation 0.80" / "Mahalanobis-whitened k-NN at 0.80". Actual `spearman_rho` = 0.7990. Fine round. |
| F6 | LOW | 485 | Quoted text "μ = 1.95, p90 = 2.65" — actuals are 1.9499 and 2.6531. Fine round. |

### 2. Tone violations

The user's tone rules: no em-dashes in body prose, no "X, not Y" pivots, no throat-clearing ("the key insight", "importantly", "remarkably"), no marketing voice ("compellingly", "elegantly"), no Greek in axis labels/body prose.

| # | Severity | Line | Issue | Fix |
|---|----------|------|-------|-----|
| T1 | MEDIUM | 243, 244 | Table headers `<th>Transfer &rho;</th>`, `<th>LitBench &mu;</th>`. Greek in axis-equivalent labels (column heads). Rule says no Greek in axis labels. | Replace with "Transfer rho" and "LitBench mean" (or use `&rho;` only inside the math/algorithm block on lines 169, 181-195 which is permitted as a code-block-equivalent). |
| T2 | MEDIUM | 169 | Methods bullet body: "population &lambda; = 16 ... initial step size &sigma;<sub>0</sub> = 0.18, rank-&mu; selection ... &lambda;&times;T = 16&times;50". Greek in body prose. Borderline since this is technical methods prose and STYLE.md rule #6 permits Greek to "mirror the paper", but it conflicts with the user's tone-feedback rule. | Either keep (justify via STYLE.md) or replace with words: "population 16 ... rank-mu selection". I would keep this one — methods bullets read as algorithm description; flag for the user's call. |
| T3 | MEDIUM | 485 | Quoted self-text inside body prose: `&ldquo;our archive&rsquo;s reward distribution sits at &mu; = 1.95...&rdquo;`. Greek in quoted text-within-prose. | Replace `&mu;` with "mean" inside the quoted text. |
| T4 | LOW | umap_explorer.html:347 | Em-dash in JS-rendered user-facing string: `'\n\n[…truncated — full text in appendix]'`. This becomes user-facing prose in the panel body. | Change `—` to ` - ` or `,` inside the truncation note. |

No em-dashes found in `index.html` body prose. The three `&mdash;` hits (lines 207, 208, 223) are all inside `<pre>` quoted prompts — explicitly excluded by the user. No "X, not Y" pivots, no throat-clearing, no marketing voice detected.

### 3. Broken citations

Bibliography contains 71 distinct `<li id="ref-...">` entries.

In-text citations found in body prose, all checked against the bibliography:

| Citation in body | Matching ref id | Status |
|---|---|---|
| Itti & Baldi (2009) — line 105 | ref-itti2009bayesian | OK |
| Boden (2004) — lines 114, 118 | ref-boden2004creative | OK |
| Chakrabarty et al. (2024) — lines 109, 144, 342 | ref-chakrabarty2024art | OK |
| Ismayilzada et al. (2024) — lines 63, 109, 144, 342 | ref-ismayilzada2024evaluating | OK |
| Kumar et al. (2025) — lines 118, 149 | ref-kumar2025asal | OK |
| Chiang (2023) — line 122 | ref-chiang2023blurry | OK |
| Lehman & Stanley (2011) — line 134 | ref-lehman2011abandoning | OK |
| Mouret & Clune (2015) — line 134 | ref-mouret2015illuminating | OK |
| Fontaine et al. (2020, 2023) — line 134 | ref-fontaine2020covariance + ref-fontaine2023cmamae | OK |
| Zhang et al. (2023) [OMNI] — line 134 | ref-zhang2023omni | OK |
| Reimers & Gurevych (2019) — line 139 | ref-reimers2019sentencebert | OK |
| Wang et al. (2024) — line 139 | ref-wang2024e5mistral | OK |
| Xiao et al. (2024) — line 139 | ref-xiao2024cpack | OK |
| Huh et al. (2024) — lines 139, 544 | ref-huh2024platonic | OK |
| Fein et al. (2025) — lines 144, 482, 735 | ref-fein2025litbench | OK |
| Hansen (2016) — lines 195, 347 | ref-hansen2016cmatutorial | OK |
| DURooM (Oberoi 2026) — lines 7, 63, 118, 149, 511, 544, 549 | ref-oberoi2026 | OK |

No orphan in-text citations found.

Bibliography entries with **no in-text citation** (would normally be removed from a strict reference list, but acceptable for a "complete machine-readable bibliography" as line 558 explicitly frames it):
ref-bengio2013representation, ref-bommasani2021opportunities, ref-bradley2023quality, ref-brown2020language, ref-burda2018exploration, ref-caron2021dino, ref-cherti2023openclip, ref-clune2019ai, ref-coifman2006diffusion, ref-davis2023memory, ref-devlin2018bert, ref-faldor2024omni, ref-halko2011svd, ref-hansen2001completely, ref-hansen2003cmaes, ref-hansen2020fastcma, ref-hart1968formal, ref-hertz2022prompt, ref-hintze2019openendedness, ref-jacob2021qualitative, ref-johnson2019faiss, ref-jumper2021highly, ref-kozlowski2019geometry, ref-lecun2015deep, ref-lehman2010revising, ref-li2016diversity, ref-loshchilov2014lmcma, ref-ma2023eureka, ref-ma2025scflow, ref-meng2022sdedit, ref-needell2022embracing, ref-newell1959report, ref-oquab2023dinov2, ref-pan2021dgp, ref-pathak2017curiosity, ref-pugh2016quality, ref-qwen2024qwen25, ref-qwen2025qwen3embedding, ref-radford2021clip, ref-rombach2022latent, ref-ros2008sepcma, ref-simeoni2025dinov3, ref-stanley2015greatness, ref-stanley2017openendedness, ref-stoinski2024thingsplus, ref-tjanaka2026dms, ref-tumanyan2023plug, ref-turing1936computable, ref-vaswani2017attention, ref-wu2023goya, ref-zhai2023siglip, ref-zhang2018unreasonable, ref-zhu2016manifold.

Severity: LOW. Action: leave as-is per line 558 framing, or prune to cited-only if a stricter reference list is wanted.

| # | Severity | Line | Issue | Fix |
|---|----------|------|-------|-----|
| C1 | LOW | 118, 122 | Two `<a href="#refs">Boden (2004)</a>` and `<a href="#refs">Chiang (2023)</a>` — link only to the section anchor, not to `#ref-boden2004creative` or `#ref-chiang2023blurry`. Other in-text citations don't deep-link at all. | If deep linking is desired: convert every "Author (year)" to `<a href="#ref-...">`. Otherwise keep consistent (currently inconsistent — only two are linked, both to the section). |

### 4. HTML / accessibility issues

| # | Severity | Line | Issue | Fix |
|---|----------|------|-------|-----|
| H1 | MEDIUM | 109 | `<p><sup>&lt;10<sup>-7</sup></sup></p>` — nested `<sup>` inside `<sup>`. Renders but is semantically odd and not all parsers handle nested sup the same. | Use `p &lt; 10<sup>&minus;7</sup>` (single sup, properly negative-signed). Same for `&lt;10<sup>-3</sup>` and `&lt;10<sup>-4</sup>`. |
| H2 | LOW | 25, 711, 715, 736 | Repo URL `github.com/avioberoi/creative_novel_stories` is hardcoded in 4 places. None broken now, but a single typo could orphan them. | Keep as-is for the static site; this is a flag, not a fix. |
| H3 | LOW | all `<figure>` | Alt text present on every `<img>`. No missing alt found. Caption text via `<div class="caption">` is not announced by screen readers as figure-caption (use `<figcaption>` for semantics). | Replace `<div class="caption">` with `<figcaption>` for 11 figures. |
| H4 | LOW | 11 | `style.css` linked, no `crossorigin` or `integrity`. Acceptable for a relative same-origin stylesheet. | None. |

JS load test: `umap_explorer.html` loads Plotly from CDN (line 10), all 7 inlined JSON blocks present (`corpus-xy`, `corpus-titles`, 5 archives), `init()` reads them via `loadJSON()` with a fetch-fallback (lines 203-225). No JS error paths that block initial render.

### 5. Visual integrity

`/project/jevans/avi/novelty_stories/poster_renders/report_final.png` (1400 x 7500 px) and `report_preview.png` (1400 x 4500 px) reviewed.

| # | Severity | Section | Issue | Fix |
|---|----------|---------|-------|-----|
| V1 | LOW | Section 06 table | Table renders cleanly at preview resolution; rightmost columns (distinct-1, distinct-2) appear tight but legible. | None at the 1400px width. Verify on narrow viewport. |
| V2 | LOW | Top strip | Logo + meta strip render side-by-side cleanly. | None. |

No overflow, no broken layout, no illegible text observed at preview resolution. Single-column max-width 820px layout is conservative — unlikely to break.

### 6. Interactive UMAP correctness

`umap_explorer.html` (880 KB self-contained, lines 1-386) static walkthrough:

| # | Severity | Line | Issue | Fix |
|---|----------|------|-------|-----|
| U1 | OK | 233-237 | JSON load via `loadJSON()` reads from inline `<script type="application/json">` blocks (lines 377-383 contain the inlined data). file:// safe. | None — works. |
| U2 | OK | 295-318 | Metric chips: per-metric `addEventListener('click')` toggles `visible: 'legendonly'` via `Plotly.restyle`. Wired correctly. | None. |
| U3 | OK | 322-329 | `plotly_click` handler: extracts `customdata` `{metric, idx}` and calls `showStory(metric, idx, a)`. Corpus trace has no `customdata`, so corpus clicks silently noop (correct: user only wants archive clicks). | None. |
| U4 | MEDIUM | 347 | `[…truncated — full text in appendix]` truncation banner has an em-dash (see T4). | Change to ` - ` or `,`. |
| U5 | LOW | 88-90 | `.chip.off { color: var(--ink-2); background: var(--bg); }` — when off, chip text fades to gray but border stays light. Could be clearer. | Optional: add `border-color: var(--rule)` when off. |
| U6 | MEDIUM | inline_data.py line 22 | Inlined `corpus_titles.json` contains the **untrimmed first 80 chars of every story including raw newlines**. Look at line 378 of umap_explorer.html: `["Super Goat Man By Jonathan Lethem When Super Go...`. Titles work but are not clean titles; they are story-start substrings. Acceptable as hover labels but flag if you intended actual titles. | Either rebuild `corpus_titles.json` from authoritative titles or rename the chip / tooltip label from "title" to "opening". |
| U7 | LOW | build_umap_data.py | Writes `corpus_umap.npy` (line 35) but the inlined JSON consumer expects `corpus_xy.json` (referenced in `inline_data.py` line 8). The script does not produce `corpus_xy.json` — there is an unwritten converter step. | Add to `build_umap_data.py` after line 35: `json.dump({'xy': XY.tolist()}, open(os.path.join(OUT, 'corpus_xy.json'), 'w'))`. Reproducibility gap. |
| U8 | LOW | line 305 | Click handler does `Plotly.restyle('plot', { visible: 'legendonly' }, [traceIdx])` — `legendonly` works but no legend is shown (layout has no `showlegend`). Use `visible: false` instead, or add a legend. | Minor. |
| U9 | LOW | line 365 | "Search trajectory" subtitle says "Hover for titles, click an archive point to read the story" but no archive trajectory line is plotted, only points. The static figure (line 368 of index.html) shows a maroon line for the CMA-ES mean trajectory; that line is not present in the interactive version. | Optional: add a line trace for the CMA-ES mean. Or rephrase subtitle to "Hover any point, click an archive point". |

The UMAP loads. Filters work. Click-to-expand works. The bugs above are cosmetic, not silent-failure.

---

## Pass 2 — Repo cleanup audit

`/home/aoberoi1/novelty_stories/` is a git repo (no remote set; `cat .git/config` shows `[core]` only). Local-only at present. Total disk: ~84 MB, dominated by `report/data/corpus_umap_reducer.pkl` (70 MB derived cache).

### Top-level inventory and recommendation

| Path | Tracked? | Recommendation | Why |
|------|----------|----------------|-----|
| `README.md` | tracked | **KEEP** | Project overview, includes run sequence. |
| `STYLE.md` | tracked | **KEEP** | Code conventions ref. |
| `.gitignore` | tracked | **KEEP** but **EXTEND** (see below) | Currently only `__pycache__/`, `*.pyc`, `*.pyo`, `*.egg-info/`, `.ipynb_checkpoints/`. Misses big derived caches and `dconf` paths. |
| `config.yaml` | tracked | **KEEP** | Run config. **Note F1 above**: line 30 comment says "768d" but real qwen3 emb is 1024d — fix the comment too. |
| `baselines.py` | tracked | KEEP | Baseline implementations. |
| `coherence.py` | tracked | KEEP | Coherence gate (60 LOC budget). |
| `encoders.py` | tracked | KEEP | Encoder registry. |
| `eval.py` | tracked | KEEP | Eval pass. |
| `expand.py` | tracked | KEEP | Snippet -> full story. |
| `generator.py` | tracked | KEEP | LLM generator. |
| `novelty.py` | tracked | KEEP | CMA-ES loop. |
| `scorers.py` | tracked | KEEP | 5 distance scorers. |
| `viz.py` | tracked | KEEP | UMAP, sigma, Pareto. |
| `encode_corpus.py` | tracked | **MOVE** to `scripts/oneoff/` | "One-shot: encode NEWCORPUS_CLEANED with one encoder" — runs once per encoder, not part of the search loop. |
| `make_qr.py` | tracked | **MOVE** to `scripts/oneoff/` | Poster QR generator. Per the user's brief: belongs in `scripts/oneoff/`. |
| `pilot.py` | tracked | **MOVE** to `scripts/oneoff/` | "Pre-launch calibration" — diagnostic, not production. Per the user's brief. |
| `poster.py` | tracked | **MOVE** to `scripts/oneoff/` | 14 KB matplotlib gridspec PDF poster generator. Different file from `poster/` directory (which holds the HTML poster + figures). Per the user's brief. |
| `recon_greedy.py` | UNTRACKED | **MOVE** to `scripts/oneoff/` | "Reconstruct baseline_greedy archive.npz from the timed-out run's text files" — a one-off recovery script. Per the user's brief. |
| `__pycache__/` | ignored | **DELETE** (already gitignored, will not be pushed; can `rm -rf`) | 162 KB of `.pyc`. |
| `dconf/` | UNTRACKED | **DELETE** | Contains `dconf/user`, a 2-byte binary blob (0x0000). Accidental leak from a desktop/dconf invocation during a non-isolated process. Will not be pushed currently (untracked) but should be removed. |
| `poster/dconf/` | UNTRACKED | **DELETE** | Same — 2-byte `user` file, accidental. |
| `canvas/Peripheria.md` | tracked | **CHECK** with user | This is a "design philosophy" doc (5 KB prose poem). Not code, not data. Decide if it belongs in the public repo. It is unique and authored and may be intentional curatorial content; recommend the user confirm before deletion. |
| `Final_Draft.pdf` (in user's other working repo at `/home/aoberoi1/novelty_search`, **not in this repo**) | n/a | n/a — not under novelty_stories. | |
| `slurm/` | mostly tracked, 2 untracked | **KEEP** | All 12 sbatch + setenv.sh files are reproduction infra. |
| `poster/` | mostly tracked | **KEEP** but see below | HTML poster + figs. **Move** poster/dconf inside DELETE; poster/figs/*.npz are figure data (small, fine to keep). |
| `report/` | UNTRACKED | **KEEP** (start tracking) the `.html`, `.css`, `.py` files, `figs/`, and the small `data/*.json` and `data/*.npy` files. **GITIGNORE** the big derived pickle. | See below. |

### `report/data/` (71 MB) — granular recommendation

| File | Size | Recommendation |
|------|------|----------------|
| `archive_*.json` (5 files) | 256 KB total | KEEP — required by `umap_explorer.html`. |
| `corpus_titles.json` | 416 KB | KEEP — required by `umap_explorer.html`. |
| `corpus_xy.json` | 208 KB | KEEP — required by `umap_explorer.html`. |
| `corpus_umap.npy` | 48 KB | KEEP — required by build script reuse. |
| `references.html`, `references.json` | 51 KB | KEEP — companion bibliography. |
| `corpus_umap_reducer.pkl` | **70 MB** | **GITIGNORE** — derived cache, regeneratable by `build_umap_data.py`. Adds 70 MB to the repo for no reason. |

### `.gitignore` — proposed additions

The current `.gitignore` is 5 lines. Add:
```
# OS / desktop leaks
dconf/
**/dconf/

# Derived caches (regeneratable)
report/data/corpus_umap_reducer.pkl

# Large outputs (only if accidentally created locally)
*.log
slurm-*.out
```

### Secrets / credentials check

`grep -rE "(api[_-]?key|secret|password|token|BEGIN .*PRIVATE)"` across all `.py / .yaml / .json / .md / .html`:
- Only hits are `api_key="none"` in `generator.py:37`, `eval.py:93`, `expand.py:20` — all are placeholder values for local vLLM (which requires a non-empty string). **Safe**.
- No `.env` file. No credentials. No token files.

### Other answers from the brief

- **What is `canvas/`?** Contains a single file `Peripheria.md`, a 5 KB authored prose-poem titled "Peripheria" describing a visual-design philosophy ("the geometry of rare things"). Already tracked. Not code, not data. **Recommendation: CHECK** — verify with the user. If kept, consider moving to `docs/peripheria.md` for clarity.
- **What is `dconf`?** A 17 KB directory at the repo root containing `dconf/user`, a 2-byte binary file (`0x00 0x00`). This is a Linux dconf/gsettings artifact, almost certainly created accidentally when something invoked `dconf` from this cwd (perhaps a GTK/GIO process). Same situation in `poster/dconf/user`. **DELETE both** and gitignore `**/dconf/`.
- **What is `poster.py` vs `poster/`?** `poster.py` is a 14 KB Python script that uses matplotlib gridspec to render a 24"x36" PDF poster. The `poster/` directory contains the **HTML** poster (`index.html`, `_template.html`, `figs/`, `logos/`, `poster-config.json`) and prose notes. They are two separate poster artifacts (PDF vs HTML); both are real, both produced figures, but the project has shipped on the HTML version. Move `poster.py` to `scripts/oneoff/`.
- **What is `pilot.py`?** 16 KB. "Pre-launch calibration. CPU-only after corpus load. Diagnoses three risks: A. Encoder correlation (committee independence)..." Belongs in `scripts/oneoff/`.
- **Is there `.git/` already?** Yes. `cat .git/config` returns `[core] repositoryformatversion = 0 ...` with **no remote configured**. Five commits exist on `main` (most recent: `65b318c DiffusionScorer: adaptive bandwidth fixes OOD-query collapse (audit bug)`). The repo is local; no remote push has happened yet. Adding the remote would just be `git remote add origin git@github.com:avioberoi/creative_novel_stories.git`.
- **Credentials?** None. See "Secrets / credentials check" above.

### Cleanup script (derivable from the table above)

```bash
# Stage 1: delete junk
rm -rf /home/aoberoi1/novelty_stories/__pycache__
rm -rf /home/aoberoi1/novelty_stories/dconf
rm -rf /home/aoberoi1/novelty_stories/poster/dconf

# Stage 2: move one-offs
mkdir -p /home/aoberoi1/novelty_stories/scripts/oneoff
git mv encode_corpus.py make_qr.py pilot.py poster.py scripts/oneoff/
git mv recon_greedy.py  scripts/oneoff/   # currently untracked, plain mv

# Stage 3: extend .gitignore (see proposed block above)

# Stage 4: stage report/ (untracked currently) BUT exclude the 70 MB pickle
# (the .gitignore addition above handles this).

# Stage 5: decide on canvas/Peripheria.md (CHECK)
```

---

## Summary of must-fix before push

1. **F1 (CRITICAL)**: Fix the "768" vs "1024" dim error for the search space throughout index.html (4 occurrences) and config.yaml comment (line 30).
2. **F2 (HIGH)**: Pareto caption "381" -> "385".
3. **F3 (HIGH)**: Disclosure "1,326 story openings ... search procedure curated" is wrong; pick one of the two corrected phrasings.
4. **U4 / T4 (MEDIUM)**: em-dash in `umap_explorer.html:347` truncation banner.
5. **T1 / T3 (MEDIUM)**: Greek `rho`/`mu` in table headers (lines 243-244) and quoted body text (line 485).
6. **U6 (MEDIUM)**: corpus_titles content is opening text, not titles; rename label or rebuild.
7. **U7 (LOW)**: `build_umap_data.py` does not emit `corpus_xy.json`.
8. **DELETE**: `dconf/`, `poster/dconf/`, `__pycache__/` before push.
9. **GITIGNORE**: `corpus_umap_reducer.pkl` (70 MB) so it never gets committed.
10. **MOVE**: `encode_corpus.py`, `make_qr.py`, `pilot.py`, `poster.py`, `recon_greedy.py` to `scripts/oneoff/`.
