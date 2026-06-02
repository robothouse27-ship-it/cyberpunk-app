"""Splice program rule text from programs_text.json into DATA.programs in both
HTML files, matched by name, preserving existing id/order. Adds a `desc` field
(composed from front/effect/refresh) that openProgram() renders via fmtRanges.

Dry-run by default (prints a match report); pass --write to modify the files.
"""
import json, re, sys, shutil

FILES = ["index.html", "combat-zone-roster-v3.html"]
TEXT = "programs_text.json"


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def compose(e):
    parts = []
    if e.get("front", "").strip():
        parts.append(e["front"].strip())
    if e.get("effect", "").strip():
        parts.append("Program Effect: " + e["effect"].strip())
    if e.get("refresh", "").strip():
        parts.append("Refresh: " + e["refresh"].strip())
    return "\n".join(parts)


def find_programs_blob(html):
    """Return (start, end) indices of the {...} value of "programs", string-aware."""
    key = html.index('"programs"')
    i = html.index("{", key)
    depth, j, in_str, esc = 0, i, False, False
    while j < len(html):
        c = html[j]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i, j + 1
        j += 1
    raise ValueError("unterminated programs object")


def main():
    write = "--write" in sys.argv
    text = json.load(open(TEXT, encoding="utf8"))
    by_norm = {norm(k): (k, v) for k, v in text.items()}

    for path in FILES:
        html = open(path, encoding="utf8").read()
        s, e = find_programs_blob(html)
        programs = json.loads(html[s:e])

        matched, missing_in_text, used = 0, [], set()
        for faction, lst in programs.items():
            for p in lst:
                key = norm(p["name"])
                if key in by_norm:
                    p["desc"] = compose(by_norm[key][1])
                    matched += 1
                    used.add(key)
                else:
                    missing_in_text.append(p["name"])
        unused = [by_norm[k][0] for k in by_norm if k not in used]

        total = sum(len(v) for v in programs.values())
        print(f"\n=== {path} ===")
        print(f"  DATA programs: {total} | matched: {matched}")
        if missing_in_text:
            print(f"  NO card text for ({len(missing_in_text)}): {missing_in_text}")
        if unused:
            print(f"  card text unused ({len(unused)}): {unused}")

        if write:
            shutil.copy(path, path + ".progbak")
            new = html[:s] + json.dumps(programs, ensure_ascii=False) + html[e:]
            open(path, "w", encoding="utf8").write(new)
            print(f"  wrote {path} (backup {path}.progbak)")

    if not write:
        print("\n(dry run — pass --write to apply)")


if __name__ == "__main__":
    main()
