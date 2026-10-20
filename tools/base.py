"""Collect every post: number, series, title, date, design, tags, text (from Texts/pNNN.txt) + the GIF spec."""
import json, re, pathlib, sys
from datetime import datetime
SRC = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2])
specs = json.load(open(OUT / "specs.json"))
SERIES = {}
posts = []
for d in sorted(SRC.glob("*/*/")):
    if not (d / "Texts").is_dir():
        continue
    m = re.match(r"LinkedIn_(.+?)_Series_(\d+)_P(\d+)-P(\d+)", d.name)
    sname, snum = m.group(1).replace("_", " ").replace("CloudDevSecOps", "Cloud / DevSecOps").replace("Linux IT", "Linux + IT"), int(m.group(2))
    md = next(d.glob("*_All_Posts.md")).read_text(encoding="utf-8")
    meta = {}
    for mm in re.finditer(r"^## P(\d+) [^\n]*\n(.*?)```text", md, re.S | re.M):
        n = int(mm.group(1)); blk = mm.group(2)
        dt = re.search(r"\*\*Date:\*\*\s*([^\n,]+?\d{4})", blk)
        meta[n] = dt.group(1).strip() if dt else ""
    for t in sorted(d.glob("Texts/p*.txt"), key=lambda p: int(p.stem[1:])):
        n = int(t.stem[1:])
        text = t.read_text(encoding="utf-8").strip()
        tags = []
        lines = text.splitlines()
        if lines and lines[-1].lstrip().startswith("#"):
            tags = re.findall(r"#(\w+)", lines[-1])
        dstr = meta.get(n, "")
        iso = ""
        for fmt in ("%A %d %B %Y", "%a %d %b %Y", "%A %d %b %Y", "%d %B %Y"):
            try:
                iso = datetime.strptime(re.sub(r"\s+", " ", dstr.replace(",", "")), fmt).date().isoformat(); break
            except ValueError:
                pass
        sp = specs.get(str(n), {})
        posts.append(dict(n=n, series=snum, series_name=sname, folder=d.name, title=sp.get("topic") or lines[0][:80],
                          design=sp.get("layout", "?"), date=iso, date_raw=dstr, tags=tags, text=text,
                          spec_text_same=(sp.get("text", "").strip() == "\n".join(l for l in lines if not l.lstrip().startswith("#") or not re.match(r"^#\w", l.strip())).strip())))
posts.sort(key=lambda p: p["n"])
json.dump(posts, open(OUT / "posts.json", "w"), ensure_ascii=False, indent=1)
print(len(posts), "posts;", sum(1 for p in posts if not p["date"]), "without date;", sum(1 for p in posts if not p["spec_text_same"]), "text differs from spec")
for p in posts[:3] + posts[-2:]:
    print(p["n"], p["series"], p["design"], p["date"], p["title"], p["tags"])
