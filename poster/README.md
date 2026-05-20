# Poster — Writing Beyond Imagination

A self-contained 24" × 36" portrait poster for the novelty-search-for-stories
project. Single HTML file, opens in any browser, prints to PDF at exact poster
dimensions.

## Files

- `index.html` — the poster (React via CDN, no build step)
- `poster-config.json` — exportable layout config (columns, card order, font
  scale). Edit visually in the browser, then click **Save** or **Copy Config**
  to roundtrip changes back here.
- `qr.png` — optional. If present, replaces the header QR placeholder. Generate
  with e.g.
  ```
  curl -sL -o qr.png "https://api.qrserver.com/v1/create-qr-code/?size=600x600&data=https://github.com/avioberoi/novelty_stories"
  ```
- `figs/` — optional. Drop in real PNGs to replace the placeholder figure
  boxes. The HTML references these paths:
  - `figs/f2_dynamics.png` — σ_t and archive size, per metric
  - `figs/f3_pareto.png` — novelty vs. quality scatter
  - `figs/f4_transfer.png` — held-out Spearman ρ per metric

  The pipeline diagram (`Figure 1`) is inline SVG — no PNG needed.

## Open in browser

```
open index.html                  # macOS
xdg-open index.html              # Linux
```

The page auto-scales the 610mm × 914mm poster to fit your viewport. Use
**A-/A+** to nudge global font scale; **Preview** hides the edit UI.

## Print to PDF (Chrome / Edge — most reliable)

1. Open `index.html` in Chrome.
2. **Cmd/Ctrl + P** → "Save as PDF".
3. In the print dialog:
   - **Paper size**: Custom → 610mm × 914mm (or "24x36 in" if available).
     If you can't set custom size, set **Scale = Default** and **Layout =
     Portrait**; the `@page` rule in the HTML carries the size through.
   - **Margins**: None.
   - **Background graphics**: ON.
   - **Headers and footers**: OFF.
4. Save.

For a slightly cleaner result, the Playwright route works too:

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto("file://" + __import__("os").path.abspath("index.html"))
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    page.pdf(path="poster.pdf",
             width="610mm", height="914mm",
             margin={"top":"0","right":"0","bottom":"0","left":"0"},
             print_background=True)
    b.close()
```

## Swap placeholder figures for real PNGs

Each placeholder figure card shows the path it wants. To swap:

1. Save the real figure as e.g. `figs/f3_pareto.png` (any aspect ratio — the
   CSS uses `object-fit: contain`, so it won't distort).
2. In `index.html`, find the matching card (e.g. `pareto`). Replace this:
   ```jsx
   <div className="fig-wrap placeholder">
     <div className="ph-tag">figs/f3_pareto.png</div>
     <div className="ph-cap">…caption…</div>
     <div className="ph-path">drop a PNG at <b>poster/figs/f3_pareto.png</b></div>
   </div>
   ```
   with this:
   ```jsx
   <div className="fig-wrap">
     <img src="figs/f3_pareto.png" alt="Novelty vs. quality (Pareto)" />
   </div>
   ```
3. Save & reload. No other changes needed.

## Iterate the layout visually

Open in browser, then use the toolbar (top-right):

- **Preview** — toggle edit UI on/off to see the print view
- **A- / A+** — global font scale (subtle; this poster is already calibrated)
- **Drag column dividers** (vertical blue strips) — resize columns left/right
- **Drag row dividers** (horizontal strips) — resize cards within a column
- **Click-to-swap** — click a card's diamond handle (top-right of each card),
  it turns amber; click another card's diamond to swap. Or click a dashed
  amber drop-zone to move the selected card there.
- **Save** — downloads a fresh `poster-config.json`
- **Copy Config** — copies layout JSON to clipboard (paste back here to
  persist changes as the new default)
- **Reset** — restore the baked-in defaults

Changes auto-persist to `localStorage` so a reload preserves your edits;
**Reset** clears them.

## TODOs before final print

- [ ] Drop real PNGs at `figs/f2_dynamics.png`, `figs/f3_pareto.png`,
  `figs/f4_transfer.png` when the runs finish.
- [ ] Replace placeholder QR with a real one (`qr.png`) once the public
  repo URL is finalised.
- [ ] Fill in the numeric cells of the **Distance-metric ablation** table
  with values from each `runs/<metric>_s42/archive.npz`.
- [ ] Update the story-card chips (`novelty 0.82`, `quality 0.71`, etc.)
  with real scores once LitBench BT scoring completes.

## Palette reference (Peripheria-aligned)

```
Background      #FAF7F2   cream / ivory
Ink             #2A2A33   charcoal, slightly cool
Secondary ink   #4A4A55
Tertiary text   #7A7A85   captions, eyebrows
Hairline        #D9D5CC
Indigo accent   #4B5D8B   primary accent (CMA-ES, observers, body links)
Amber accent    #C18A3B   secondary accent (LLM/generator, qualitative chip)
Sage (sparing)  #7A9072   coherence gate, held-out branch
```

Fonts (Google Fonts via CDN):

- **Crimson Pro** — display title, story prose, card headers
- **Inter** — body, table, byline
- **JetBrains Mono** — labels, eyebrows, paths, numeric columns
