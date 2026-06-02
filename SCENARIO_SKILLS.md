# Combat Zone — Scenario Action Skills

**Status:** ✅ Complete. The skill to perform each scenario **action** is tagged
on `SCENARIO_DATA` and shown as a chip in the scenario popup. Done 2026-06-01.

## What this is
Each scenario has special **actions** (Data Scrape, Hack Info, Shove 'Em, …).
The skill used to perform an action is shown only as an **icon** on the action
card — it is not in any text. This reads those icons and tags each action with
its skill.

## Source
- **`cyberpunk-combat-zone-scenario-compilation-1.pdf`** (gitignored), pp.2–35,
  one scenario per page. Text layer has the bodies but **no skill** — the skill
  is the hex icon on each action's title bar (image only) → vision-read.

## Icon legend (confirmed from the cards)
- Fist + burst = **Melee** · Crosshair = **Ranged** · "+" cross = **Medical**
- Gear/cog + plug = **Tech** · "!" = **Influence** · Running figure = **Reflexes**

(Cross-checked against text where stated: Shove 'Em "opposed by Reflexes" is a
Melee action defended by Reflexes; Lend Aid notes "instead of Med"; Pump Up's
Sats & Terms says "free Tech roll".)

## Method
1. `crop_scenarios.py` — crop each scenario page's action-box strip to
   `out/scenarios/actions/` at 5× (high-zoom icon crops for ambiguous ones).
2. Vision-read each action's icon → `scenario_skills.json`
   (`{scenario: {action title: skill}}`, action-type only; passive rules omitted).
3. `build_scenario_skills.py` — match by normalized title substring within each
   scenario and splice `skill` onto `special[]` in both HTML files. Dry-run by
   default; `--write` applies (writes `*.scnbak`). Result: **25 actions tagged**.
4. `openScenario` renders a cyan skill chip next to action titles that have one.

## Notes
- Passive specials (scoring rules, deploy rules) get no skill — intentional.
- Actions that are explicitly "Easy action (no roll)" (Recovery "Free Stuff",
  Secret Stash "The Search") get no skill — they require no test.
- Some actions allow an alternate skill (Crack the Container: Tech or Melee;
  Lend Aid: Med, or Influence/Tech vs a Camera) — the **default** icon skill is
  tagged; the alternates remain described in the action body.
