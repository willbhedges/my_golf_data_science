"""courses/qa_page.js <set> on a single-set page (sycamore_ridge qa_rebuild.md): the set picker is hidden, so the
run must check the page's own set instead of timing out on the click. Needs node + playwright + chromium; skipped
otherwise."""
import json
import os
import shutil
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
QA = os.path.join(HERE, "..", "courses", "qa_page.js")
IMG = "data:image/png;base64," + "A" * 1200

PAGE = """<!doctype html><html><body>
<div id="setRow" style="display:none"><div id="set"><button data-v="osm_back">osm_back</button></div></div>
<div id="src"></div><select id="start"><option>1</option><option>10</option></select><span id="windLbl">calm</span>
<button id="nextTop">next</button>
<section class="hole"><span id="hNo">1</span><span id="topNo">1</span><span id="hPar">Par 4</span>
<span id="hPlay">Driver</span><svg id="ov"><image href="%s"/></svg>
<table id="hTable"><tbody><tr><td>Driver</td></tr></tbody></table></section>
<script>
var D = {holes: [{key: "1"}, {key: "2"}], sets: ["osm_back"], days: []}, i = 0;
document.getElementById("nextTop").onclick = function () { i = (i + 1) %% 2;
  document.getElementById("hNo").textContent = String(i + 1); };
</script></body></html>""" % IMG


def _have_playwright():
    if not shutil.which("node"):
        return False
    r = subprocess.run(["node", "-e", "try{require('playwright')}catch(e){require('/opt/node22/lib/node_modules/playwright')}"],
                       capture_output=True)
    return r.returncode == 0 and (os.path.exists("/opt/pw-browsers/chromium") or os.environ.get("PW_CHROMIUM"))


@pytest.mark.skipif(not _have_playwright(), reason="node / playwright / chromium not available")
def test_set_argument_on_a_single_set_page(tmp_path):
    page = tmp_path / "page.html"
    page.write_text(PAGE)
    out = tmp_path / "out"
    r = subprocess.run(["node", QA, str(page), str(out), "Black"], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    rep = json.loads((out / "qa.json").read_text())
    assert "picker hidden" in rep["set_note"]
    assert len(rep["views"]["phone"]["holes"]) == 2 and "holes checked: 2" in r.stdout
