#!/usr/bin/env python3
"""Recover the still-missing character cards from the JudgesBook by OCR, matching ONLY
against the small set of missing names with a looser cutoff (low false-positive risk)."""
import fitz, re, json, io, os, difflib
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
ocr = RapidOCR()

def norm(s): return re.sub(r'[^A-Z0-9]', '', s.upper())
def slug(s): return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

d = json.loads(re.search(r'const DATA = (\{.*?\});\n', open('app.src.html').read(), re.S).group(1))
have = set(json.load(open('cards/_manifest.json')).keys())
gearset = {g['name'] for fac, lst in d.get('gear', {}).items() for g in lst}
allnames = [c['name'] for fac, lst in d.get('characters', {}).items() for c in lst] + [g['name'] for g in d.get('mercs', [])]
missing = {norm(n): n for n in allnames if slug(n) not in have}
keys = list(missing)
print('missing char targets:', len(keys))

def title_lines(img):
    res, _ = ocr(img)
    if not res: return []
    W, H = img.size
    cand = [(b[0][1], b[0][0], t) for b, t, c in res if b[0][1] < 0.30 * H and b[0][0] < 0.62 * W]
    cand.sort()
    if not cand: return []
    lines, cur = [], [cand[0]]
    for y, x, t in cand[1:]:
        if y - cur[-1][0] <= 26: cur.append((y, x, t))
        else: lines.append(cur); cur = [(y, x, t)]
    lines.append(cur)
    return [' '.join(p[2] for p in sorted(l, key=lambda z: z[1])) for l in lines]

def match(lines):
    for t in ([lines[0]] + ([lines[0] + ' ' + lines[1]] if len(lines) >= 2 else []) if lines else []):
        k = norm(t)
        if not k: continue
        if k in missing: return missing[k], 1.0
        c = difflib.get_close_matches(k, keys, n=1, cutoff=0.74)
        if c: return missing[c[0]], round(difflib.SequenceMatcher(None, k, c[0]).ratio(), 2)
    return None, 0

doc = fitz.open('JudgesBook_V1 (4).pdf')
manifest = json.load(open('cards/_manifest.json'))
best = {}
seen = set()
for pi in range(len(doc)):
    for im in doc[pi].get_images(full=True):
        dd = doc.extract_image(im[0]); w, h = dd['width'], dd['height']
        if w < 250 or h < 250 or w > 2000 or h > 2000: continue
        if not (0.6 < w / h < 0.8): continue          # portrait char cards only
        import hashlib
        md5 = hashlib.md5(dd['image']).hexdigest()
        if md5 in seen: continue
        seen.add(md5)
        img = Image.open(io.BytesIO(dd['image'])).convert('RGB')
        nm, sc = match(title_lines(img))
        if not nm: continue
        area = w * h
        if nm not in best or area > best[nm][1]:
            best[nm] = (sc, area, img)
    if (pi + 1) % 20 == 0: print(f'...page {pi+1}  found {len(best)}')

for nm, (sc, area, img) in best.items():
    s = slug(nm); w, h = img.size
    scale = min(1.0, 640 / max(w, h))
    if scale < 1.0: img = img.resize((round(w*scale), round(h*scale)), Image.LANCZOS)
    img.save(f'cards/{s}.jpg', quality=84, optimize=True)
    manifest[s] = nm
    print('  +', nm, '(score', sc, ')')
json.dump(manifest, open('cards/_manifest.json', 'w'), indent=0, sort_keys=True)
print(f'\nrecovered {len(best)} of {len(keys)}; total {len(manifest)}')
