# AI Attribution — Poster Footer

## Output 1 — Schema reference (aiattribution.github.io)

The AI Attribution Toolkit (https://aiattribution.github.io, Apache-2.0, Svelte/TypeScript) defines a four-dimensional disclosure schema, drawing on the CRediT contributor-role taxonomy. Each AI contribution is tagged along **(1) Proportion** of AI vs. human authorship — `EAI` Entirely AI, `PAI` Primarily AI, `HAb` Human-AI blend, `Ph` Primarily human, `Eh` Entirely human; **(2) Contribution type** — `Se` Stylistic edits, `Ce` Content edits, `Nc` New content; **(3) Initiative** — `Hin` Human-initiated, `Ain` AI-initiated; and **(4) Human review** — `R` Reviewed-and-approved, `Nr` Not reviewed. The canonical render is `[Tool name] · ABBR/ABBR/ABBR/ABBR` (one tag from each axis), optionally preceded by the toolkit's per-tag icon. Source of truth: `src/lib/models/tag-library.ts` and `src/lib/common/constants.ts` in the [aiattribution/aiattribution.github.io](https://github.com/aiattribution/aiattribution.github.io) repository.

### Per-tool mapping for this work

| Tool / Model | Role on poster | Proportion | Contribution | Initiative | Review |
|---|---|---|---|---|---|
| Claude (Opus 4.7, 1M ctx) | Author-collaborator (code, design, prose, planning) | `HAb` | `Nc` | `Hin` | `R` |
| Qwen3-32B | Generator of the ~1700 stories evaluated by the search | `EAI` | `Nc` | `Hin` | `R` |
| Qwen3-Embedding-0.6B | Search-space embedding (768d) | `Ph` | `Nc` | `Hin` | `R` |
| BGE-large-en-v1.5 | Search-time observer #1 | `Ph` | `Nc` | `Hin` | `R` |
| E5-Mistral-7B-instruct | Search-time observer #2 | `Ph` | `Nc` | `Hin` | `R` |
| EmbeddingGemma-300m | Held-out transfer encoder | `Ph` | `Nc` | `Hin` | `R` |
| ConicCat Litbench-Creative-Writing-RM-3B | LitBench Bradley-Terry quality scoring | `Ph` | `Nc` | `Hin` | `R` |

---

## Output 2 — Copy-paste JSX footer block

Drop the snippet below into the existing `<footer className="footer">…</footer>` in `index.html`. The companion CSS (also below) targets the existing footer typography (JetBrains Mono 8–9pt, `#6B7280`) and keeps the block to at most three wrapped lines.

```jsx
<div
  className="ai-attrib"
  aria-label="AI attribution per aiattribution.github.io"
>
  <span className="ai-attrib-lede">
    AI attribution (
    <a
      href="https://aiattribution.github.io"
      target="_blank"
      rel="noopener noreferrer"
    >
      aiattribution.github.io
    </a>
    ):
  </span>{" "}
  <span className="ai-item">
    Claude Opus 4.7 (1M ctx)
    <span className="tags">HAb/Nc/Hin/R</span>
    <span className="role-label">author-collaborator — code, design, prose, planning</span>
  </span>{"; "}
  <span className="ai-item">
    Qwen3-32B
    <span className="tags">EAI/Nc/Hin/R</span>
    <span className="role-label">generator — ~1,700 candidate stories</span>
  </span>{"; "}
  <span className="ai-item">
    Qwen3-Embedding-0.6B
    <span className="tags">Ph/Nc/Hin/R</span>
    <span className="role-label">search-space embedding (768d)</span>
  </span>{"; "}
  <span className="ai-item">
    BGE-large-en-v1.5
    <span className="tags">Ph/Nc/Hin/R</span>
    <span className="role-label">observer #1</span>
  </span>{"; "}
  <span className="ai-item">
    E5-Mistral-7B-instruct
    <span className="tags">Ph/Nc/Hin/R</span>
    <span className="role-label">observer #2</span>
  </span>{"; "}
  <span className="ai-item">
    EmbeddingGemma-300m
    <span className="tags">Ph/Nc/Hin/R</span>
    <span className="role-label">held-out transfer encoder</span>
  </span>{"; "}
  <span className="ai-item">
    Litbench-Creative-Writing-RM-3B
    <span className="tags">Ph/Nc/Hin/R</span>
    <span className="role-label">Bradley-Terry quality scoring</span>
  </span>
  .
</div>
```

### Companion CSS

```css
.ai-attrib {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 8.5pt;
  line-height: 1.45;
  color: #6B7280;
  max-width: 100%;
  /* keep to ~3 lines on the poster */
}
.ai-attrib .ai-attrib-lede { font-weight: 600; }
.ai-attrib a { color: inherit; text-decoration: underline dotted; }
.ai-attrib .ai-item { white-space: nowrap; }     /* prevents awkward mid-item breaks */
.ai-attrib .tags {
  margin: 0 0.35em;
  padding: 0 0.35em;
  border: 1px solid currentColor;
  border-radius: 3px;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}
.ai-attrib .role-label { font-style: italic; }
```

### Compact one-line fallback (use if the poster's footer band is single-line)

```jsx
<div className="ai-attrib">
  AI attribution (<a href="https://aiattribution.github.io">aiattribution.github.io</a>):
  Claude Opus 4.7 <span className="tags">HAb/Nc/Hin/R</span>;
  Qwen3-32B <span className="tags">EAI/Nc/Hin/R</span>;
  Qwen3-Embedding-0.6B, BGE-large-en-v1.5, E5-Mistral-7B-instruct,
  EmbeddingGemma-300m, Litbench-Creative-Writing-RM-3B
  <span className="tags">Ph/Nc/Hin/R</span>.
</div>
```

### Tag legend (optional sibling line, even smaller, for first-time readers)

```jsx
<div className="ai-attrib-legend">
  Tags: Proportion (EAI/PAI/HAb/Ph/Eh) · Contribution (Se/Ce/Nc) ·
  Initiative (Hin/Ain) · Review (R/Nr).
</div>
```

```css
.ai-attrib-legend {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 7.5pt;
  color: #9CA3AF;
  margin-top: 0.25em;
}
```
