#!/usr/bin/env python3
"""Extract Combat Zone card faces from the JudgesBook, OCR their titles, match to
DATA names, and render matched cards to cards/<nameslug>.jpg.

Keyed by normalized NAME (not id) so every rank-tier of a character/gear shares
one card image. Run from repo root:  python3 scripts/extract_cards.py
"""
import fitz, re, json, io, difflib, hashlib, os, sys
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ocr = RapidOCR()

def norm(s): return re.sub(r'[^A-Z0-9]', '', s.upper())
def slug(s): return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

# ---- name pool from DATA (characters + mercs + gear) ----
d = json.loads(re.search(r'const DATA = (\{.*?\});\n', open('app.src.html').read(), re.S).group(1))
pool = {}   # norm(name) -> canonical name
for fac, lst in d.get('characters', {}).items():
    for c in lst: pool.setdefault(norm(c['name']), c['name'])
for g in d.get('mercs', []): pool.setdefault(norm(g['name']), g['name'])
for fac, lst in d.get('gear', {}).items():
    for g in lst: pool.setdefault(norm(g['name']), g['name'])
keys = list(pool)

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

def match_one(s):
    k = norm(s)
    if not k: return None, 0
    if k in pool: return pool[k], 1.0
    c = difflib.get_close_matches(k, keys, n=1, cutoff=0.90)   # high cutoff = no garbage
    if c: return pool[c[0]], round(difflib.SequenceMatcher(None, k, c[0]).ratio(), 2)
    return None, 0

def best(lines):
    if not lines: return None, 0
    tries = [lines[0]] + ([lines[0] + ' ' + lines[1]] if len(lines) >= 2 else [])
    b = (None, 0)
    for t in tries:
        m, sc = match_one(t)
        if sc > b[1]: b = (m, sc)
        if sc == 1.0: break
    return b

doc = fitz.open('JudgesBook_V1 (4).pdf')
seen_hash = {}      # md5 -> already processed
best_for = {}       # name -> (score, area, PIL image)
stats = dict(imgs=0, ocr=0, matched=0)
log = open('out/extract_cards.log', 'w')
def say(*a):
    print(*a); print(*a, file=log); log.flush()

for pi in range(len(doc)):
    page = doc[pi]
    for im in page.get_images(full=True):
        xref = im[0]
        dd = doc.extract_image(xref)
        w, h = dd['width'], dd['height']
        if w < 250 or h < 250 or w > 2000 or h > 2000: continue
        ar = w / h
        if not (0.6 < ar < 0.8 or 1.3 < ar < 1.6): continue
        stats['imgs'] += 1
        md5 = hashlib.md5(dd['image']).hexdigest()
        if md5 in seen_hash: continue       # skip duplicate prints of same card
        seen_hash[md5] = 1
        img = Image.open(io.BytesIO(dd['image'])).convert('RGB')
        stats['ocr'] += 1
        m, sc = best(title_lines(img))
        if not m: continue
        area = w * h
        prev = best_for.get(m)
        if prev is None or area > prev[1]:
            best_for[m] = (sc, area, img)
    if (pi + 1) % 10 == 0:
        say(f'...page {pi+1}/{len(doc)}  imgs={stats["imgs"]} ocr={stats["ocr"]} matched={len(best_for)}')

# ---- save matched cards ----
os.makedirs('cards', exist_ok=True)
manifest = {}
for name, (sc, area, img) in best_for.items():
    s = slug(name)
    w, h = img.size
    scale = min(1.0, 700 / max(w, h))
    if scale < 1.0:
        img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    out = f'cards/{s}.jpg'
    img.save(out, quality=82, optimize=True)
    manifest[s] = name
json.dump(manifest, open('cards/_manifest.json', 'w'), indent=0, sort_keys=True)
say(f'\nDONE. unique cards saved: {len(manifest)}  (of {len(pool)} data names)')
say('unmatched data names:', sorted(set(pool.values()) - set(best_for.keys()))[:40])
