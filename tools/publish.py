"""Copy built notes into the two repos and refresh both READMEs.
A note goes to every repo of its sections (a note in both sections goes to both).
Scripts go with their notes; a script with no note (a bonus script) goes to both.
Nothing is deleted from the repos: new files are added, changed files are replaced.
Usage: python3 publish.py OUT_DIR IT_REPO_DIR DEVSECOPS_REPO_DIR"""
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from make_readme import build, front_matter  # noqa: E402

out, it_repo, dso_repo = (pathlib.Path(a) for a in sys.argv[1:4])
repos = {"it": it_repo, "devsecops": dso_repo}
used = set()
count = {"it": 0, "devsecops": 0}
for f in sorted((out / "notes").glob("*.md")):
    fm = front_matter(f.read_text(encoding="utf-8"))
    for sec in fm.get("sections", []):
        dest = repos[sec]
        (dest / "notes").mkdir(parents=True, exist_ok=True)
        shutil.copy(f, dest / "notes" / f.name)
        count[sec] += 1
        if fm.get("script"):
            used.add(fm["script"])
            (dest / "scripts").mkdir(exist_ok=True)
            shutil.copy(out / "scripts" / fm["script"], dest / "scripts" / fm["script"])
for s in sorted((out / "scripts").glob("*.py")):
    if s.name not in used:
        for dest in repos.values():
            (dest / "scripts").mkdir(exist_ok=True)
            shutil.copy(s, dest / "scripts" / s.name)
for sec, dest in repos.items():
    print(sec, "copied", count[sec], "notes; README:", build(dest, sec))
