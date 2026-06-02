"""Crop each program (front+back card pair) from the PROGRAMS section at high
zoom so the effect text is legible for vision transcription.

Layout (612x792 page, pp.240-250): 4 card slots/row x 3 rows; each program is a
2-card pair. Captions (name/faction/Errata) sit just below each pair:
  left captions x0~113, right captions x0~375; rows at caption-y ~256/480/703.
Crop = the card area directly above each caption.
"""
import fitz, os, re

PDF = "Copy of Data Fortress Omnibus 24-13-11 FC.pdf"
PAGES = range(240, 251)
ZOOM = 7
OUT_DIR = "out/programs/crops"

def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def captions(page):
    """Return [(name, faction, x0, name_y0)] for the 6 programs on a page."""
    d = page.get_text("dict")
    lines = []
    for b in d["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).strip()
            if txt:
                lines.append((round(l["bbox"][0]), round(l["bbox"][1]), txt))
    out = []
    for i, (x0, y0, txt) in enumerate(lines):
        if txt.startswith("Errata") and i >= 2:
            name = lines[i - 2][2]
            faction = lines[i - 1][2]
            nx0, ny0 = lines[i - 2][0], lines[i - 2][1]
            out.append((name, faction, nx0, ny0))
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = fitz.open(PDF)
    mat = fitz.Matrix(ZOOM, ZOOM)
    n = 0
    for pno in PAGES:
        page = doc[pno - 1]
        for name, faction, nx0, ny0 in captions(page):
            # The pair of cards sits just above its caption; left edge ~21pt left
            # of the caption text, pair ~216pt wide. Derive from each caption so
            # per-page margin shifts (odd/even pages) are handled automatically.
            x0, x1 = nx0 - 21, nx0 + 195
            clip = fitz.Rect(x0, ny0 - 200, x1, ny0 - 6)
            pix = page.get_pixmap(matrix=mat, clip=clip)
            out = f"{OUT_DIR}/p{pno}_{slug(name)}.png"
            pix.save(out)
            n += 1
    doc.close()
    print(f"{n} program crops -> {OUT_DIR}")


if __name__ == "__main__":
    main()
