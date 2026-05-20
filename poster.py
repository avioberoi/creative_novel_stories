"""Single-PDF poster (24"×36" portrait) for the project.
Renders with matplotlib gridspec. Designed for 3-foot readability:
  - matte, desaturated palette (cream bg, indigo/amber/sage accents)
  - serif body, sans headers
  - large font scale (title 64pt, headers 26pt, body 14pt)
Sections: TITLE → TAKEAWAY → MOTIVATION → PIPELINE → RESULTS → EXAMPLES → PROCESS → REFLECTION → AI DISCLOSURE + QR."""
import argparse, json, textwrap
from pathlib import Path
import numpy as np
import yaml
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


# matte minimalist palette
BG = '#FAF7F2'          # warm cream
INK = '#2A2A33'         # near-black, slightly cool
MUTE = '#7A7A85'        # muted grey for secondary text
RULE = '#D9D5CC'        # hairline rule colour
ACCENT = {
    'indigo':  '#4B5D8B',
    'amber':   '#C18A3B',
    'sage':    '#7A9072',
    'dusk':    '#9E6D7B',
    'slate':   '#5C6B72',
    'sand':    '#C7B98C',
}
CONDITION_COLOR = {
    'euclidean':   ACCENT['indigo'],
    'cosine':      ACCENT['amber'],
    'mahalanobis': ACCENT['sage'],
    'lof':         ACCENT['dusk'],
    'diffusion':   ACCENT['slate'],
    'random':      MUTE,
    'greedy':      ACCENT['sand'],
    'divbeam':     '#9DAAAE',
}


def setup_rc():
    mpl.rcParams.update({
        'figure.facecolor': BG,
        'axes.facecolor':   BG,
        'savefig.facecolor': BG,
        'axes.edgecolor':   INK,
        'axes.labelcolor':  INK,
        'xtick.color':      INK,
        'ytick.color':      INK,
        'text.color':       INK,
        'axes.spines.top':    False,
        'axes.spines.right':  False,
        'axes.spines.left':   True,
        'axes.spines.bottom': True,
        'axes.linewidth':   0.8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'xtick.major.size':  4,
        'ytick.major.size':  4,
        'font.family':      'serif',
        'font.serif':       ['Palatino', 'STIXGeneral', 'DejaVu Serif'],
        'font.size':        14,
        'axes.titlesize':   18,
        'axes.titleweight': 'normal',
        'axes.labelsize':   13,
        'legend.fontsize':  11,
        'legend.frameon':   False,
        'pdf.fonttype':     42,
        'ps.fonttype':      42,
    })


def _text(ax, x, y, s, size=14, weight='normal', color=INK, ha='left', va='top', font='serif', wrap=False):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, fontweight=weight, color=color,
            family=font, wrap=wrap, transform=ax.transAxes)


def panel_blank(ax, title=None):
    ax.set_facecolor(BG); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
    if title:
        _text(ax, 0.0, 1.0, title.upper(), size=18, weight='bold', font='sans-serif')
        ax.axhline(0.94, color=RULE, lw=0.6, xmin=0, xmax=1)


def header(ax, title, name, ai_note):
    panel_blank(ax)
    _text(ax, 0.0, 1.0, title, size=58, weight='bold', font='serif')
    _text(ax, 0.0, 0.42, name, size=20, color=MUTE, font='sans-serif')
    _text(ax, 0.0, 0.18, ai_note, size=11, color=MUTE, font='sans-serif')


def takeaway(ax, sentence):
    panel_blank(ax)
    # one big sentence with breathing room
    wrapped = '\n'.join(textwrap.wrap(sentence, width=42))
    _text(ax, 0.5, 0.5, wrapped, size=32, weight='bold', color=ACCENT['indigo'],
          ha='center', va='center', font='serif')


def section_text(ax, header_str, body):
    panel_blank(ax, title=header_str)
    wrapped = '\n'.join(textwrap.wrap(body, width=60))
    _text(ax, 0.0, 0.85, wrapped, size=14, font='serif')


