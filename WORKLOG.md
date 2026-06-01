# Combat Zone Roster — Worklog

App: `combat-zone-roster-v3.html` (single-file, embedded `DATA` blob).
Last updated: 2026-05-31.

## 1. Transcription — ALL 14 FACTIONS COMPLETE ✅
All factions transcribed/verified against the Omnibus cards (p158-206).
See `TRANSCRIPTION_CHECKLIST.md` for the per-faction workflow.

- [x] **Lawmen** — verified vs cards (p184-187, 2026-05-31). All 30 entries
      already correct; no changes needed. (Cell order ≠ text-layer order.)
- [x] **Edgerunners** — full redo done (p170-181, 2026-05-31). Replaced 35
      fabricated anime-cast entries with the real 46-model / 94-entry generic
      roster, read field-by-field from the card images. Committed ef1d4e4.
- [x] **Zoners** — low-confidence fields re-checked & fixed (Blaze, Forty Mike
      Mike, Scrub skills + Blaze actions). Committed 66c74dd.

### Done / verified (all 14)
6th Street · Arasaka · Bozos · Danger Gals · Edgerunners · Generation Red ·
Lawmen · Maelstrom · Max-Tac · Piranhas · Trauma Team · Tyger Claws ·
Wild Things · Zoners.

### Edgerunners low-confidence notes (re-check if cleaner renders appear)
- Jonathan Powers: only std+vet present on p170-181; index hinted an Elite
  tier that has no cell on this page set (may be in the p252-279 duplicate set).
- A few vet skill-vs-action upgrades were tie-broken by the std→vet pattern
  (e.g. Intrepid Media, Crew Chief). Specials with garbled card text
  (Obsessed Paparazzi VIDEO RECORD, Rockerboy Drummer WILD BEAT) were
  paraphrased for clarity.

## 2. App / UX
- [x] **Make the factions available on mobile.** Polished the native `<select>`:
      under 600px the faction picker + all `.field` controls now get min-height 44px,
      roomier padding, and 16px font (also stops iOS focus-zoom); labels bumped to 11px.
      Scoped to mobile, desktop untouched.
  - [ ] Still TODO: open on a real phone / 375px viewport and confirm the LIBRARY
        list + ROSTER stack readably under the TEAM SETUP panel.

## 3. Housekeeping
- [ ] Remove scratch files (`_*.txt` dumps) before each commit.
- [ ] Keep the `combat-zone-roster-progress` memory in sync after each faction.
