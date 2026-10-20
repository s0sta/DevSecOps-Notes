"""Turn the LinkedIn posts into Markdown notes (GitHub-ready) + index.json.
Usage: python3 make_notes.py SRC_DIR BUILD_DIR OUT_DIR"""
import json
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from codeutil import is_code, lang_of, mark_inline  # noqa: E402
from topics import ASSIGN  # noqa: E402

SRC, BUILD, OUT = (pathlib.Path(a) for a in sys.argv[1:4])
posts = json.load(open(BUILD / "posts.json"))
specs = json.load(open(BUILD / "specs.json"))

# Small fixes to the source data (post number -> [(old text, new text)]). Keep this list short and tell Hosam.
FIXES = {
    208: [("kubectl.io is open in the exam", "kubernetes.io/docs is open in the exam")],
}


def _fix(obj, pairs):
    if isinstance(obj, str):
        for old, new in pairs:
            obj = obj.replace(old, new)
        return obj
    if isinstance(obj, list):
        return [_fix(x, pairs) for x in obj]
    if isinstance(obj, dict):
        return {k: _fix(v, pairs) for k, v in obj.items()}
    return obj


for _n, _pairs in FIXES.items():
    if str(_n) in specs:
        specs[str(_n)] = _fix(specs[str(_n)], _pairs)
    for _p in posts:
        if _p["n"] == _n:
            _p["text"] = _fix(_p["text"], _pairs)
SCRIPTS = {f.name: f for f in SRC.glob("*/*/Scripts/*.py")}


# ---------------------------------------------------------------- markdown helpers
def esc(t):
    t = t.replace("\\", "\\\\").replace("`", "\\`").replace("*", "\\*")
    t = re.sub(r"<(?=[A-Za-z/!])", r"\\<", t)
    t = re.sub(r"\[(?=[^\]]*\]\()", r"\\[", t)
    return t


def code_span(c):
    c = c.strip()
    if "`" in c:
        return "`` " + c + " ``"
    return "`" + c + "`"


def inline(text, known):
    out = []
    for kind, seg in mark_inline(text, known):
        out.append(code_span(seg) if kind == "c" else esc(seg))
    s = "".join(out)
    if re.match(r"^(>|#|[-+] |\d+[.)] )", s):
        s = "\\" + s
    return s


def inl(text, known):
    """Like inline(), for text inside bold, a list item or a table cell (no escape at the start)."""
    return "".join(code_span(seg) if kind == "c" else esc(seg) for kind, seg in mark_inline(text, known))


def cellify(s):
    """Text for a table cell: no line breaks, | escaped (also inside code spans, GFM style)."""
    return s.replace("\n", " ").replace("|", "\\|")


def block(lines, lang=None):
    lines = [l.rstrip() for l in lines]
    body = "\n".join(lines).strip("\n")
    if not lang:
        first = next((l for l in lines if l.strip() and not l.lstrip().startswith("#")), "")
        lang = lang_of(first)
    fence = "~~~" if "```" in body else "```"
    return f"{fence}{lang}\n{body}\n{fence}"


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def title_label(s):
    s = re.sub(r"^#?\s*\d+\s+", "", s.strip())          # "# 01  What did the server answer?" / "01  BUILD THE STACK"
    s = s.lstrip("# ").strip()
    if s.isupper():
        parts = [x for x in re.split(r"\s{2,}", s) if x]
        s = " · ".join(x.capitalize() for x in parts)
        s = re.sub(r"\b(dns|ip|tls|ssl|ssh|cpu|lvm|api|ci|cd|sql|aws|gcp|vm|vms|k8s|iam|rbac|pv|pvc|vg|lv|nsg)\b", lambda m: m.group(1).upper(), s, flags=re.I)
    return s


def tag_md(tag):
    tag = (tag or "").strip()
    if not tag:
        return ""
    if is_code(tag) or re.search(r"[$:/_.()=<>\[\]]", tag):
        return " · " + code_span(tag)
    return " · *" + esc(tag) + "*"


