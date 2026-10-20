"""Open the preview, click through every note in both sections, report errors and odd rendering, take screenshots."""
import json
import pathlib
import sys
from playwright.sync_api import sync_playwright

page_path = pathlib.Path(sys.argv[1]).resolve()
shots = pathlib.Path(sys.argv[2]); shots.mkdir(exist_ok=True)
# the published page is wrapped in a skeleton with charset + viewport; do the same for the test
wrapped = page_path.with_name("_test_wrapped.html")
wrapped.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                   '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
                   + page_path.read_text() + '</body></html>')
report = {"errors": [], "odd": []}
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    pg.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    pg.on("pageerror", lambda e: report["errors"].append(str(e)))
    pg.on("console", lambda m: m.type == "error" and "ERR_FAILED" not in m.text and report["errors"].append(m.text))
    pg.goto(wrapped.as_uri())
    pg.wait_for_timeout(300)
    report["it_count"] = pg.inner_text("#shown")
    pg.screenshot(path=str(shots / "desk-light.png"))
    for sec in ("it", "devsecops"):
        pg.click(f'.seg button[data-sec="{sec}"]')
        ids = pg.eval_on_selector_all(".item button", "els => els.map(e => e.dataset.id)")
        report[sec + "_ids"] = len(ids)
        for i in ids:
            pg.click(f'.item button[data-id="{i}"]')
            t = pg.inner_text("#note .md")
            h = pg.inner_html("#note .md")
            for bad in ("**", "``", "\\`", "\\*", "\\<", "\\|", "](", "~~~", "```"):
                if bad in t:
                    report["odd"].append((i, bad, t[max(0, t.find(bad) - 50): t.find(bad) + 50].replace("\n", " ")))
            if "<h3" not in h:
                report["odd"].append((i, "no-sections", ""))
    # search + topic
    pg.click('.seg button[data-sec="it"]')
    pg.fill("#q", "lvextend")
    pg.wait_for_timeout(300)
    report["search_lvextend"] = pg.inner_text("#shown")
    pg.fill("#q", "")
    pg.wait_for_timeout(300)
    pg.click('#topics .chip:nth-child(2)')
    report["topic_click"] = pg.inner_text("#shown")
    # a note with a script
    pg.click('#topics .chip:first-child')
    pg.evaluate("location.hash = \"p182\"")
    pg.wait_for_timeout(300)
    report["p182_has_expand"] = pg.locator('[data-act="expand"]').count()
    pg.screenshot(path=str(shots / "desk-script.png"), full_page=False)
    pg.evaluate("location.hash = \"p72\"")
    pg.wait_for_timeout(300)
    pg.emulate_media(color_scheme="dark")
    pg.screenshot(path=str(shots / "desk-dark.png"))
    # phone
    ph = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pp = ph.new_page()
    pp.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    pp.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    pp.on("pageerror", lambda e: report["errors"].append("phone: " + str(e)))
    pp.goto(wrapped.as_uri())
    pp.wait_for_timeout(300)
    report["phone_overflow_list"] = pp.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    pp.screenshot(path=str(shots / "phone-list.png"))
    pp.click(".item button >> nth=0")
    pp.wait_for_timeout(200)
    report["phone_overflow_note"] = pp.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    pp.screenshot(path=str(shots / "phone-note.png"))
    pp.emulate_media(color_scheme="dark")
    pp.click('[data-act="back"]')
    pp.click('.seg button[data-sec="devsecops"]')
    pp.click(".item button >> nth=3")
    pp.wait_for_timeout(200)
    report["phone_overflow_note2"] = pp.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    pp.screenshot(path=str(shots / "phone-note-dark.png"))
    b.close()
wrapped.unlink()
report["odd_count"] = len(report["odd"])
report["odd"] = report["odd"][:25]
print(json.dumps(report, indent=1, ensure_ascii=False))
