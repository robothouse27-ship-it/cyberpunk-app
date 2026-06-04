#!/usr/bin/env python3
"""Extract PROGRAM cards from the Data Fortress Omnibus program gallery (pp.240-250).
Programs are double-sided cards shown as a pair (Launch side + Running side), 2 cols x 3
rows, caption at the pair's bottom-left. Anchor on the caption (text layer) and crop the
pair. Keyed by name-slug."""
import fitz, re, json, io, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

def norm(s): return re.sub(r'[^A-Z0-9]', '', s.upper())
def slug(s): return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

d = json.loads(re.search(r'const DATA = (\{.*?\});\n', open('app.src.html').read(), re.S).group(1))
progs = {}
for fac, lst in d.get('programs', {}).items():
    for p in lst: progs.setdefault(norm(p['name']), p['name'])

manifest = json.load(open('cards/_manifest.json'))
doc = fitz.open('Copy of Data Fortress Omnibus 24-13-11 FC.pdf')
M = fitz.Matrix(3, 3)
added = 0
for pi in range(len(doc)):
    page = doc[pi]; R = page.rect
    anchors = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            for s in l.get('spans', []):
                nm = progs.get(norm(s['text']))
                if nm and 9 <= s['size'] <= 13 and 20 <= s['bbox'][0] <= 500:
                    anchors.append((s['bbox'][0], s['bbox'][1], nm))
    if not anchors: continue
    rows = {round(y / 25) for _, y, _ in anchors}
    if len(rows) > 4:            # skip index pages
        continue
    for x0, cy, nm in anchors:
        s = slug(nm)
        if s in manifest: continue
        box = fitz.Rect(x0 - 12, cy - 182, x0 - 12 + 252, cy - 4) & R
        img = Image.open(io.BytesIO(page.get_pixmap(clip=box, matrix=M).tobytes('png'))).convert('RGB')
        w, h = img.size
        sc = min(1.0, 820 / max(w, h))
        if sc < 1.0: img = img.resize((round(w*sc), round(h*sc)), Image.LANCZOS)
        img.save(f'cards/{s}.jpg', quality=84, optimize=True)
        manifest[s] = nm
        added += 1
        print(f'  + p{pi+1} {nm}')

json.dump(manifest, open('cards/_manifest.json', 'w'), indent=0, sort_keys=True)
print(f'\nadded {added} programs; total {len(manifest)}')
