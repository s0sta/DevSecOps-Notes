"""Build the one-file preview page from the notes index (with notes_tech.js for the tech filters).
Usage: python3 build_preview.py NOTES_OUT TEMPLATE.html DEST.html"""
import json
import pathlib
import re
import sys

out, tpl, dest = (pathlib.Path(a) for a in sys.argv[1:4])
idx = json.load(open(out / "index.json"))
keep = ("id", "n", "slug", "title", "sections", "topic", "tags", "series_name", "design", "script")
data = []
for n in idx:
    md = re.sub(r"^---\n.*?\n---\n\n?", "", n["md"], flags=re.S)
    data.append({**{k: n[k] for k in keep}, "md": md})
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from codeutil import STRONG, WEAK  # noqa: E402
tools = json.dumps({"strong": sorted(STRONG), "weak": sorted(WEAK)}).replace("<", "\\u003c")
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
nums = [n["n"] for n in idx]
scripts = len(list((out / "scripts").glob("*.py"))) + len(list((out / "scripts").glob("*.sh")))
tech = (pathlib.Path(__file__).resolve().parent / "notes_tech.js").read_text()
assert "</" not in tech
html = tpl.read_text()
for k, v in {"__COUNT__": str(len(idx)), "__FIRST__": str(min(nums)), "__LAST__": str(max(nums)), "__SCRIPTS__": str(scripts)}.items():
    html = html.replace(k, v)
assert html.count("__DATA__") == 1 and html.count("__TOOLS__") == 1 and html.count("__TECHJS__") == 1
html = html.replace("__TECHJS__", tech).replace("__TOOLS__", tools).replace("__DATA__", js)
dest.write_text(html)
print(dest, round(len(html.encode()) / 1024), "KB")
