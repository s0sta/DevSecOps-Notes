# tools

These scripts turn my LinkedIn post folders into the notes of **two repos**: [IT-Notes](https://github.com/s0sta/IT-Notes) and [DevSecOps-Notes](https://github.com/s0sta/DevSecOps-Notes).
They read the GIF builder files with Python's `ast` module and never run them. GIFs are not used, only the text, the GIF data (commands, tables, quiz answers) and the scripts.

## What each file does

| File | Job |
|:--|:--|
| `load_specs.py` | Reads the `POSTS[n] = dict(...)` data from `Code/posts_*.py` into `specs.json` |
| `base.py` | Reads `Texts/pNNN.txt` and the dates in `*_All_Posts.md` into `posts.json` |
| `topics.py` | The topic and section of every post: `i` = IT, `d` = DevSecOps, `b` = both |
| `codeutil.py` | Finds commands inside text, so they become code |
| `make_notes.py` | Writes `notes/*.md`, copies `scripts/*.py` and `scripts/*.sh`, writes `index.json` |
| `check_md.py` | Renders every note and lists Markdown problems |
| `publish.py` | Copies each note into the repo of its section (both = both repos) and refreshes both READMEs |
| `make_readme.py` | Writes one repo's README from the notes that are in it |
| `build_preview.py` + `preview_template.html` | One HTML page to read, search and copy all notes |
| `test_preview.py`, `test_search.py` | Click through the preview page, try many searches, take screenshots |

## Add new posts

Needs Python 3.10+. For the checks: `pip install "markdown-it-py[linkify]" pyyaml playwright`.

```bash
# clone IT-Notes and DevSecOps-Notes next to each other, then work in DevSecOps-Notes
# 1. put the extracted series folders in src/, same layout as the zips:
#    src/LinkedIn_<Name>_Series_<N>_P<a>-P<b>/LinkedIn_<Name>_Series_<N>_P<a>-P<b>/{Texts,Code,Scripts}
mkdir -p build out
python3 tools/load_specs.py src build/specs.json
python3 tools/base.py src build
# 2. add the new post numbers to RAW in tools/topics.py, e.g. "372 K8 d"
python3 tools/make_notes.py src build out
python3 tools/check_md.py out/notes
# 3. copy the notes into both repos and refresh both READMEs
python3 tools/publish.py out ../IT-Notes .
```

`make_notes.py` empties its output folder first, so never point it at `notes/` directly.
`publish.py` only adds or replaces files. It never deletes a note.
To fix a slip in the source data, add it to `FIXES` at the top of `make_notes.py`.
