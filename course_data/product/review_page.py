"""review.json (verify.py, schema review/1) -> the self-contained phone review page.

  python3 course_data/product/review_page.py course_data/packages/<slug>/out/review/review.json [out.html]

The page (review_page_template.html) has no network calls: the NAIP crops are data URIs inside the data blob,
the plan consequences of every answer are precomputed by verify.py, answers persist in localStorage and leave
the page only through the "Copy answers" button (JSON for apply_answers.py). Green items are listed without
images to keep the page small.
"""
import html as _html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "review_page_template.html")

KEEP = ("id", "hole", "type", "severity", "par", "lie", "side", "question", "detail", "options", "crop", "toward",
        "along", "edge", "confidence")


def _slim_outcome(o):
    if not o:
        return None
    return {k: o[k] for k in ("pick", "aim", "d_ev", "club_changed", "aim_shift", "severity") if k in o}


def page_data(rv):
    items = []
    for it in rv["items"]:
        d = {k: it[k] for k in KEEP if k in it}
        opts = []
        for o in it.get("options", []):
            oo = {k: o[k] for k in ("answer", "label", "drag", "text") if k in o}
            oo["outcome"] = _slim_outcome(o.get("outcome"))
            if "samples" in o:
                oo["samples"] = [dict({k: s[k] for k in ("name", "dx", "dy", "shift", "text") if k in s},
                                      outcome=_slim_outcome(s.get("outcome"))) for s in o["samples"]]
            opts.append(oo)
        d["options"] = opts
        if it["severity"] == "green":
            d.pop("crop", None)
        items.append(d)
    holes = {k: dict(par=v["par"], base=v.get("base")) for k, v in rv["holes"].items()}
    return dict(course=rv["course"], slug=rv["slug"], tee_set=rv["tee_set"], built=rv["built"],
                counts=rv["counts"], imagery=rv.get("imagery"), holes=holes, items=items,
                settings=dict(n=rv["settings"]["n"]))


def _short(name):
    for w in (" Golf Course", " Golf Club", " Country Club", " Golf Links"):
        name = (name or "").replace(w, "")
    return name.strip() or "Course"


def build(rv, out_html):
    data = page_data(rv)
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    title = f"{_short(rv['course'])} Pre-Round Check"
    page = open(TEMPLATE).read()
    page = page.replace("__TITLE__", _html.escape(title)).replace("/*__DATA__*/null", blob)
    os.makedirs(os.path.dirname(os.path.abspath(out_html)), exist_ok=True)
    with open(out_html, "w") as fh:
        fh.write(page)
    return out_html


if __name__ == "__main__":
    src = sys.argv[1]
    rv = json.load(open(src))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(src), "index.html")
    print(build(rv, out))