def chain(links, names):
    """Turn [[a,b],[b,c],[c,d],[c,e]] into 'A → B → C → D, C → E'."""
    nxt = {}
    for a, b in links:
        nxt.setdefault(a, []).append(b)
    inc = {b for _, b in links}
    starts = [a for a, _ in links if a not in inc] or ([links[0][0]] if links else [])
    seen_edges, parts = set(), []
    for s0 in dict.fromkeys(starts):
        stack = [[s0]]
        while stack:
            path = stack.pop()
            cur = path[-1]
            kids = [k for k in nxt.get(cur, []) if (cur, k) not in seen_edges]
            if not kids:
                if len(path) > 1:
                    parts.append(" → ".join(names.get(x, x) for x in path))
                continue
            for i, k in enumerate(reversed(kids)):
                seen_edges.add((cur, k))
                stack.append((path if i == len(kids) - 1 else [cur]) + [k])
    return "; ".join(parts)


# ---------------------------------------------------------------- quick reference from the GIF data
def quickref(sp, known):
    L = sp["layout"]
    out = []
    if L == "terminal":
        for ch in sp.get("chapters", []):
            out.append("### " + title_label(ch.get("head", ch.get("tab", ""))))
            lines = []
            for row in ch.get("rows", []):
                cmd, comment = row[0], (row[2] if len(row) > 2 else "")
                if comment:
                    lines.append("# " + comment.lstrip("# ").strip())
                lines.append(cmd)
            out.append(block(lines))
    elif L == "checklist":
        for g in sp.get("rows", []):
            out.append("### " + title_label(g.get("label", "")))
            items = g.get("items", [])
            if items and all(is_code(it[1]) for it in items):
                lines = []
                for it in items:
                    lines += ["# " + it[0], it[1]]
                out.append(block(lines))
            else:
                out.append("\n".join(f"- **{esc(it[0])}**" + (f" — {code_span(it[1])}" if is_code(it[1]) else f" — {inl(it[1], known)}") for it in items))
    elif L == "steps":
        for g in sp.get("groups", []):
            head = title_label(g.get("label", ""))
            if g.get("head"):
                head += " — " + g["head"]
            out.append("### " + head)
            rows = g.get("rows", [])
            if rows and all(is_code(r[0]) for r in rows):
                lines = []
                for r in rows:
                    lines += ["# " + r[1], r[0]]
                out.append(block(lines))
            else:
                out.append("\n".join(f"- {code_span(r[0]) if is_code(r[0]) else '**' + esc(r[0]) + '**'} — {inline(r[1], known)}" for r in rows))
    elif L == "cheatsheet":
        for b in sp.get("blocks", []):
            out.append("### " + b.get("name", ""))
            out.append(block(b.get("cmds", [])))
    elif L == "dontdo":
        for i, pr in enumerate(sp.get("pairs", []), 1):
            bad, good = pr.get("bad", ""), pr.get("good", "")
            if is_code(bad) or is_code(good):
                out.append(f"**{i}. Don't**")
                out.append(block([bad]) if is_code(bad) else inline(bad, known))
                out.append(inline(pr.get("bad_why", ""), known))
                out.append("**Do instead**")
                out.append(block([good]) if is_code(good) else inline(good, known))
                out.append(inline(pr.get("good_why", ""), known))
            else:
                out.append(f"**{i}.** ❌ **{inl(bad, known)}** — {inline(pr.get('bad_why', ''), known)}  \n✅ **{inl(good, known)}** — {inline(pr.get('good_why', ''), known)}")
    elif L == "code":
        run, output = sp.get("run"), sp.get("output") or []
        if sp.get("pyfile"):
            out.append(f"The full script is at the end of this note: **{sp['pyfile']}** (standard library only, no `pip install`).")
        if run:
            out.append("**Run it**")
            out.append(block([run], "bash"))
        if output:
            out.append("**Example output**")
            out.append(block(output, "text"))
    elif L == "anatomy":
        segs = sp.get("segments", [])
        sep = sp.get("sep", " ")
        out.append(block([sep.join(s[0] for s in segs)], "text"))
        out.append("| Part | Name | What it means |\n|:--|:--|:--|\n" + "\n".join(
            f"| {cellify(code_span(s[0]))} | {cellify(esc(s[1]))} | {cellify(inline(s[2], known))} |" for s in segs))
    elif L == "pipeline":
        out.append("\n".join(f"{i}. **{esc(st[0])}** — {inline(st[1], known)}" + (tag_md(st[2]) if len(st) > 2 else "")
                             for i, st in enumerate(sp.get("stages", []), 1)))
    elif L == "quiz":
        for i, q in enumerate(sp.get("questions", []), 1):
            opts = q.get("opts", [])
            out.append(f"**Q{i}. {inline(q.get('q', ''), known)}**")
            out.append("\n".join(f"- {'abcdef'[j]}) {inline(o, known)}" for j, o in enumerate(opts)))
            a = q.get("answer")
            ans = f"{'abcdef'[a]}) {inline(opts[a], known)}" if isinstance(a, int) and a < len(opts) else ""
            out.append(f"> **Answer:** {ans}. {inline(q.get('why', ''), known)}")
    elif L == "numbers":
        cards = sp.get("cards", [])
        extra = any(len(c) > 3 and c[3] for c in cards)
        head = "| Number | What | Why it matters |" + (" |" if extra else "")
        out.append(head + "\n|:--|:--|:--|" + (":--|" if extra else "") + "\n" + "\n".join(
            f"| **{cellify(esc(c[0]))}** | {cellify(esc(c[1]))} | {cellify(inline(c[2], known))} |" + (f" {cellify(esc(c[3]))} |" if extra else "") for c in cards))
    elif L == "compare":
        lt, rt = sp.get("left", {}), sp.get("right", {})
        out.append(f"| | **{esc(lt.get('name', ''))}** | **{esc(rt.get('name', ''))}** |\n|:--|:--|:--|\n" + "\n".join(
            f"| {cellify(esc(r[0]))} | {cellify(inline(r[1], known))} | {cellify(inline(r[2], known))} |" for r in sp.get("rows", [])))
        for side in (lt, rt):
            line = f"**{esc(side.get('name', ''))}** ({esc(side.get('full', ''))}): {inline(side.get('blurb', ''), known)}"
            out.append(line)
            if side.get("cmd"):
                out.append(block([side["cmd"]]) if is_code(side["cmd"]) else "Example: " + code_span(side["cmd"]))
        if sp.get("short"):
            out.append("\n".join("- " + inline(re.sub(r"\s+->\s+", " → ", s), known) for s in sp["short"]))
    elif L == "matrix":
        cols = sp.get("cols", [])
        sym = {"+": "✅ ", "-": "❌ ", "~": "🟡 "}
        cell = lambda v: cellify(sym.get(v[:1], "") + inline(v[1:] if v[:1] in sym else v, known)) if v else ""
        out.append("| | " + " | ".join(f"**{esc(c)}**" for c in cols) + " |\n|:--|" + ":--|" * len(cols) + "\n" + "\n".join(
            f"| {cellify(esc(r[0]))} | " + " | ".join(cell(v) for v in r[1]) + " |" for r in sp.get("rows", [])))
        if sp.get("pick"):
            out.append("**How to pick**")
            out.append("\n".join("- " + re.sub(r"^(.+?)\s+->\s+", lambda m: f"**{esc(m.group(1))}** → ", inline(p, known)) for p in sp["pick"]))
    elif L == "stack":
        if sp.get("axis"):
            out.append(f"*{esc(sp['axis'].capitalize())}*")
        out.append("\n".join(f"{i}. **{esc(l[0])}** — {inline(l[1], known)}" + (tag_md(l[2]) if len(l) > 2 else "")
                             for i, l in enumerate(sp.get("layers", []), 1)))
    elif L == "dashboard":
        if sp.get("status"):
            out.append(f"**Status:** {esc(sp['status'])}")
        out.append("| Metric | Value | Note |\n|:--|:--|:--|\n" + "\n".join(
            f"| {cellify(esc(t.get('label', '')))} | **{cellify(esc(str(t.get('display', t.get('value', '')))))}{'%' if t.get('kind') in ('ring', 'bar') else ''}** | {cellify(inline(t.get('sub', ''), known))} |"
            for t in sp.get("tiles", [])))
    elif L == "timeline":
        out.append("| Time | Step | What happens |\n|:--|:--|:--|\n" + "\n".join(
            f"| **{cellify(esc(e[0]))}** | {cellify(esc(e[1]))} | {cellify(inline(e[2], known))} |" for e in sp.get("events", [])))
    elif L == "reveal":
        out.append("\n".join(f"- **{esc(c[0])}** — {inline(c[1], known)}" for c in sp.get("cards", [])))
    elif L == "architecture":
        names = {}
        for t in sp.get("tiers", []):
            nodes = t.get("nodes", [])
            for nd in nodes:
                names[nd.get("id")] = nd.get("name")
            out.append(f"- **{esc(title_label(t.get('label', '')))}:** " + " · ".join(f"{esc(nd.get('name', ''))} ({esc(nd.get('tag', ''))})" for nd in nodes))
        out = ["\n".join(out)] if out else []
        if sp.get("links"):
            out.append("**Request flow:** " + esc(chain(sp["links"], names)))
        if sp.get("services"):
            out.append("**Around it:** " + " · ".join(f"{esc(s.get('name', ''))} ({esc(s.get('tag', ''))})" for s in sp["services"]))
    elif L == "explainer":
        for pn in sp.get("panels", []):
            out.append("### " + pn.get("head", ""))
            out.append("\n".join("- " + inline(b, known) for b in pn.get("bullets", [])))
        if sp.get("note"):
            out.append("> **Note:** " + inline(sp["note"], known))
    return out


