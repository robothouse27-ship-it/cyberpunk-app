# Combat Zone — Program Extraction (Program cards, pp. 240–250)

**Status:** ✅ Complete. Rules text for all **60** in-app programs transcribed and
spliced into `DATA.programs`. Done 2026-06-01.

## What this is
A card-by-card read of every **Program** in the Omnibus PROGRAMS section, adding a
`desc` field (front ability + Program Effect + Refresh) to each program so the
in-app program popup (`openProgram`) shows real rules instead of the
"No rules text transcribed yet" placeholder.

## Source
- **`Copy of Data Fortress Omnibus 24-13-11 FC.pdf`**, pages **240–250** (1-indexed),
  the PROGRAMS section: 6 programs per page, **66 cards total**.
- Text layer per card = **name + faction + "Errata"** only. The card **body**
  (flavor, ability, Program Effect, Refresh) is **image-only** → vision-read, the
  same as the Gear cards (see `GEAR_EXTRACTION.md`).

## Method (reproducible)
1. `render_programs.py` — render pp.240–250 to `out/programs/page_<n>.png` (4×) and
   build `programs_to_fill.json` (name+faction scaffold from the text layer).
2. `crop_programs.py` — crop each program's front+back card pair to
   `out/programs/crops/p<page>_<slug>.png` at 7×. Crop x-extents are derived from
   each caption's position (odd pages are inset ~56pt vs even pages).
3. Vision-read each crop → `programs_text.json`: `{name: {faction, front, effect, refresh}}`,
   verbatim from the cards.
4. `build_program_data.py` — match by normalized name, compose
   `desc = front + "Program Effect: …" + "Refresh: …"`, and splice into
   `DATA.programs` in **both** `index.html` and `combat-zone-roster-v3.html`,
   **preserving existing `id` and order**. Dry-run by default; `--write` to apply
   (writes `*.progbak` backups). Result: **60/60 matched**.

## Output files
- `programs_text.json` — source of truth (66 cards, verbatim front/effect/refresh).
- `programs_to_fill.json` — name+faction scaffold from the text layer.
- `render_programs.py`, `crop_programs.py`, `build_program_data.py` — tooling.
- `out/programs/` — page renders; `out/programs/crops/` — per-program crops.

## Conventions
- `desc` uses `\n` line breaks (the app's `fmtRanges` converts to `<br>` and
  colorizes GREEN/YELLOW/RED). "Program Effect" / "Refresh" label the back-card text.
- "Vulnerable" is kept where printed (it's a program keyword).

## ⚠️ Flags / things to double-check
1. **6 programs on the cards are NOT in the app's `DATA.programs`** and were left
   out (no in-app entry to attach to): **I Am Rubber...** (Bozos), **Junk.exe**
   (Generation Red), **Molasses.exe** (Edgerunners), **Program 7** (Universal),
   **Stomp.exe** (Generation Red), **Tag!** (Zoners). Their text is already in
   `programs_text.json` — re-run `build_program_data.py` after adding the stubs to
   DATA to populate them.
2. A few weapon-style fronts (e.g. **Aerial Strike**, **Nervous System Overload**)
   show a range-bar + traits rather than a sentence; these were paraphrased into a
   short attack description. Verify against the card if exact wording matters.
3. **Magnetic Shielding** and **Request Backup** have no/blank Refresh box on the
   card; their `refresh` is left empty.
