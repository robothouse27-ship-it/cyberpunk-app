"""Rebuild DATA.fbc in index.html from fbc_to_fill.csv.

Parses the FBC (Full Body Conversion) spreadsheet into a JS array and splices it
into index.html as a delimited `DATA.fbc = [...]` block placed right after the
`const DATA = {...};` literal. Idempotent: re-running replaces the block in place.

Skill cells: a leading '+' (e.g. "+1") -> additive bonus (skill_bonus); a bare
number (e.g. "3") -> replace-if-higher (skills); blank -> no change.
"""
import json, csv, re, unicodedata, shutil

HERE = '/Users/Benjamin/Desktop/Projects/cyberpunk app/'
CSV = HERE + 'fbc_to_fill.csv'
HTML_FILES = [HERE + 'index.html']

SKILLS = ['Reflexes', 'Melee', 'Ranged', 'Medical', 'Tech', 'Influence']
START = '/* FBC_DATA_START */'
END = '/* FBC_DATA_END */'


def slug(name):
    s = unicodedata.normalize('NFKD', name)
    for a, b in [('’', "'"), ('‘', "'"), ('“', '"'),
                 ('”', '"'), ('–', '-'), ('—', '-')]:
        s = s.replace(a, b)
    s = re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
    return 'fbc_' + s


def num(x):
    x = (x or '').strip()
    return int(x) if x.isdigit() else 0


def read_rows():
    # Skip blank lines and comment lines starting with '#'.
    with open(CSV, newline='', encoding='utf-8') as fh:
        lines = [ln for ln in fh if ln.strip() and not ln.lstrip().startswith('#')]
    return list(csv.DictReader(lines))


def build_fbc():
    out = []
    for r in read_rows():
        name = (r.get('name') or '').strip()
        if not name:
            continue
        skills, skill_bonus = {}, {}
        for sk in SKILLS:
            cell = (r.get(sk) or '').strip()
            if not cell:
                continue
            if cell.startswith('+'):
                skill_bonus[sk] = num(cell[1:])
            else:
                skills[sk] = num(cell)
        bonus_actions = ''.join(c for c in (r.get('bonus_actions') or '').upper()
                                if c in 'GYR')
        keywords = [k.strip() for k in (r.get('keywords') or '').split(',') if k.strip()]
        out.append({
            'id': slug(name),
            'name': name,
            'cost': num(r.get('cost')),
            'cred': num(r.get('cred')),
            'rarity': num(r.get('rarity')),
            'bonus_actions': bonus_actions,
            'armor': num(r.get('armor')),
            'skills': skills,
            'skill_bonus': skill_bonus,
            'abilities': (r.get('abilities') or '').strip(),
            'keywords': keywords,
        })
    return out


def splice(html, fbc):
    block = START + 'DATA.fbc = ' + json.dumps(fbc, ensure_ascii=False) + ';' + END
    if START in html and END in html:
        pre = html[:html.index(START)]
        post = html[html.index(END) + len(END):]
        return pre + block + post
    # First run: locate end of `const DATA = {...};` and insert after it.
    i = html.index('const DATA = ')
    start = html.index('{', i)
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
    # advance past the trailing ';'
    end = html.index(';', j) + 1
    return html[:end] + '\n' + block + html[end:]


def run():
    fbc = build_fbc()
    for path in HTML_FILES:
        html = open(path, encoding='utf-8').read()
        shutil.copy(path, path + '.bak')
        open(path, 'w', encoding='utf-8').write(splice(html, fbc))
        print(f'{path.split("/")[-1]}: {len(fbc)} FBC card(s) -> '
              f'{", ".join(f["name"] for f in fbc) or "(none)"}')


if __name__ == '__main__':
    run()
