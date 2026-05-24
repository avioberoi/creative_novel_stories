"""Inline JSON data blocks into umap_explorer.html for a self-contained file."""
import json, re, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = str(HERE / 'umap_explorer.html')
DATA = str(HERE / 'data')

files = {
    'corpus-xy':       'corpus_xy.json',
    'corpus-titles':   'corpus_titles.json',
    'archive-mahalanobis': 'archive_mahalanobis.json',
    'archive-euclidean':   'archive_euclidean.json',
    'archive-cosine':      'archive_cosine.json',
    'archive-lof':         'archive_lof.json',
    'archive-diffusion':   'archive_diffusion.json',
}

blocks = []
for tag, fn in files.items():
    with open(os.path.join(DATA, fn)) as f:
        # round-trip to compact JSON (no spaces) to keep file smaller
        d = json.load(f)
    blocks.append(f'<script id="{tag}" type="application/json">{json.dumps(d, separators=(",",":"))}</script>')

block_text = '\n'.join(blocks)
marker = '<!-- INLINE_DATA -->'

html = open(HTML).read()
# remove any previously inlined block (between two markers) and any leftover scripts
html = re.sub(r'<!-- INLINE_DATA_START -->.*?<!-- INLINE_DATA_END -->',
              '<!-- INLINE_DATA -->', html, flags=re.DOTALL)

wrapped = f'<!-- INLINE_DATA_START -->\n{block_text}\n<!-- INLINE_DATA_END -->'
if marker in html:
    html = html.replace(marker, wrapped)
else:
    # insert just before </body>
    html = html.replace('</body>', wrapped + '\n</body>')

with open(HTML, 'w') as f:
    f.write(html)
print(f'inlined {len(blocks)} blocks, total size {sum(len(b) for b in blocks)//1024} KB')
