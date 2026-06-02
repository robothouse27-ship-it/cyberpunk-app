"""Insert the 6 programs that exist on the cards but are missing from
DATA.programs, as {id, name} stubs in the correct faction. Run build_program_data.py
afterwards to populate their desc. Writes *.addbak backups."""
import json, re, shutil
from build_program_data import find_programs_blob, norm

FILES = ["index.html", "combat-zone-roster-v3.html"]

# card faction label -> DATA faction key
FAC = {"Bozos": "bozos", "Generation Red": "genred", "Edgerunners": "edgerunners",
       "Universal": "universal", "Zoners": "zoners"}

MISSING = ["I Am Rubber...", "Junk.exe", "Molasses.exe", "Program 7", "Stomp.exe", "Tag!"]


def pid(name):
    return "p_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def main():
    text = json.load(open("programs_text.json", encoding="utf8"))
    for path in FILES:
        html = open(path, encoding="utf8").read()
        s, e = find_programs_blob(html)
        programs = json.loads(html[s:e])
        existing = {norm(p["name"]) for v in programs.values() for p in v}
        added = []
        for name in MISSING:
            if norm(name) in existing:
                continue
            fac = FAC[text[name]["faction"]]
            programs.setdefault(fac, []).append({"id": pid(name), "name": name})
            # keep each faction list alphabetical by name, like the source data
            programs[fac].sort(key=lambda p: p["name"].lower())
            added.append(f"{name} -> {fac} ({pid(name)})")
        shutil.copy(path, path + ".addbak")
        new = html[:s] + json.dumps(programs, ensure_ascii=False) + html[e:]
        open(path, "w", encoding="utf8").write(new)
        print(f"{path}: added {len(added)}")
        for a in added:
            print("   +", a)


if __name__ == "__main__":
    main()
