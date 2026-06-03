"""Rebuild DATA.mercs in app.src.html from mercs_to_fill.csv.

Parses the Merc (mercenary / hired gun) spreadsheet into a JS array and splices it
into app.src.html as a delimited `DATA.mercs = [...]` block placed right after the
`const DATA = {...};` literal. Idempotent: re-running replaces the block in place.

Mercs are whole models (the same object shape as faction characters), so each skill
cell is a plain printed value -> skills{}. The build auto-adds the "Merc" keyword.

After running this, re-run build_locked.mjs to regenerate the locked index.html.
"""
import json, csv, re, unicodedata, shutil

HERE = '/Users/Benjamin/Desktop/Projects/cyberpunk app/'
CSV = HERE + 'mercs_to_fill.csv'
HTML_FILES = [HERE + 'app.src.html']

SKILLS = ['Reflexes', 'Melee', 'Ranged', 'Medical', 'Tech', 'Influence']
START = '/* MERC_DATA_START */'
END = '/* MERC_DATA_END */'


def slug(name):
    s = unicodedata.normalize('NFKD', name)
    for a, b in [('’', "'"), ('‘', "'"), ('“', '"'),
                 ('”', '"'), ('–', '-'), ('—', '-')]:
        s = s.replace(a, b)
    s = re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
    return 'merc_' + s


def num(x):
    x = (x or '').strip().lstrip('+')
    return int(x) if x.isdigit() else 0


def read_rows():
    # Skip blank lines and comment lines starting with '#'.
    with open(CSV, newline='', encoding='utf-8') as fh:
        lines = [ln for ln in fh if ln.strip() and not ln.lstrip().startswith('#')]
    return list(csv.DictReader(lines))


def build_mercs():
    out = []
    for r in read_rows():
        name = (r.get('name') or '').strip()
        if not name:
            continue
        skills = {sk: num(r.get(sk)) for sk in SKILLS}
        actions = ''.join(c for c in (r.get('actions') or '').upper() if c in 'GYR')
        keywords = [k.strip() for k in (r.get('keywords') or '').split(',') if k.strip()]
        if 'Merc' not in keywords:
            keywords.append('Merc')
        out.append({
            'id': slug(name),
            'name': name,
            'stars': num(r.get('stars')),
            'cost': num(r.get('cost')),
            'armor': num(r.get('armor')),
            'keywords': keywords,
            'actions': actions,
            'skills': skills,
            'special': (r.get('special') or '').strip(),
        })
    return out


def splice(html, mercs):
    block = START + 'DATA.mercs = ' + json.dumps(mercs, ensure_ascii=False) + ';' + END
    if START in html and END in html:
        pre = html[:html.index(START)]
        post = html[html.index(END) + len(END):]
        return pre + block + post
    # First run: locate end of `const DATA = {...};` and insert after it.
    i = html.index('const DATA = ')
    depth, j = 0, html.index('{', i)
    while j < len(html):
        c = html[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1
    end = html.index(';', j) + 1
    return html[:end] + '\n' + block + html[end:]


def run():
    mercs = build_mercs()
    for path in HTML_FILES:
        html = open(path, encoding='utf-8').read()
        shutil.copy(path, path + '.bak')
        open(path, 'w', encoding='utf-8').write(splice(html, mercs))
        print(f'{path.split("/")[-1]}: {len(mercs)} merc(s) -> '
              f'{", ".join(m["name"] for m in mercs) or "(none)"}')


if __name__ == '__main__':
    run()