# ---------------------------------------------------------------- the post text as readable Markdown
CALLOUT = re.compile(r"^(One honest caveat|The honest caveat|An honest caveat|The caveat|Honest caveat|The lesson behind it|The lesson|"
                     r"The rule that saves you|The rule|The pattern behind all five|The pattern|The theme|The practical use|"
                     r"Why this matters in practice|The debugging order that works|The trick|The result|The one habit)\b[^:]{0,40}:")
HEAD_OK = re.compile(r"^[A-Z0-9\"'(][^.!]{0,58}[?]?$")


def body_md(text, end_line, known):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    if paras and re.match(r"^#\w", paras[-1]):
        paras.pop()                                         # hashtags
    if paras and paras[-1].endswith("?") and len(paras[-1]) < 160:
        paras.pop()                                         # the LinkedIn question
    if paras and end_line and norm(paras[-1]) == norm(end_line):
        paras.pop()                                         # the closing line (shown as "In one line")
    elif paras and len(paras[-1]) < 70 and "\n" not in paras[-1] and paras[-1].endswith("."):
        pass
    lead = paras.pop(0) if paras else ""
    out = []
    for i, p in enumerate(paras):
        lines = p.splitlines()
        nxt = paras[i + 1] if i + 1 < len(paras) else ""
        if len(lines) == 1 and HEAD_OK.match(p) and len(p) <= 60 and nxt and not CALLOUT.match(p) and not p.endswith((":", ".")):
            out.append("### " + esc(p))
            continue
        m = CALLOUT.match(p)
        if m:
            label = m.group(0)[:-1]
            rest = p[len(m.group(0)):].strip()
            out.append(f"> **{esc(label)}:** " + inline(rest, known).replace("\n", "  \n> "))
            continue
        if p.startswith("Answer:"):
            out.append("> **Answer:** " + inline(p[7:].strip(), known).replace("\n", "  \n> "))
            continue
        if all(" — " in l for l in lines):
            items = []
            for l in lines:
                a, b = l.split(" — ", 1)
                items.append(f"- {code_span(a) if is_code(a, spec_field=False) or a.strip() in known else '**' + esc(a) + '**'} — {inline(b, known)}")
            out.append("\n".join(items))
            continue
        mnum = re.match(r"^(\d+)\.\s+(.*)$", lines[0])
        if mnum:
            n, first = mnum.group(1), mnum.group(2)
            rest = lines[1:]
            if rest and (is_code(first, spec_field=False) or first.strip() in known):
                item = f"{n}. {code_span(first)}"
                out.append(item + "\n" + "\n".join("   " + inline(r, known) for r in rest))
                continue
            sent = re.match(r"^([^.!?]{3,60}[.!?])(\s+.*)?$", first)
            if sent and len(sent.group(1).split()) <= 7:
                first_md = f"**{esc(sent.group(1))}**" + (inline(sent.group(2), known) if sent.group(2) else "")
            else:
                first_md = inline(first, known)
            out.append(f"{n}. {first_md}" + ("\n" + "\n".join("   " + inline(r, known) for r in rest) if rest else ""))
            continue
        if len(lines) > 1 and len(lines[0]) <= 40 and not re.search(r"[.,;:!?]$", lines[0]) and not is_code(lines[0], spec_field=False):
            out.append(f"**{esc(lines[0])}**  \n" + "  \n".join(inline(l, known) for l in lines[1:]))
            continue
        out.append("  \n".join(inline(l, known) for l in lines))
    return lead, out