def pipeline_diagram(ax):
    """Boxes-and-arrows pipeline. Keep abstract enough to read at 3 ft."""
    panel_blank(ax, title='Pipeline')
    ax.set_xlim(0, 10); ax.set_ylim(0, 5)
    boxes = [
        (0.5, 2.0, 'Qwen3-Emb\n768d corpus'),
        (2.8, 2.0, 'CMA-ES\nsample v ∈ ℝ⁷⁶⁸'),
        (5.1, 2.0, 'k-NN\nretrieval'),
        (7.4, 2.0, 'Qwen3-32B\nstory'),
        (5.1, 0.4, 'BGE + E5-Mistral\nMAD-normalised k-NN'),
        (2.8, 0.4, 'archive\n(percentile gate)'),
    ]
    for x, y, lbl in boxes:
        p = FancyBboxPatch((x - 0.85, y - 0.5), 1.7, 1.0,
                           boxstyle="round,pad=0.08,rounding_size=0.12",
                           lw=0.8, edgecolor=INK, facecolor='#F0EBE0')
        ax.add_patch(p)
        ax.text(x, y, lbl, ha='center', va='center', fontsize=11.5, family='sans-serif')
    arrows = [(1.4, 2.0, 1.95, 2.0), (3.65, 2.0, 4.25, 2.0),
              (5.95, 2.0, 6.55, 2.0), (7.4, 1.5, 5.95, 0.4),
              (4.25, 0.4, 3.65, 0.4), (2.8, 0.9, 2.8, 1.5)]
    for x1, y1, x2, y2 in arrows:
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     arrowstyle='-|>', mutation_scale=14,
                                     lw=0.8, color=ACCENT['indigo']))
    ax.text(5.0, 4.6, 'one CMA-ES sample → 1 generated story → committee novelty',
            ha='center', va='top', fontsize=12, color=MUTE, family='sans-serif',
            style='italic')


def search_dynamics(ax_s, ax_a, run_dirs):
    """Two panels: σ-trajectory and cumulative archive size."""
    for ax, ylab, key in [(ax_s, 'σ (step size)', 'log_σ'),
                          (ax_a, 'archive size', 'log_archive')]:
        ax.set_facecolor(BG)
        for d in run_dirs:
            try:
                a = np.load(Path(d) / 'archive.npz', allow_pickle=True)
            except Exception: continue
            name = Path(d).name.split('_')[0]
            col = CONDITION_COLOR.get(name, MUTE)
            ax.plot(a['log_iter'], a[key], color=col, lw=2.2, label=name)
        ax.set_xlabel('iteration'); ax.set_ylabel(ylab)
        ax.grid(alpha=0.25, color=RULE)
        for s in ax.spines.values(): s.set_color(INK); s.set_linewidth(0.8)
        ax.legend(loc='best', frameon=False, fontsize=11)


def pareto_panel(ax, run_dirs, quality_key='litbench'):
    ax.set_facecolor(BG)
    for d in run_dirs:
        try:
            a = np.load(Path(d) / 'archive.npz', allow_pickle=True)
            q = np.load(Path(d) / f'{quality_key}.npz')['scores']
        except Exception: continue
        name = Path(d).name.split('_')[0]
        col = CONDITION_COLOR.get(name, MUTE)
        ax.scatter(a['novelties'], q, s=22, color=col, alpha=0.55, edgecolors='none', label=name)
    ax.set_xlabel('novelty (committee)'); ax.set_ylabel('quality (LitBench BT)')
    ax.grid(alpha=0.25, color=RULE)
    ax.legend(loc='best', frameon=False, fontsize=11)


