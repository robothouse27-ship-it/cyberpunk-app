# Combat Zone Roster — Per-Faction Transcription Checklist

Workflow for replacing/verifying character data in the embedded `DATA` blob of
`combat-zone-roster-v3.html` against the Omnibus character cards.

Card pages (first tiered set, p158–206): 6th Street 158-159 · Arasaka 160-162 ·
Bozos 163-165 · Danger Gals 166-169 · Edgerunners 170-181 · Generation Red 182-183 ·
Lawmen 184-187 · Maelstrom 188-190 · Max-Tac 192-193 · Piranhas 194-195 ·
Trauma Team 196-197 · Tyger Claws 198-200 · Wild Things 202-203 · Zoners 204-206.

## Per faction

### 1. Prep
- [ ] Identify the faction's card page range (table above).
- [ ] Confirm pages are pre-rendered in `out/p<page>/` (`card_<cell>.png`,
      `_skills.png`, `_acts.png`). If missing, run `extract_cards.py` to rasterize.
- [ ] Read each page's `out/p<page>/index.txt` for the grid-cell map + text-layer
      names. NOTE: text-layer order does NOT map to cell order — always confirm by image.

### 2. Read the cards (images are the source of truth, not the PDF text layer)
- [ ] Read the full `card_<cell>.png` for each model/tier. Rows = tiers
      (A=Standard, B=Veteran, C=Elite); columns = different models.
- [ ] For each card capture: **Name**, **Keywords**, **Veteran stars** (0/1/2),
      **Cost/EB** (top-right), **Actions** (left hex column G/Y/R top→bottom),
      **Armor** (magenta number, left side — present only on some models, else 0),
      **Skills** (up to 3 right-side hexes), **Special rule(s)**, **Gear** (bottom bar).
- [ ] Use `_skills.png` strips to read skill values precisely. Icon legend:
      up-chevron = Reflexes · fist/web = Melee · crosshair = Ranged ·
      plus-cross = Medical · gear/CPU = Tech · "!" = Influence. The other skills = 0.
- [ ] Use `_acts.png` / left strip to confirm the action hex colors + armor.

### 3. Build the DATA entries
- [ ] One entry per tier: `{id, name, stars, cost, armor, actions, keywords[],
      skills{Reflexes,Melee,Ranged,Medical,Tech,Influence}, special}`.
- [ ] `id` = `<faction>_<name_snake>`, with `_v` (veteran) / `_e` (elite) suffixes.
- [ ] `cost` (EB) stays constant across tiers — vet/elite cost extra Street Cred (stars), not EB.
- [ ] Gonk/minion models: use `isGonk:true` + `action` (singular, e.g. "Y"),
      NOT `actions`. This is not corruption.
- [ ] `special` format: `"RULE NAME: text. Gear: NAME (keywords): rules."`
- [ ] Edit the blob by parsing JSON and re-dumping with `separators=(",",": ")`
      (the `DATA` blob is ONE giant line).

### 4. Verify
- [ ] Entry count == total card cells across the faction's pages.
- [ ] Every model name + tier count matches the cards.
- [ ] Spot-check costs, actions, skills, armor, specials, gear against the card images.
- [ ] (Pre-existing data) Triage by name-match: high match ⇒ stats usually correct,
      spot-check only; low match ⇒ fabricated, full redo. Watch for missing models.

### 5. Commit
- [ ] `git add combat-zone-roster-v3.html`
- [ ] Commit msg: `Transcribe <Faction> from Omnibus cards (p<range>)`
      (or `Verify <Faction> vs cards; <fixes>` if only verifying/fixing).
- [ ] Remove any scratch files (`_*.txt` dumps) before committing.
- [ ] Update the `combat-zone-roster-progress` memory (Done / Verify / Fabricated lists).

## Status snapshot (2026-05-31)
- **Done / verified:** 6th Street, Arasaka, Bozos, Danger Gals, Generation Red,
  Maelstrom, Max-Tac, Piranhas, Trauma Team, Tyger Claws, Wild Things, Zoners,
  Lawmen.
- **Lawmen** verified vs cards p184-187 (2026-05-31): all 30 entries correct,
  no changes. Cell→model order differs from text-layer order (read images).
- **Zoners** low-confidence fields re-checked vs clean renders (2026-05-31):
  fixed Blaze, Forty Mike Mike, Scrub skills + Blaze actions.
- **Still to do:** Edgerunners (full redo, p170-181) — fabricated anime cast,
  real cards are generic roles (Industrial Tech Supervisor, Nomad Scout, etc.).
