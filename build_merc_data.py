"""Rebuild DATA.mercs in app.src.html by deriving it from the embedded characters.

Mercs are not a separate hand-authored deck: every "Merc"-keyworded character in
DATA.characters is a universal hireable model. This script reads the `const DATA = {...};`
literal, collects every Merc-tagged character (all star tiers, full object), and splices
the result into a delimited `DATA.mercs = [...]` block right after the literal. Idempotent.

Run this whenever DATA.characters changes, then re-run build_locked.mjs.
"""
import json, shutil

HERE = '/Users/Benjamin/Desktop/Projects/cyberpunk app/'
HTML_FILES = [HERE + 'app.src.html']

START = '/* MERC_DATA_START */'
END = '/* MERC_DATA_END */'
DATA_PREFIX = 'const DATA = '


def find_data_literal(html):
    """Return (start_index, end_index_exclusive_of_semicolon, parsed_dict) for `const DATA = {...};`."""
    i = html.index(DATA_PREFIX)
    brace = html.index('{', i)
    depth, j = 0, brace
    while j < len(html):
        c = html[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        j += 1
    literal = html[brace:j + 1]
    return brace, j + 1, json.loads(literal)


def collect_mercs(data):
    mercs, seen = [], set()
    for faction in (data.get('characters') or {}):
        for c in data['characters'][faction]:
            if any(str(k).lower() == 'merc' for k in (c.get('keywords') or [])):
                if c['id'] in seen:
                    continue
                seen.add(c['id'])
                mercs.append(c)
    # Sort by cost then name then star tier, for a tidy hire list.
    mercs.sort(key=lambda m: (m.get('cost', 0), m.get('name', ''), m.get('stars', 0)))
    return mercs


def splice(html, mercs):
    block = START + 'DATA.mercs = ' + json.dumps(mercs, ensure_ascii=False) + ';' + END
    if START in html and END in html:
        pre = html[:html.index(START)]
        post = html[html.index(END) + len(END):]
        return pre + block + post
    _, end, _ = find_data_literal(html)
    end = html.index(';', end - 1) + 1
    return html[:end] + '\n' + block + html[end:]


def run():
    for path in HTML_FILES:
        html = open(path, encoding='utf-8').read()
        _, _, data = find_data_literal(html)
        mercs = collect_mercs(data)
        shutil.copy(path, path + '.bak')
        open(path, 'w', encoding='utf-8').write(splice(html, mercs))
        factions = sorted({k for m in mercs for k in m.get('keywords', [])
                           if k in (data.get('factions') or {}).values()})
        print(f'{path.split("/")[-1]}: {len(mercs)} merc entr(ies) derived from tagged characters')


if __name__ == '__main__':
    run()
