"""Render the PROGRAMS section (Omnibus pp.240-250) to page PNGs and build a
scaffold JSON of {name, faction, desc:""} for vision transcription.

Card rules text is image-only in the PDF; only name+faction are in the text
layer. Mirrors the Gear pipeline (montage_gear.py / GEAR_EXTRACTION.md).
"""
import fitz, json, os

PDF = "Copy of Data Fortress Omnibus 24-13-11 FC.pdf"
PAGES = range(240, 251)  # 1-indexed, inclusive
ZOOM = 4
OUT_DIR = "out/programs"


def page_cards(page):
    """Parse (name, faction) pairs from the text layer: each card is
    name / faction / 'Errata: ...' in reading order."""
    lines = [l.strip() for l in page.get_text().splitlines() if l.strip()]
    cards = []
    for i, l in enumerate(lines):
        if l.startswith("Errata") and i >= 2:
            name, faction = lines[i - 2], lines[i - 1]
            cards.append((name, faction))
    return cards


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = fitz.open(PDF)
    mat = fitz.Matrix(ZOOM, ZOOM)
    scaffold = []
    for pno in PAGES:
        page = doc[pno - 1]
        pix = page.get_pixmap(matrix=mat)
        out = f"{OUT_DIR}/page_{pno}.png"
        pix.save(out)
        cards = page_cards(page)
        print(f"page {pno}: {len(cards)} cards -> {out} ({pix.width}x{pix.height})")
        for name, faction in cards:
            scaffold.append({"name": name, "faction": faction, "page": pno, "desc": ""})
    doc.close()
    with open("programs_to_fill.json", "w", encoding="utf8") as f:
        json.dump(scaffold, f, indent=2, ensure_ascii=False)
    print(f"\n{len(scaffold)} cards -> programs_to_fill.json")


if __name__ == "__main__":
    main()