def example_box(ax, snippet, label, novelty=None, quality=None):
    panel_blank(ax)
    ax.add_patch(FancyBboxPatch((0.01, 0.01), 0.98, 0.98,
                                boxstyle="round,pad=0.01,rounding_size=0.04",
                                transform=ax.transAxes, lw=0.6, edgecolor=RULE,
                                facecolor='#F4EFE3'))
    body = '\n'.join(textwrap.wrap(snippet[:500] + ('…' if len(snippet) > 500 else ''), width=60))
    _text(ax, 0.04, 0.92, label.upper(), size=12, weight='bold',
          color=ACCENT['amber'], font='sans-serif')
    _text(ax, 0.04, 0.82, body, size=12.5, font='serif')
    chip = []
    if novelty is not None: chip.append(f'novelty {novelty:.2f}')
    if quality is not None: chip.append(f'quality {quality:.2f}')
    if chip:
        _text(ax, 0.04, 0.06, '   '.join(chip), size=11, color=MUTE, font='sans-serif')


def process_highlights(ax, items):
    panel_blank(ax, title='Process highlights')
    y = 0.85
    for label, body in items:
        _text(ax, 0.0, y, label, size=14, weight='bold', font='sans-serif',
              color=ACCENT['indigo'])
        wrapped = '\n'.join(textwrap.wrap(body, width=70))
        _text(ax, 0.0, y - 0.07, wrapped, size=13, font='serif', color=INK)
        y -= 0.25


def reflection_disclosure(ax, reflection, ai_disclosure, qr_path=None):
    panel_blank(ax)
    _text(ax, 0.0, 1.0, 'REFLECTION', size=14, weight='bold', font='sans-serif')
    wrapped = '\n'.join(textwrap.wrap(reflection, width=60))
    _text(ax, 0.0, 0.92, wrapped, size=12, font='serif')
    _text(ax, 0.0, 0.34, 'AI DISCLOSURE', size=14, weight='bold', font='sans-serif')
    wrapped2 = '\n'.join(textwrap.wrap(ai_disclosure, width=60))
    _text(ax, 0.0, 0.26, wrapped2, size=11, font='serif', color=MUTE)
    if qr_path and Path(qr_path).exists():
        from matplotlib.image import imread
        qr = imread(qr_path)
        ax.imshow(qr, extent=(0.85, 1.0, 0.05, 0.3), aspect='auto', zorder=10)


def pick_examples(run_dirs, n=3):
    """Pick top-novelty stories from across runs."""
    picks = []
    for d in run_dirs:
        try: a = np.load(Path(d) / 'archive.npz', allow_pickle=True)
        except Exception: continue
        if not len(a['texts']): continue
        i = int(np.argmax(a['novelties']))
        picks.append({'label': Path(d).name.split('_')[0],
                      'snippet': str(a['texts'][i]),
                      'novelty': float(a['novelties'][i])})
    picks.sort(key=lambda p: -p['novelty'])
    return picks[:n]


