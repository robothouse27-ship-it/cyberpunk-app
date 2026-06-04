#!/usr/bin/env python3
"""Extract gear/cyberware card entries from the Data Fortress Omnibus gallery pages.
Cards are 'live' (vector+text): each entry = card art + faction table, with a Roboto
caption (the card name) ~115pt below the art. We anchor on the caption (text layer,
no OCR), crop the entry region, and save for any name still missing. Keyed by name-slug."""
import fitz, re, json, io, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

def norm(s): return re.sub(r'[^A-Z0-9]', '', s.upper())
def slug(s): return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

d = json.loads(re.search(r'const DATA = (\{.*?\});\n', open('app.src.html').read(), re.S).group(1))
gear_pool = {}
for fac, lst in d.get('gear', {}).items():
    for g in lst: gear_pool.setdefault(norm(g['name']), g['name'])

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
                nm = gear_pool.get(norm(s['text']))
                x0, y0 = s['bbox'][0], s['bbox'][1]
                col = (16 <= x0 <= 64) or (300 <= x0 <= 352)
                if nm and 9.5 <= s['size'] <= 11.5 and col:
                    anchors.append((x0, y0, nm))
    rows = {round(y / 20) for _, y, _ in anchors}
    if len(anchors) < 3 or len(rows) > 6:   # galleries have ~4 rows; index pages have many
        continue
    for cx, cy, nm in anchors:
        s = slug(nm)
        if s in manifest: continue
        if cy < 116: continue
        box = fitz.Rect(cx - 9, cy - 116, cx - 9 + 286, cy - 8)
        if box.x1 > R.width or box.y1 > R.height:
            box = box & R
        img = Image.open(io.BytesIO(page.get_pixmap(clip=box, matrix=M).tobytes('png'))).convert('RGB')
        w, h = img.size
        sc = min(1.0, 760 / max(w, h))
        if sc < 1.0: img = img.resize((round(w*sc), round(h*sc)), Image.LANCZOS)
        img.save(f'cards/{s}.jpg', quality=84, optimize=True)
        manifest[s] = nm
        added += 1
        print(f'  + p{pi+1} {nm}')

json.dump(manifest, open('cards/_manifest.json', 'w'), indent=0, sort_keys=True)
print(f'\nadded {added} gear from Omnibus; total {len(manifest)}')
