"""Crop the action-box strip (bottom of each scenario page) so the skill icon
next to each action is legible for vision-reading. Scenario action skills are
icon-only in the compilation PDF (text layer has no skill)."""
import fitz, os, re

PDF = "cyberpunk-combat-zone-scenario-compilation-1.pdf"
OUT = "out/scenarios/actions"

# PDF page (1-indexed) -> scenario name (matched by flavor; 2 added by hand)
PAGES = {
    2: "Flushable Swipes", 3: "Don't Fence Me In", 4: "Pump Up the Signal",
    5: "Open Connection", 6: "Blitzkrieg of the Bands", 7: "Heroics for the Cam",
    8: "Tech-Tock", 9: "Opportune Collapse", 10: "Test the Security",
    11: "Hit Em in the Wallet", 12: "Fair LOL", 13: "Making Kings",
    14: "Push and Theyre Off", 15: "Let the Cubs Hunt", 16: "Youve Got the Beat",
    17: "Get the Message Out", 18: "Glitch at 11", 19: "Playing Tag",
    20: "Let It Snow", 22: "Turf War", 23: "The Mule", 24: "Data Sweep",
    25: "Frame Up", 26: "Quarter Mile", 27: "Recovery", 28: "Corporate Ladder",
    29: "Heist", 30: "Crossing Barricades", 31: "Hot Zone", 32: "Corporate Affairs",
    33: "Secret Stash", 34: "Hostile Takeover", 35: "Pit Fight",
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def main():
    os.makedirs(OUT, exist_ok=True)
    d = fitz.open(PDF)
    for pno, name in PAGES.items():
        clip = fitz.Rect(0, 405, 612, 786)
        pix = d[pno - 1].get_pixmap(matrix=fitz.Matrix(5, 5), clip=clip)
        pix.save(f"{OUT}/p{pno}_{slug(name)}.png")
    print(f"{len(PAGES)} action strips -> {OUT}")


if __name__ == "__main__":
    main()
