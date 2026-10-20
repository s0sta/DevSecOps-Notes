"""Write README.md for one notes repo from the notes that are in it (front matter of notes/*.md).
Usage: python3 make_readme.py REPO_DIR it|devsecops"""
import pathlib
import re
import sys
from collections import defaultdict

REPOS = {
    "it": {
        "name": "IT-Notes", "title": "IT notes", "other": "DevSecOps-Notes",
        "intro": "Practical IT notes from my LinkedIn posts: Linux, Windows, networks, storage, web servers, databases and security.",
        "other_line": "Cloud, containers, Kubernetes, CI/CD and security automation are in **[DevSecOps-Notes](https://github.com/s0sta/DevSecOps-Notes)**.",
        "alt": "s0sta IT notes: commands and checklists you can copy and run",
        "example": "`lvextend` or `journalctl`",
    },
    "devsecops": {
        "name": "DevSecOps-Notes", "title": "DevSecOps notes", "other": "IT-Notes",
        "intro": "Practical DevSecOps notes from my LinkedIn posts: Docker, Kubernetes, Terraform, CI/CD, cloud, observability and security.",
        "other_line": "Linux, Windows, networks, storage and databases are in **[IT-Notes](https://github.com/s0sta/IT-Notes)**.",
        "alt": "s0sta DevSecOps notes: commands and checklists you can copy and run",
        "example": "`kubectl logs` or `terraform plan`",
    },
}


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    out = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            out[k.strip()] = [x.strip().strip('"') for x in v[1:-1].split(",") if x.strip()]
        else:
            out[k.strip()] = v.strip('"')
    return out


def md_title(t):
    return t.replace("[", "\\[").replace("]", "\\]").replace("*", "\\*").replace("<", "\\<")


def build(repo, section):
    cfg = REPOS[section]
    notes = []
    for f in sorted((repo / "notes").glob("*.md")):
        fm = front_matter(f.read_text(encoding="utf-8"))
        fm["file"] = "notes/" + f.name
        fm["n"] = int(re.sub(r"\D", "", fm.get("id", "0")) or 0)
        notes.append(fm)
    notes.sort(key=lambda x: x["n"])
    scripts = sorted(x.name for x in (repo / "scripts").glob("*.py")) if (repo / "scripts").is_dir() else []
    by = defaultdict(list)
    for n in notes:
        by[n.get("topic", "Other")].append(n)
    both = sum(1 for n in notes if len(n.get("sections", [])) > 1)
    toc = []
    for topic, items in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        toc.append(f"<details>\n<summary><b>{topic.replace('&', '&amp;')}</b> · {len(items)} notes</summary>\n")
        for n in items:
            extra = " · script" if n.get("script") else ""
            toc.append(f"- [{md_title(n.get('title', n['file']))}]({n['file']}) <sub>P{n['n']}{extra}</sub>")
        toc.append("\n</details>\n")
    tools_line = "\ntools/     the converter that turns my LinkedIn post folders into notes for both repos" if (repo / "tools").is_dir() else ""
    readme = f"""<a href="https://s0sta.com"><img src=".github/assets/banner.png" alt="{cfg['alt']}" width="100%"></a>

# {cfg['title']}

{cfg['intro']} Every note has a **quick reference** you can copy, the **full explanation**, and the **script** when there is one.

| Notes | Topics | Scripts |
|:--|:--|:--|
| **{len(notes)}** | **{len(by)}** | **{len(scripts)}** Python scripts, standard library only |

{cfg['other_line']} The {both} notes that fit both are in both repos.

## How to use it

1. Open a topic below and pick a note.
2. Copy a command from a code box. GitHub shows a copy button on every box.
3. Need a script? It is at the end of the note and in [`scripts/`](scripts).

Looking for one command? Use the search box at the top of GitHub, for example {cfg['example']}.

## Notes by topic

{chr(10).join(toc)}

## What is in a note

Each file in [`notes/`](notes) is Markdown with a short header:

```yaml
---
id: p72
title: "9 curl commands for debugging websites"
sections: [it]              # it, devsecops, or [it, devsecops]
topic: "Web servers, TLS & HTTP"
tags: [Linux, curl, SysAdmin]
source: "LinkedIn post P72 · Linux series"
---
```

Then the parts: **Quick reference** (commands, checklists, tables), **Explained** (the full post), **In one line** (the short version) and, for script posts, **Script**.

## Folders

```text
notes/     {len(notes)} notes, one Markdown file each (p072-....md)
scripts/   {len(scripts)} Python scripts from the posts{tools_line}
```

---

Made by **Hosam Hani** ([s0sta](https://github.com/s0sta)) · [s0sta.com](https://s0sta.com) · [LinkedIn](https://www.linkedin.com/in/hosam-hani-abdelati) · Contact: [s0sta.com/#contact](https://s0sta.com/#contact)
"""
    (repo / "README.md").write_text(readme, encoding="utf-8")
    return len(notes), len(scripts), both


if __name__ == "__main__":
    repo, section = pathlib.Path(sys.argv[1]), sys.argv[2]
    print(repo, build(repo, section))
