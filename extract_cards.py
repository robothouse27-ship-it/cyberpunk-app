#!/usr/bin/env python3
"""Rasterize Combat Zone Omnibus card pages for vision transcription.

Cards on a character page are individual composite images (~101x142 pt) laid out
in a grid: columns = models, rows = tiers (A=Standard, B=Veteran, C=Elite).
All stats (cost, armor, skills, actions, rules, gear) live INSIDE these images;
the PDF text layer only holds names + release/errata. So we must render & read.

Usage:
  python3 extract_cards.py <pdf> <page_1based> [zoom]

Outputs to out/p<page>/:
  card_<R><C>.png        full card  (default zoom 8x)
  card_<R><C>_skills.png skill column, high zoom (18x)
  card_<R><C>_acts.png   action limiter + armor, high zoom (15x)
plus an index.txt mapping grid cells to the names from the text layer.
"""
import sys, os, fitz

def card_rects(pg):
    """Return card image rects sorted into grid order (row-major, top-to-bottom,
    left-to-right). Filters to card-sized images (~101x142 pt), excluding the
    full-page background and small logos."""
    rects = []
    for img in pg.get_images(full=True):
        for r in pg.get_image_rects(img[0]):
            w, h = r.width, r.height
            if 80 <= w <= 130 and 120 <= h <= 165:
                rects.append(r)
    # cluster rows by y0 (tolerance), then sort
    rects.sort(key=lambda r: (round(r.y0 / 50), r.x0))
    return rects

def main():
    pdf = sys.argv[1]
    page = int(sys.argv[2])          # 1-based (== printed page per the brief)
    zoom = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
    doc = fitz.open(pdf)
    pg = doc[page - 1]
    outdir = f"out/p{page}"
    os.makedirs(outdir, exist_ok=True)
    rects = card_rects(pg)
    # assign grid letters/numbers: group by row (y), order cols by x
    rows = {}
    for r in rects:
        key = round(r.y0 / 50)
        rows.setdefault(key, []).append(r)
    row_letters = "ABCDE"
    pad = 3
    index = []
    for ri, key in enumerate(sorted(rows)):
        cards = sorted(rows[key], key=lambda r: r.x0)
        for ci, r in enumerate(cards, 1):
            cell = f"{row_letters[ri]}{ci}"
            clip = fitz.Rect(r.x0-pad, r.y0-pad, r.x1+pad, r.y1+pad)
            pg.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip).save(f"{outdir}/card_{cell}.png")
            # skills column (right ~30%, top ~55%)
            sk = fitz.Rect(r.x0+72, r.y0+2, r.x1+2, r.y0+78)
            pg.get_pixmap(matrix=fitz.Matrix(18, 18), clip=sk).save(f"{outdir}/card_{cell}_skills.png")
            # action limiter + armor (left strip)
            ac = fitz.Rect(r.x0-1, r.y0+2, r.x0+24, r.y0+118)
            pg.get_pixmap(matrix=fitz.Matrix(15, 15), clip=ac).save(f"{outdir}/card_{cell}_acts.png")
            index.append(f"{cell}\tx={r.x0:.0f},y={r.y0:.0f}")
    # dump text-layer names for cross-reference
    names = [l for l in pg.get_text().splitlines()
             if l.strip() and l.strip() not in row_letters
             and not l.strip().isdigit()
             and all(k not in l for k in ("Release", "Errata", "BETA", "CHARACTERS"))]
    with open(f"{outdir}/index.txt", "w") as f:
        f.write("GRID CELLS:\n" + "\n".join(index))
        f.write("\n\nTEXT-LAYER NAMES (in reading order):\n" + "\n".join(names))
    print(f"page {page}: {len(rects)} cards -> {outdir}/  (grid {len(rows)} rows)")
    print("names:", " | ".join(names))

if __name__ == "__main__":
    main()