def slugify(s):
    s = s.lower().replace("&", " and ").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70].rstrip("-")


def known_cmds(sp):
    vals = []

    def add(x):
        if isinstance(x, str) and x.strip() and is_code(x):
            vals.append(x.strip())
    for ch in sp.get("chapters", []) or []:
        for r in ch.get("rows", []):
            add(r[0])
    for g in sp.get("rows", []) if sp.get("layout") == "checklist" else []:
        for it in g.get("items", []):
            add(it[1])
    for g in sp.get("groups", []) or []:
        for r in g.get("rows", []):
            add(r[0])
    for b in sp.get("blocks", []) or []:
        for c in b.get("cmds", []):
            add(c)
    for pr in sp.get("pairs", []) or []:
        add(pr.get("bad")); add(pr.get("good"))
    e = sp.get("end") or {}
    if isinstance(e, dict):
        add(e.get("cmd"))
        if e.get("instead"):
            add(e["instead"][1])
    add(sp.get("run"))
    for seg in sp.get("segments", []) or []:
        if is_code(seg[0]):
            vals.append(seg[0])
    return vals


# ---------------------------------------------------------------- build
_missing = [p["n"] for p in posts if p["n"] not in ASSIGN]
if _missing:
    sys.exit(f"Add a topic and section for these posts in topics.py: {_missing}")
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "notes").mkdir(parents=True)
(OUT / "scripts").mkdir()
index, slugs = [], set()
for p in posts:
    n = p["n"]
    sp = specs[str(n)]
    topic, sections = ASSIGN[n]
    if sp["layout"] == "code":
        assert topic == "Python scripts", n
    known = known_cmds(sp)
    end = sp.get("end") or {}
    end_line = (end.get("line") or "").replace("\n", " ").strip()
    lead, body = body_md(p["text"], end_line, known)
    slug = slugify(p["title"])
    while slug in slugs:
        slug += "-2"
    slugs.add(slug)
    tags = [t for t in p["tags"]]
    md = ["---",
          f"id: p{n}",
          f'title: "{p["title"].replace(chr(34), chr(39))}"',
          f"slug: {slug}",
          f"sections: [{', '.join(sections)}]",
          f'topic: "{topic}"',
          f"tags: [{', '.join(tags)}]",
          f'source: "LinkedIn post P{n} · {p["series_name"]} series"',
          f"linkedin_date: {p['date']}",
          f"design: {sp['layout']}"]
    if sp.get("pyfile"):
        md.append(f"script: {sp['pyfile']}")
    md += ["---", "", f"# {esc(p['title'])}", "", inline(lead, known), ""]
    qr = quickref(sp, known)
    if qr:
        md += ["## Quick reference", ""]
        for q in qr:
            md += [q, ""]
    if body:
        md += ["## Explained", ""]
        for b in body:
            md += [b, ""]
    if end_line or end.get("instead") or end.get("cmd"):
        md += ["## In one line", ""]
        if end_line:
            md += [f"> **{esc(end_line)}**" + (f" {inline(end.get('sub', ''), known)}" if end.get("sub") else ""), ""]
        if end.get("cmd") and is_code(end["cmd"]):
            md += ["**Try it**", "", block([end["cmd"]]), ""]
        if end.get("instead"):
            label, val = end["instead"][0], end["instead"][1]
            label = label.capitalize()
            if is_code(val):
                md += [f"**{esc(label)}**", "", block([val]), ""]
            else:
                md += [f"**{esc(label)}:** {inl(val, known)}", ""]
    script_name = sp.get("pyfile")
    if script_name and script_name in SCRIPTS:
        code = SCRIPTS[script_name].read_text(encoding="utf-8").rstrip()
        md += [f"## Script: {script_name}", "", f"Download: [scripts/{script_name}](../scripts/{script_name})", "", block(code.splitlines(), "python"), ""]
    text = "\n".join(md).rstrip() + "\n"
    fname = f"p{n:03d}-{slug}.md"
    (OUT / "notes" / fname).write_text(text, encoding="utf-8")
    index.append(dict(id=f"p{n}", n=n, slug=slug, file=f"notes/{fname}", title=p["title"], sections=sections, topic=topic,
                      tags=tags, series=p["series"], series_name=p["series_name"], design=sp["layout"], linkedin_date=p["date"],
                      script=script_name or "", lead=lead, md=text))
for name, f in sorted(SCRIPTS.items()):
    shutil.copy(f, OUT / "scripts" / name)
json.dump(index, open(OUT / "index.json", "w"), ensure_ascii=False, indent=1)
print(len(index), "notes;", sum("it" in x["sections"] for x in index), "IT;", sum("devsecops" in x["sections"] for x in index), "DevSecOps;",
      sum(len(x["sections"]) == 2 for x in index), "in both;", len(SCRIPTS), "scripts")
