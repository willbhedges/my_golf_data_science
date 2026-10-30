"""The national course index for the app (course_index/1): course_data/library/us_courses.json.gz -> a compact,
gzip + base64 string that build_app.py puts into course_index.js (placeholder /*__COURSE_INDEX__*/null).

One line per open course: "name|city|ST|lat|lon|osm|holes|tier" (osm "w123" / "r45" / "n6", lat/lon 4 decimals),
sorted by state then name. ~16 k courses come to roughly 0.4 MB of base64 in the page.

  python course_data/app/course_index.py            # print the size it would add
"""
import base64
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
US = os.path.join(HERE, "..", "library", "us_courses.json.gz")
PLACEHOLDER = "/*__COURSE_INDEX__*/null"


def compact(path=US):
    if not os.path.exists(path):
        return None
    with gzip.open(path, "rt") as fh:
        doc = json.load(fh)
    f = {k: i for i, k in enumerate(doc["fields"])}
    lines = []
    for r in doc["rows"]:
        if r[f["closed"]]:
            continue
        name, city = (str(r[f[k]] or "").replace("|", "/").replace("\n", " ") for k in ("name", "city"))
        typ, _, oid = str(r[f["osm"]]).partition("/")
        lines.append("|".join([name, city, r[f["state"]], f"{r[f['lat']]:.4f}", f"{r[f['lon']]:.4f}",
                               (typ[:1] + oid) if oid else "", str(r[f["holes"]] or ""), r[f["tier"]]]))
    raw = "\n".join(lines).encode()
    b64 = base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode()
    return dict(schema="course_index/1", n=len(lines), built=doc.get("built"), b64=b64)


def inject(js_text, path=US):
    """replace the placeholder in the concatenated engine JS; returns (text, info)"""
    if PLACEHOLDER not in js_text:
        return js_text, None
    d = compact(path)
    return js_text.replace(PLACEHOLDER, json.dumps(d, separators=(",", ":")) if d else "null"), d


if __name__ == "__main__":
    d = compact()
    print("no us_courses.json.gz yet" if not d else f"{d['n']} courses, {len(d['b64']) / 1e6:.2f} MB base64")
