"""Splice the per-action `skill` from scenario_skills.json into SCENARIO_DATA in
both HTML files. Adds special[].skill (e.g. "Tech") to action-type specials,
matched by normalized title substring within each scenario.

Dry-run by default; pass --write to apply (writes *.scnbak backups)."""
import json, re, sys, shutil

FILES = ["index.html", "combat-zone-roster-v3.html"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def find_blob(html, anchor):
    """Return (start, end) of the {...} that follows `anchor`, string-aware."""
    key = html.index(anchor)
    i = html.index("{", key)
    depth, j, ins, esc = 0, i, False, False
    while j < len(html):
        c = html[j]
        if ins:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': ins = False
        else:
            if c == '"': ins = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i, j + 1
        j += 1
    raise ValueError("unterminated object after " + anchor)


def main():
    write = "--write" in sys.argv
    skills = {k: v for k, v in json.load(open("scenario_skills.json", encoding="utf8")).items()
              if not k.startswith("_")}
    skills_norm = {norm(k): v for k, v in skills.items()}

    for path in FILES:
        html = open(path, encoding="utf8").read()
        s, e = find_blob(html, "const SCENARIO_DATA")
        data = json.loads(html[s:e])

        applied, unmatched = 0, []
        for sc in data["scenarios"]:
            amap = skills_norm.get(norm(sc["name"]))
            if not amap:
                continue
            want = {norm(t): sk for t, sk in amap.items()}
            hit = set()
            for sp in sc.get("special", []):
                tnorm = norm(sp["title"])
                for frag, sk in want.items():
                    if frag in tnorm:
                        sp["skill"] = sk
                        applied += 1
                        hit.add(frag)
                        break
            for frag in want:
                if frag not in hit:
                    unmatched.append(f"{sc['name']} :: {frag}")

        print(f"\n=== {path} ===")
        print(f"  skills applied: {applied}")
        if unmatched:
            print(f"  UNMATCHED action titles ({len(unmatched)}): {unmatched}")

        if write:
            shutil.copy(path, path + ".scnbak")
            open(path, "w", encoding="utf8").write(html[:s] + json.dumps(data, ensure_ascii=False) + html[e:])
            print(f"  wrote {path} (backup {path}.scnbak)")

    if not write:
        print("\n(dry run — pass --write to apply)")


if __name__ == "__main__":
    main()
