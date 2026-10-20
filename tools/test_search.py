"""Try many searches on the preview page and report counts, errors and screenshots."""
import json
import pathlib
import sys
from playwright.sync_api import sync_playwright

page_path = pathlib.Path(sys.argv[1]).resolve()
shots = pathlib.Path(sys.argv[2]); shots.mkdir(exist_ok=True)
wrapped = page_path.with_name("_test_wrapped.html")
wrapped.write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                   '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
                   + page_path.read_text() + '</body></html>')
R = {"errors": [], "queries": {}}


def block_fonts(pg):
    pg.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    pg.route("**/fonts.gstatic.com/**", lambda r: r.abort())


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    block_fonts(pg)
    pg.on("pageerror", lambda e: R["errors"].append(str(e)))
    pg.on("console", lambda m: m.type == "error" and "ERR_FAILED" not in m.text and R["errors"].append(m.text))
    pg.goto(wrapped.as_uri())
    pg.wait_for_timeout(300)

    def q(text):
        pg.fill("#q", text)
        pg.wait_for_timeout(160)
        items = pg.eval_on_selector_all(".item .t", "els => els.slice(0,3).map(e => e.textContent)")
        chips = pg.eval_on_selector_all("#active .fchip", "els => els.map(e => e.innerText.replace(/\\s+/g,' ').replace(' ×',''))")
        n = pg.eval_on_selector_all(".item", "els => els.length")
        R["queries"][text] = {"n": n, "first": items, "chips": chips}
        return n

    for text in ["", "@kubectl", "#lvextend", "--previous", "-r", "-rf", "topic:kubernetes --dry-run", "type:quiz", "has:script", "p:72-91", "date:2027",
                 "@kubectl !@helm", "@helm", "@kustomize", "@helm OR @kustomize", '"disk full"', "series:data", "in:both", "tag:kubernetes",
                 'topic:"Docker & containers" type:commands', "restart", "nginx reload", "@Get-ADUser", "@sql", "has:quiz type:quiz", "!has:commands",
                 "date:2027-03..2027-08", "p:>360", "series:linux", "series:linux-it", "@kube", "#\"kubectl logs\"", "tag:linux"]:
        q(text)
    # scope: restart in code only
    q("restart")
    pg.click("#advbtn")
    pg.click('#f-scope [data-v="code"]')
    pg.wait_for_timeout(120)
    R["restart_code_scope"] = pg.eval_on_selector_all(".item", "els => els.length")
    pg.click('#f-scope [data-v="title"]')
    pg.wait_for_timeout(120)
    R["restart_title_scope"] = pg.eval_on_selector_all(".item", "els => els.length")
    pg.click('#f-scope [data-v="all"]')
    # filter by topic chip, then a second filter in the panel
    pg.fill("#q", "")
    pg.wait_for_timeout(120)
    pg.click('#topics [data-v="Kubernetes"]')
    pg.wait_for_timeout(120)
    R["topic_chip_query"] = pg.input_value("#q")
    R["topic_chip_n"] = pg.eval_on_selector_all(".item", "els => els.length")
    pg.click('#f-type [data-v="commands"]')
    pg.wait_for_timeout(120)
    R["topic_plus_type_query"] = pg.input_value("#q")
    R["topic_plus_type_n"] = pg.eval_on_selector_all(".item", "els => els.length")
    pg.click('#topics [data-v="Docker & containers"]')
    pg.wait_for_timeout(120)
    R["two_topics_type_query"] = pg.input_value("#q")
    R["two_topics_type_n"] = pg.eval_on_selector_all(".item", "els => els.length")
    pg.fill("#p-from", "200"); pg.dispatch_event("#p-from", "change")
    pg.wait_for_timeout(120)
    R["with_p_from"] = pg.input_value("#q")
    pg.screenshot(path=str(shots / "s-desk-adv.png"))
    # remove a chip
    pg.click("#active .fchip:first-child button")
    pg.wait_for_timeout(120)
    R["after_remove_chip"] = pg.input_value("#q")
    pg.click('[data-act="reset"]')
    pg.click("#advbtn")
    # suggestions
    pg.click("#q")
    pg.wait_for_timeout(120)
    R["tips_open"] = pg.is_visible("#sugg")
    pg.type("#q", "@kub", delay=30)
    pg.wait_for_timeout(150)
    R["sugg_at_kub"] = pg.eval_on_selector_all("#sugg .opt .l", "els => els.map(e => e.textContent)")
    pg.screenshot(path=str(shots / "s-desk-sugg.png"))
    pg.keyboard.press("Tab")
    pg.wait_for_timeout(150)
    R["after_tab"] = pg.input_value("#q")
    pg.type("#q", "--pr", delay=30)
    pg.wait_for_timeout(150)
    R["sugg_opt"] = pg.eval_on_selector_all("#sugg .opt .l", "els => els.map(e => e.textContent)")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(150)
    R["after_enter_opt"] = pg.input_value("#q")
    pg.type("#q", "topic:", delay=30)
    pg.wait_for_timeout(150)
    R["sugg_topic"] = pg.eval_on_selector_all("#sugg .opt .l", "els => els.slice(0,4).map(e => e.textContent)")
    pg.keyboard.press("Escape")
    pg.fill("#q", "kubectl --previous")
    pg.wait_for_timeout(150)
    pg.keyboard.press("Escape")
    pg.click(".item button >> nth=0")
    pg.wait_for_timeout(500)
    R["marks"] = pg.eval_on_selector_all("#note mark", "els => els.length")
    R["hits_text"] = pg.inner_text("#note .hits") if pg.is_visible("#note .hits") else None
    pg.click('[data-act="nexthit"]')
    pg.wait_for_timeout(300)
    R["hits_text2"] = pg.inner_text("#note .hits")
    pg.screenshot(path=str(shots / "s-desk-note.png"))
    pg.evaluate("window.scrollTo(0,0)")
    pg.emulate_media(color_scheme="dark")
    pg.fill("#q", "@kubectl -n")
    pg.wait_for_timeout(200)
    pg.click("#helpbtn")
    pg.wait_for_timeout(100)
    pg.screenshot(path=str(shots / "s-desk-dark-help.png"))
    # phone
    ph = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pp = ph.new_page(); block_fonts(pp)
    pp.on("pageerror", lambda e: R["errors"].append("phone: " + str(e)))
    pp.goto(wrapped.as_uri())
    pp.wait_for_timeout(300)
    R["phone_overflow"] = pp.evaluate("document.documentElement.scrollWidth - innerWidth")
    pp.screenshot(path=str(shots / "s-phone-top.png"))
    pp.click("#advbtn")
    pp.wait_for_timeout(150)
    R["phone_overflow_adv"] = pp.evaluate("document.documentElement.scrollWidth - innerWidth")
    pp.screenshot(path=str(shots / "s-phone-adv.png"), full_page=False)
    pp.click("#advbtn")
    pp.tap("#q")
    pp.type("#q", "@doc", delay=30)
    pp.wait_for_timeout(150)
    R["phone_overflow_sugg"] = pp.evaluate("document.documentElement.scrollWidth - innerWidth")
    pp.screenshot(path=str(shots / "s-phone-sugg.png"))
    pp.keyboard.press("Tab")
    pp.keyboard.press("Enter")
    pp.wait_for_timeout(200)
    pp.screenshot(path=str(shots / "s-phone-results.png"))
    pp.tap(".item button >> nth=0")
    pp.wait_for_timeout(500)
    R["phone_overflow_note"] = pp.evaluate("document.documentElement.scrollWidth - innerWidth")
    pp.screenshot(path=str(shots / "s-phone-note.png"))
    b.close()
wrapped.unlink()
print(json.dumps(R, indent=1, ensure_ascii=False))
