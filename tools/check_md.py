"""Render every note with a GFM-like parser and list anything that looks wrong."""
import html
import pathlib
import re
import sys
from markdown_it import MarkdownIt

md = MarkdownIt("gfm-like")
notes = sorted(pathlib.Path(sys.argv[1]).glob('*.md'))
bad = {}
def add(k, f, s): bad.setdefault(k, []).append((f.name, s))
for f in notes:
    t = re.sub(r'^---\n.*?\n---\n', '', f.read_text(), flags=re.S)
    h = md.render(t)
    h2 = re.sub(r'<pre>.*?</pre>', '', h, flags=re.S)
    h2 = re.sub(r'<code>.*?</code>', '', h2, flags=re.S)
    txt = html.unescape(re.sub(r'<[^>]+>', '', h2))
    for m in re.finditer(r'\\[\\`*_\[\]()#+\-.!<>|]', txt):
        add('literal-backslash', f, txt[max(0, m.start()-40):m.end()+40].replace('\n', ' '))
    for m in re.finditer(r'(?<![\w`])\*\*?\w', txt):
        add('stray-star', f, txt[max(0, m.start()-40):m.end()+40].replace('\n', ' '))
    if len(re.findall(r'<h1', h)) != 1:
        add('h1count', f, str(len(re.findall(r'<h1', h))))
    for m in re.finditer(r'<pre><code>(.{0,80})', h, flags=re.S):
        add('pre-nolang', f, m.group(1).replace('\n', ' | '))
    for m in re.finditer(r'<h2>(.*?)</h2>', h):
        if m.group(1) not in ('Quick reference', 'Explained', 'In one line') and not m.group(1).startswith('Script: '):
            add('odd-h2', f, m.group(1))
    for m in re.finditer(r'<a href="(?!\.\./scripts/)([^"]+)"', h):
        add('link', f, m.group(1))
    for m in re.finditer(r'<(del|s)>', h):
        add('strike', f, h[m.start():m.start()+80])
for k, v in bad.items():
    print('==', k, len(v))
    for x in v[:12]:
        print('   ', x)
print('checked', len(notes))