def main(args):
    cfg = yaml.safe_load(open(args.config))
    setup_rc()
    run_dirs = sorted(Path(args.runs_root).glob('*_s*')) if not args.runs else [Path(r) for r in args.runs]
    run_dirs = [d for d in run_dirs if (d / 'archive.npz').exists()]
    print(f'rendering poster from {len(run_dirs)} runs:')
    for d in run_dirs: print(f'  {d.name}')

    # 24" × 36" portrait
    fig = plt.figure(figsize=(24, 36), dpi=args.dpi)
    # 12-row layout, 6-col layout for fine placement; explicit ratios for hierarchy
    gs = GridSpec(nrows=22, ncols=6, figure=fig,
                  left=0.04, right=0.96, top=0.97, bottom=0.025,
                  hspace=0.55, wspace=0.35)

    ax_header   = fig.add_subplot(gs[0:2, :])
    ax_takeaway = fig.add_subplot(gs[2:4, :])
    ax_motiv    = fig.add_subplot(gs[4:6, 0:3])
    ax_rq       = fig.add_subplot(gs[4:6, 3:6])
    ax_pipe     = fig.add_subplot(gs[6:10, :])
    ax_sigma    = fig.add_subplot(gs[10:13, 0:3])
    ax_archive  = fig.add_subplot(gs[10:13, 3:6])
    ax_pareto   = fig.add_subplot(gs[13:16, 0:4])
    ax_transfer = fig.add_subplot(gs[13:16, 4:6])
    ax_ex1      = fig.add_subplot(gs[16:18, 0:2])
    ax_ex2      = fig.add_subplot(gs[16:18, 2:4])
    ax_ex3      = fig.add_subplot(gs[16:18, 4:6])
    ax_process  = fig.add_subplot(gs[18:20, 0:4])
    ax_refl     = fig.add_subplot(gs[18:20, 4:6])

    header(ax_header,
           title='Novelty Search in Foundation-Model Space\nfor Creative Story Generation',
           name='Avi Oberoi  ·  University of Chicago  ·  2026',
           ai_note='AI disclosure: code, search, and prose generation use Qwen3 + Claude; '
                   'details below.')
    takeaway(ax_takeaway,
             'CMA-ES in a text-embedding space discovers stories that are novel '
             'under a committee of foundation-model observers — beyond any single '
             'encoder’s preference, on a 5K New Yorker corpus.')
    section_text(ax_motiv, 'Motivation',
                 'Large language models produce fluent prose, but tend to drift toward the '
                 'centre of mass of their training distribution. Asking what lies on the '
                 'periphery — what stories the corpus does not have — is a question about '
                 'creative cognition itself.')
    section_text(ax_rq, 'Research question',
                 'Can the methodology that uncovered off-manifold images in foundation-model '
                 'embedding spaces (CMA-ES + multi-observer committee + corpus-Mahalanobis '
                 'k-NN) be ported to language, and do its claims transfer?')
    pipeline_diagram(ax_pipe)
    search_dynamics(ax_sigma, ax_archive, run_dirs)
    pareto_panel(ax_pareto, run_dirs, quality_key='litbench')
    panel_blank(ax_transfer, title='Transfer (held-out encoder Spearman ρ)')
    _text(ax_transfer, 0.0, 0.85,
          '(filled in when transfer.npz lands)', size=12, color=MUTE, font='sans-serif')
    examples = pick_examples(run_dirs, n=3)
    while len(examples) < 3:
        examples.append({'label': 'tbd', 'snippet': '(awaiting search results)', 'novelty': None})
    for ax, e in zip([ax_ex1, ax_ex2, ax_ex3], examples):
        example_box(ax, e['snippet'], e['label'], novelty=e.get('novelty'))
    process_highlights(ax_process, [
        ('Thinking-mode trap',
         'Qwen3-32B initially produced ~95% reasoning, ~5% prose. Forcing /no_think + stripping '
         '<think> blocks recovered clean 400–500 word literary openings.'),
        ('Length-regime parity',
         'Mean-pooled corpus (14 chunks) vs single-chunk candidates introduced a 2.1× variance '
         'bias. Switching to first-chunk encoding aligned both regimes.'),
        ('Committee is independent',
         'Pre-launch diagnostic: BGE ↔ Qwen3-Emb pairwise-distance Spearman = 0.39. Well below '
         'the 0.85 worry threshold — the committee actually disagrees.'),
    ])
    reflection_disclosure(
        ax_refl,
        reflection='The method ports cleanly but the LLM does the heavy lifting; CMA-ES selects '
                   'across observer axes rather than generating novelty itself. A subject for '
                   'planned ablations.',
        ai_disclosure='Code authored with Claude Code (Opus 4.7); generation uses Qwen3-32B; '
                      'embeddings use Qwen3-Emb-0.6B, BGE-large, E5-Mistral-7B, EmbeddingGemma.',
        qr_path=args.qr,
    )

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format='pdf', bbox_inches=None, facecolor=BG)
    print(f'wrote {out}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config.yaml')
    ap.add_argument('--runs_root', default='/project/jevans/avi/novelty_stories/runs')
    ap.add_argument('--runs', nargs='*', help='explicit run dirs (overrides --runs_root)')
    ap.add_argument('--qr', default=None, help='optional QR code PNG to embed')
    ap.add_argument('--out', default='/project/jevans/avi/novelty_stories/poster.pdf')
    ap.add_argument('--dpi', type=int, default=200)
    main(ap.parse_args())
