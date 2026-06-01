# Combat Zone Roster — Worklog

App: `combat-zone-roster-v3.html` (single-file, embedded `DATA` blob).
Last updated: 2026-05-31.

## 1. Transcription — remaining factions
Replacing fabricated/placeholder card data with accurate Omnibus stats, faction by faction.
See `TRANSCRIPTION_CHECKLIST.md` for the per-faction workflow.

- [ ] **Lawmen** — verify vs cards (p184-187). 87% name match, so likely mostly
      correct; spot-check costs/actions/skills/armor/specials rather than full redo.
- [ ] **Edgerunners** — full redo (p170-181, 12 pages). Baseline is the fabricated
      anime cast (David/Lucy/Rebecca) instead of generic roles. Largest remaining job.
- [ ] **Zoners** — re-check low-confidence fields once renders are clean:
      Blaze skills {Mel2,Ran1}, Forty Mike Mike skills {Ran2 only?},
      Scrub skills {Ref1,Ran1}; all armor currently set to 0.

### Done / verified
6th Street · Arasaka · Bozos · Danger Gals · Generation Red · Maelstrom ·
Max-Tac · Piranhas · Trauma Team · Tyger Claws · Wild Things · Zoners (rebuilt).

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
