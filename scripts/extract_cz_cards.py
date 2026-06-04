#!/usr/bin/env python3
"""Supplement card images from the dedicated CZ card PDFs (gear/leaders, vehicle mods).
These are page-per-card with a real text layer (EthnocentricRg title font), so we render
the whole front page and read the title directly. Keyed by name-slug, merged into cards/."""
import fitz, re, json, os, difflib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

def norm(s): return re.sub(r'[^A-Z0-9]', '', s.upper())
def slug(s): return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')

d = json.loads(re.search(r'const DATA = (\{.*?\});\n', open('app.src.html').read(), re.S).group(1))
pool = {}
for fac, lst in d.get('characters', {}).items():
    for c in lst: pool.setdefault(norm(c['name']), c['name'])
for g in d.get('mercs', []): pool.setdefault(norm(g['name']), g['name'])
for fac, lst in d.get('gear', {}).items():
    for g in lst: pool.setdefault(norm(g['name']), g['name'])
keys = list(pool)

def title(page):
    sp = [(s['bbox'][1], s['text'].strip()) for b in page.get_text('dict')['blocks']
          for l in b.get('lines', []) for s in l.get('spans', [])
          if 'Ethnocentric' in s['font'] and s['text'].strip()
          and not s['text'].strip().isdigit()]
    sp.sort()
    return ' '.join(t for _, t in sp).strip()

def match(t):
    k = norm(t)
    if not k: return None
    if k in pool: return pool[k]
    c = difflib.get_close_matches(k, keys, n=1, cutoff=0.88)
    return pool[c[0]] if c else None

manifest = json.load(open('cards/_manifest.json'))
added = 0
for pdf in ['CZ_GearCards_Leaders_v4.pdf', 'CZ_VehicleModsCards.pdf']:
    doc = fitz.open(pdf)
    for p in doc:
        if not p.get_text().strip(): continue          # skip card backs
        nm = match(title(p))
        if not nm: continue
        s = slug(nm)
        if s in manifest: continue                      # JudgesBook version already saved
        pix = p.get_pixmap(dpi=200)
        import io as _io
        from PIL import Image as _Img
        img = _Img.open(_io.BytesIO(pix.tobytes('png'))).convert('RGB')
        w, h = img.size
        sc = min(1.0, 800 / max(w, h))
        if sc < 1.0: img = img.resize((round(w*sc), round(h*sc)), _Img.LANCZOS)
        img.save(f'cards/{s}.jpg', quality=85, optimize=True)
        manifest[s] = nm
        added += 1
        print(f'  + {nm}  ({pdf})')
json.dump(manifest, open('cards/_manifest.json', 'w'), indent=0, sort_keys=True)
print(f'\nadded {added} from CZ PDFs; total cards now {len(manifest)}')
