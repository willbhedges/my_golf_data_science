"""Workstream B (zero-tap): outside evidence of which hole is which, without golfer input.

Runs on GitHub Actions (the sandbox cannot reach course websites). One shard of courses per job.
For each course:

  1. sources   - course website (OSM `website` tag): robots.txt-checked crawl of the course / tour / hole /
                 layout / scorecard pages (<= MAX_PAGES pages, >= 1 s apart); golfify.io __NEXT_DATA__ and
                 OpenGolfAPI detail, scanned for any per-hole coordinates.
  2. images    - candidate layout maps and per-hole images are downloaded to a temp dir (never committed).
  3. register  - each image is matched to the course's NAIP mosaic (RootSIFT + ratio test + RANSAC
                 homography, multi-scale NAIP, rotation-free since SIFT is rotation invariant).
  4. read      - a registered per-hole image gives that hole's footprint and its tee/green anchors (image
                 bottom/top centre after the hole-image convention is checked against the footprint shape);
                 a registered overview map is OCR'd (tesseract) for the numbers 1-18, each placed on the ground.
  5. evidence  - hole_evidence/1 per course (see README.md); only derived positions + source URLs are kept.

Usage: python probe.py --slugs a,b,c --out course_data/zero_tap/evidence/runs/<run>
"""
import argparse
import hashlib
import html as htmlmod
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.robotparser
from urllib.parse import urljoin, urlparse, quote_plus

import numpy as np
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GEN = os.path.join(ROOT, "course_data", "generalize")

UA_TOKEN = "golf-hole-evidence-research"
# Browser-like (many club sites sit behind WAFs that 403 bare bots) but self-identifying; robots.txt is checked
# for both our token and "*".
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
      f"({UA_TOKEN}/0.1; +https://github.com/willbhedges/my_golf_data_science)")
GUESS_PATHS = ("/course-tour", "/hole-by-hole", "/the-course", "/course", "/golf/course-tour", "/golf/the-course",
               "/course-layout", "/course-map", "/scorecard", "/golf/hole-by-hole", "/golf", "/course-info")
MAX_PAGES = 40
MAX_IMAGES = 60
PAGE_DELAY_S = 1.0
IMG_MAX_BYTES = 8_000_000

COURSE_LINK = re.compile(r"(?i)hole|tour|course|layout|map|score|card|flyover|yardage|\.pdf|the-?course|golf")
SKIP_LINK = re.compile(r"(?i)instagram|facebook|twitter|youtube\.com/(?!watch)|tiktok|linkedin|foreup|teesnap|"
                       r"chronogolf|golfnow|teeitup|mailto:|tel:|login|account|cart|checkout|book|tee-?time|"
                       r"event|wedding|banquet|menu|dining|news|blog|calendar|careers|jobs|privacy|terms|"
                       r"membership|lesson|league|outing|gift|shop|\.css|\.js(\?|$)|\.xml|\.zip|\.docx?$")
HOLE_NUM = re.compile(r"(?i)(?:hole|hl|no)[\s_\-#.]*0?(\d{1,2})(?!\d)")
LAYOUT_WORD = re.compile(r"(?i)layout|course[\s_\-]?map|routing|overview|site[\s_\-]?map|aerial|"
                         r"map[\s_\-]?of|course[\s_\-]?layout|yardage[\s_\-]?guide|overhead|birds?[\s_\-]?eye")
SCORE_WORD = re.compile(r"(?i)score[\s_\-]?card")


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def jload(p, default=None):
    try:
        with open(p) as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return default


# ----------------------------------------------------------------------------- polite HTTP
class Polite:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        self.robots = {}
        self.last = {}
        self.log = []

    def allowed(self, url):
        p = urlparse(url)
        host = p.netloc
        if host not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                r = self.s.get(f"{p.scheme}://{host}/robots.txt", timeout=20)
                if r.status_code in (401, 403):
                    rp.disallow_all = True
                elif r.status_code >= 400:
                    rp.allow_all = True
                else:
                    rp.parse(r.text.splitlines())
            except Exception:  # noqa: BLE001
                rp.allow_all = True
            self.robots[host] = rp
        rp = self.robots[host]
        return rp.can_fetch(UA_TOKEN, url) and rp.can_fetch("*", url)

    def get(self, url, stream=False, timeout=30):
        if not self.allowed(url):
            self.log.append(dict(url=url, status="robots_disallow"))
            return None
        host = urlparse(url).netloc
        wait = PAGE_DELAY_S - (time.time() - self.last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        try:
            r = self.s.get(url, timeout=timeout, stream=stream, allow_redirects=True)
        except Exception as e:  # noqa: BLE001
            self.log.append(dict(url=url, status=f"error {type(e).__name__}"))
            return None
        finally:
            self.last[host] = time.time()
        self.log.append(dict(url=url, status=r.status_code))
        return r


# ----------------------------------------------------------------------------- website crawl
def links_of(base, text):
    out = []
    for m in re.finditer(r'(?is)<a\b[^>]*href\s*=\s*["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', text):
        href, label = m.group(1), re.sub(r"<[^>]+>", " ", m.group(2))
        out.append((urljoin(base, htmlmod.unescape(href.strip())), " ".join(label.split())[:80]))
    return out


def images_of(base, text):
    out = []
    for m in re.finditer(r"(?is)<img\b[^>]*>", text):
        tag = m.group(0)
        src = None
        for attr in ("data-src", "data-lazy-src", "data-original", "src"):
            mm = re.search(attr + r'\s*=\s*["\']([^"\']+)["\']', tag)
            if mm and not mm.group(1).startswith("data:"):
                src = mm.group(1)
                break
        ss = re.search(r'srcset\s*=\s*["\']([^"\']+)["\']', tag)
        if ss:                                    # largest srcset candidate
            cands = [c.strip().split() for c in ss.group(1).split(",") if c.strip()]
            best = max(cands, key=lambda c: int(re.sub(r"\D", "", c[1]) or 0) if len(c) > 1 else 0)
            src = best[0]
        if not src:
            continue
        alt = re.search(r'alt\s*=\s*["\']([^"\']*)["\']', tag)
        out.append((urljoin(base, htmlmod.unescape(src)), (alt.group(1) if alt else "")[:120]))
    # CSS background images (sliders, hole galleries)
    for m in re.finditer(r"""(?i)background(?:-image)?\s*:\s*url\(\s*['"]?([^'")]+)""", text):
        out.append((urljoin(base, htmlmod.unescape(m.group(1))), ""))
    # anchors straight to images (lightbox galleries)
    for m in re.finditer(r"""(?i)href\s*=\s*["']([^"']+\.(?:jpe?g|png|webp))["']""", text):
        out.append((urljoin(base, htmlmod.unescape(m.group(1))), ""))
    return out


def hole_of(*texts):
    for t in texts:
        if not t:
            continue
        t2 = re.sub(r"(?i)\d{2,4}x\d{2,4}|\b(19|20)\d{2}\b", " ", t)       # sizes, years
        for m in HOLE_NUM.finditer(t2):
            n = int(m.group(1))
            if 1 <= n <= 18:
                return n
    return None


def same_site(u, host):
    h = urlparse(u).netloc.lower().lstrip("www.")
    return h == host.lower().lstrip("www.") or h.endswith("." + host.lower().lstrip("www."))


def crawl_site(P, website):
    if not website.startswith("http"):
        website = "https://" + website
    r = P.get(website)
    res = dict(website=website, reachable=False, robots_ok=P.allowed(website), pages=[], hole_pages={},
               images=[], pdfs=[], videos=[])
    if r is None or r.status_code >= 400 or "html" not in r.headers.get("content-type", "html"):
        res["status"] = None if r is None else r.status_code
        return res
    res["reachable"] = True
    host = urlparse(r.url).netloc
    queue = [(r.url, "", 0, r)]
    seen = {r.url, website}
    home_links = links_of(r.url, r.text)
    res["home_links"] = len(home_links)
    res["home_links_sample"] = [u for u, _ in home_links if same_site(u, host)][:40]
    res["home_bytes"] = len(r.text)
    root = f"{urlparse(r.url).scheme}://{host}"
    for g in GUESS_PATHS:
        if root + g not in seen:
            seen.add(root + g)
            queue.append((root + g, "", 1, None))
    imgs = {}
    while queue and len(res["pages"]) < MAX_PAGES:
        url, label, depth, rr = queue.pop(0)
        if rr is None:
            rr = P.get(url)
        if rr is None or rr.status_code >= 400:
            continue
        ctype = rr.headers.get("content-type", "")
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            res["pdfs"].append(dict(url=url, label=label, bytes=len(rr.content), hole=hole_of(url, label),
                                    _content=rr.content))
            continue
        if "html" not in ctype:
            continue
        text = rr.text
        page_hole = hole_of(url, label)
        res["pages"].append(dict(url=url, label=label, depth=depth, hole=page_hole))
        if page_hole:
            res["hole_pages"].setdefault(str(page_hole), url)
        for iu, alt in images_of(url, text):
            if iu in imgs or not re.search(r"(?i)\.(jpe?g|png|webp|gif)(\?|$)|/image|wp-content|cdn", iu):
                continue
            imgs[iu] = dict(url=iu, alt=alt, page=url, page_hole=page_hole, img_hole=hole_of(
                urlparse(iu).path.rsplit("/", 1)[-1], alt))
        for m in re.finditer(r"(?i)(?:youtube\.com/(?:embed/|watch\?v=)|youtu\.be/|player\.vimeo\.com/video/)"
                             r"[\w\-]+", text):
            if m.group(0) not in res["videos"]:
                res["videos"].append(m.group(0))
        if depth >= 2:
            continue
        for lu, lt in links_of(url, text):
            lu = lu.split("#")[0]
            if lu in seen:
                continue
            is_pdf = lu.lower().split("?")[0].endswith(".pdf")
            if not (same_site(lu, host) or is_pdf):
                continue
            if SKIP_LINK.search(lu) or not (COURSE_LINK.search(lu) or COURSE_LINK.search(lt)):
                continue
            seen.add(lu)
            pri = 0 if (hole_of(lu, lt) or re.search(r"(?i)tour|hole|layout|map", lu + lt)) else 1
            queue.append((lu, lt, depth + 1, None))
            queue.sort(key=lambda q: (q[2] if q[3] is not None else 0,
                                      0 if (hole_of(q[0], q[1]) or re.search(r"(?i)tour|hole|layout|map|flyover",
                                                                            q[0] + q[1])) else 1))
            _ = pri
    for im in imgs.values():
        t = im["url"] + " " + im["alt"]
        im["kind"] = ("hole" if (im["img_hole"] or (im["page_hole"] and not re.search(r"(?i)logo|icon", t)))
                      else "layout" if LAYOUT_WORD.search(t) else "scorecard" if SCORE_WORD.search(t) else "other")
        im["hole"] = im["img_hole"] or im["page_hole"]
    res["images"] = list(imgs.values())
    return res


# ----------------------------------------------------------------------------- third-party JSON scans
LATLON_KEY = re.compile(r"(?i)^(lat|latitude|lng|lon|longitude|coordinates|geometry|location|point|gps|"
                        r"tee_?(lat|lng|location|point|coords?)|green_?(lat|lng|location|center|centre|front|back)|"
                        r"center|centre|front|back|polygon|geojson)$")


def scan_geo_keys(obj, path="", out=None, depth=0):
    out = out if out is not None else {}
    if depth > 12:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            if LATLON_KEY.match(str(k)) and v not in (None, "", [], {}):
                gp = re.sub(r"\[\d+\]", "[]", p)
                out[gp] = out.get(gp, 0) + 1
            scan_geo_keys(v, p, out, depth + 1)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:40]):
            scan_geo_keys(v, f"{path}[{i}]", out, depth + 1)
    return out


def golfify_probe(P, slug):
    sc = jload(os.path.join(GEN, "courses", slug, "scorecard.json"), {}) or {}
    urls = [c.get("url") for c in sc.get("cards", []) if c.get("source") == "golfify" and c.get("url")]
    if not urls:
        return dict(status="no golfify url in scorecard.json")
    r = P.get(urls[0])
    if r is None or r.status_code != 200:
        return dict(url=urls[0], status=None if r is None else r.status_code)
    m = re.search(r'(?is)<script[^>]*__NEXT_DATA__[^>]*>(.*?)</script>', r.text)
    if not m:
        return dict(url=urls[0], status="no __NEXT_DATA__")
    d = json.loads(m.group(1))
    keys = scan_geo_keys(d)
    hole_keys = {k: v for k, v in keys.items() if re.search(r"(?i)hole", k)}
    pp = d.get("props", {}).get("pageProps", {})
    sample_hole = None
    for t in pp.get("tees") or []:
        hi = t.get("holeInformation") or []
        if hi:
            sample_hole = sorted(hi[0].keys())
            break
    return dict(url=urls[0], status=200, website=(pp.get("facility") or {}).get("website"),
                geo_keys=keys, hole_geo_keys=hole_keys, hole_fields=sample_hole,
                page_props=sorted(pp.keys())[:40])


def _ll(v):
    """Any common coordinate shape -> [lon, lat] or None."""
    if v is None:
        return None
    if isinstance(v, dict):
        for la, lo in (("lat", "lng"), ("lat", "lon"), ("latitude", "longitude")):
            if la in v and lo in v:
                try:
                    return [float(v[lo]), float(v[la])]
                except (TypeError, ValueError):
                    return None
        if v.get("type") == "Point":
            return _ll(v.get("coordinates"))
        for k in ("center", "centre", "middle", "coords", "coordinates", "point"):
            if k in v:
                return _ll(v[k])
        return None
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        a, b = float(v[0]), float(v[1])
        return [a, b] if abs(a) > abs(b) else [b, a]          # US: |lon| > |lat|
    if isinstance(v, list) and v and isinstance(v[0], (dict, list)):
        return _ll(v[0])
    return None


def opengolfapi_probe(P, slug):
    raw = os.path.join(GEN, "courses", slug)
    sc = jload(os.path.join(raw, "scorecard.json"), {}) or {}
    urls = [c.get("url") for c in sc.get("cards", []) if c.get("source") == "opengolfapi" and c.get("url")]
    if not urls:
        return dict(status="no opengolfapi url in scorecard.json")
    time.sleep(1.2)
    try:
        r = P.s.get(urls[0], timeout=30, headers={"Accept": "application/json"})
    except Exception as e:  # noqa: BLE001
        return dict(url=urls[0], status=f"error {e!r}"[:200])
    if r.status_code != 200:
        return dict(url=urls[0], status=r.status_code)
    d = r.json()
    hd = d.get("holes_data") or d.get("holes") or []
    pts = []
    sample = None
    if isinstance(hd, list):
        geo_f = ("tee_coords", "green", "green_polygon", "fairway_polygon", "landing_zone")
        sample = [{k: h.get(k) for k in geo_f + ("number",)} for h in hd[:2] if isinstance(h, dict)]
        for h in hd:
            if not isinstance(h, dict):
                continue
            n = h.get("number")
            tc = h.get("tee_coords")
            gr = h.get("green")
            for role, v in (("tee", tc), ("green", gr)):
                ll = _ll(v)
                if n and ll:
                    pts.append(dict(hole=int(n), role=role, point=ll))
    return dict(url=urls[0], status=200, website=d.get("website"), hole_points=pts, holes_sample=sample,
                n_holes_with_geo=len({p["hole"] for p in pts}),
                geo_keys=scan_geo_keys(d), top_keys=sorted(d.keys())[:60],
                hole_fields=sorted(hd[0].keys()) if isinstance(hd, list) and hd and isinstance(hd[0], dict) else None)


# ----------------------------------------------------------------------------- NAIP + registration
def naip_for(slug, work):
    sys.path.insert(0, os.path.join(ROOT, "course_data", "imagery"))
    import fetch_imagery as FI
    cj = jload(os.path.join(GEN, "courses", slug, "course.json"))
    w, s, e, n = cj["bbox"]
    out = os.path.join(work, "naip")
    os.makedirs(out, exist_ok=True)
    s2, w2, n2, e2 = FI.pad_bbox((s, w, n, e), 150)
    meta = FI.fetch_naip((s2, w2, n2, e2), out, 0.6)
    import cv2
    img = cv2.imread(os.path.join(out, meta["lo"]["files"]["rgb"]))
    return img, meta


def px_to_lonlat_fn(meta):
    from pyproj import Transformer
    a, b, c, d, e, f = meta["lo"]["transform"]
    tr = Transformer.from_crs(meta["crs"], "EPSG:4326", always_xy=True)

    def fn(x, y):
        X, Y = a * x + b * y + c, d * x + e * y + f
        return tr.transform(X, Y)
    return fn


def lonlat_to_px_fn(meta):
    from pyproj import Transformer
    a, b, c, d, e, f = meta["lo"]["transform"]
    tr = Transformer.from_crs("EPSG:4326", meta["crs"], always_xy=True)

    def fn(lon, lat):
        X, Y = tr.transform(lon, lat)
        return (X - c) / a, (Y - f) / e
    return fn


class NaipFeatures:
    """RootSIFT on the NAIP mosaic at a few scales (website images are 0.3-3 m/px)."""

    def __init__(self, img):
        import cv2
        self.cv2 = cv2
        self.sift = cv2.SIFT_create(nfeatures=40000, contrastThreshold=0.02)
        self.levels = []
        for k in (1.0, 0.5, 0.25):
            im = img if k == 1.0 else cv2.resize(img, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            g = cv2.createCLAHE(2.0, (8, 8)).apply(g)
            kp, des = self.sift.detectAndCompute(g, None)
            if des is None:
                continue
            des = rootsift(des)
            pts = np.float32([p.pt for p in kp]) / k
            self.levels.append((k, pts, des))
        self.shape = img.shape

    def match(self, im):
        cv2 = self.cv2
        h0, w0 = im.shape[:2]
        sc = min(1.0, 1600 / max(h0, w0))
        imr = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA) if sc < 1 else im
        g = cv2.createCLAHE(2.0, (8, 8)).apply(cv2.cvtColor(imr, cv2.COLOR_BGR2GRAY))
        kp, des = self.sift.detectAndCompute(g, None)
        if des is None or len(kp) < 20:
            return None
        des = rootsift(des)
        qpts = np.float32([p.pt for p in kp]) / sc
        best = None
        flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=64))
        for k, pts, ndes in self.levels:
            mm = flann.knnMatch(des, ndes, k=2)
            good = [m[0] for m in mm if len(m) == 2 and m[0].distance < 0.82 * m[1].distance]
            if len(good) < 12:
                continue
            A = qpts[[m.queryIdx for m in good]]
            B = pts[[m.trainIdx for m in good]]
            H, inl = cv2.findHomography(A, B, cv2.USAC_MAGSAC, 6.0 / k, maxIters=20000, confidence=0.999)
            if H is None:
                continue
            ni = int(inl.sum())
            if best is None or ni > best[1]:
                best = (H, ni, len(good), k)
        if best is None:
            return None
        H, ni, ng, k = best
        sane = homography_sane(H, w0, h0, self.shape)
        return dict(H=H.tolist(), inliers=ni, good=ng, level=k, **sane)


def rootsift(des):
    des = des / (np.abs(des).sum(axis=1, keepdims=True) + 1e-7)
    return np.sqrt(des).astype(np.float32)


def homography_sane(H, w, h, naip_shape):
    import cv2
    corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    pc = cv2.perspectiveTransform(corners, np.float64(H)).reshape(-1, 2)
    area = abs(cv2.contourArea(pc.astype(np.float32)))
    convex = bool(cv2.isContourConvex(pc.astype(np.float32)))
    sides = [np.linalg.norm(pc[i] - pc[(i + 1) % 4]) for i in range(4)]
    aspect_in = w / h
    aspect_out = ((sides[0] + sides[2]) / 2) / max(1e-6, (sides[1] + sides[3]) / 2)
    skew = max(aspect_in / max(aspect_out, 1e-6), aspect_out / max(aspect_in, 1e-6))
    H_, W_ = naip_shape[:2]
    cx, cy = pc.mean(axis=0)
    inside = 0 <= cx <= W_ and 0 <= cy <= H_
    ok = convex and skew < 2.0 and inside and area > 400 and area < 4 * W_ * H_
    return dict(footprint_px=pc.tolist(), area_px=float(area), convex=convex, skew=float(skew), sane=bool(ok))


def ocr_numbers(im):
    """tesseract word boxes that read as 1..18 -> [(n, x, y, conf)] in image px."""
    import cv2
    out = []
    h, w = im.shape[:2]
    sc = 2.0 if max(h, w) < 1500 else 1.0
    big = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC) if sc != 1 else im
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        cv2.imwrite(tf.name, big)
        path = tf.name
    try:
        for psm in ("11", "12"):
            r = subprocess.run(["tesseract", path, "stdout", "--psm", psm, "-c",
                                "tessedit_char_whitelist=0123456789", "tsv"], capture_output=True, text=True,
                               timeout=120)
            for line in r.stdout.splitlines()[1:]:
                f = line.split("\t")
                if len(f) < 12 or not f[11].strip().isdigit():
                    continue
                n = int(f[11])
                conf = float(f[10])
                if 1 <= n <= 18 and conf >= 40:
                    x = (int(f[6]) + int(f[8]) / 2) / sc
                    y = (int(f[7]) + int(f[9]) / 2) / sc
                    out.append((n, x, y, conf))
    finally:
        os.remove(path)
    # dedupe (same number within 15 px)
    ded = []
    for o in sorted(out, key=lambda t: -t[3]):
        if not any(o[0] == d[0] and math.hypot(o[1] - d[1], o[2] - d[2]) < 15 for d in ded):
            ded.append(o)
    return ded


def decode_image(content):
    import cv2
    arr = np.frombuffer(content, np.uint8)
    im = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if im is None:
        try:
            from PIL import Image
            pil = Image.open(io.BytesIO(content)).convert("RGB")
            im = cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)
        except Exception:  # noqa: BLE001
            return None
    return im


def pdf_pages(content, work):
    """Render a PDF's pages (<= 3) to images at 150 dpi; also report embedded image count."""
    p = os.path.join(work, hashlib.sha1(content).hexdigest()[:10] + ".pdf")
    with open(p, "wb") as fh:
        fh.write(content)
    n_img = None
    try:
        r = subprocess.run(["pdfimages", "-list", p], capture_output=True, text=True, timeout=60)
        n_img = max(0, len(r.stdout.splitlines()) - 2)
    except Exception:  # noqa: BLE001
        pass
    ims = []
    try:
        subprocess.run(["pdftoppm", "-r", "150", "-l", "3", "-png", p, p[:-4]], check=True, timeout=120)
        import cv2
        for f in sorted(os.listdir(work)):
            if f.startswith(os.path.basename(p)[:-4]) and f.endswith(".png"):
                ims.append(cv2.imread(os.path.join(work, f)))
                os.remove(os.path.join(work, f))
    except Exception:  # noqa: BLE001
        pass
    os.remove(p)
    return n_img, ims


# ----------------------------------------------------------------------------- per course
def probe_course(slug, out_dir, do_register=True):
    P = Polite()
    cj = jload(os.path.join(GEN, "courses", slug, "course.json"), {}) or {}
    rec = dict(slug=slug, name=cj.get("name"), state=cj.get("state"), town=cj.get("town"),
               website=cj.get("website"))
    t0 = time.time()
    try:
        rec["golfify"] = golfify_probe(P, slug)
    except Exception as e:  # noqa: BLE001
        rec["golfify"] = dict(status=f"error {e!r}"[:300])
    try:
        rec["opengolfapi"] = opengolfapi_probe(P, slug)
    except Exception as e:  # noqa: BLE001
        rec["opengolfapi"] = dict(status=f"error {e!r}"[:300])
    site = None
    web = cj.get("website")
    rec["website_source"] = "osm" if web else None
    if not web:
        for key in ("opengolfapi", "golfify"):
            w = (rec.get(key) or {}).get("website")
            if w and not re.search(r"(?i)golfify|opengolfapi|facebook|golfnow|teeitup", w):
                web, rec["website_source"] = w, key
                break
    rec["website"] = web
    if web:
        try:
            site = crawl_site(P, web)
        except Exception as e:  # noqa: BLE001
            site = dict(error=traceback.format_exc()[-800:])
    rec["site"] = {k: v for k, v in (site or {}).items() if k != "pdfs"}
    if site:
        rec["site"]["pdfs"] = [{k: v for k, v in p.items() if k != "_content"} for p in site.get("pdfs", [])]
    rec["site_summary"] = summarize_site(site)

    # ---- download + register candidate images
    regs = []
    if do_register and site and site.get("reachable"):
        work = tempfile.mkdtemp(prefix=f"ev_{slug}_")
        cands = [im for im in site["images"] if im["kind"] in ("hole", "layout", "scorecard")]
        others = [im for im in site["images"] if im["kind"] == "other"
                  and re.search(r"(?i)course|tour|hole|aerial|drone|map", im["page"] + im["url"])]
        cands = (cands + others)[:MAX_IMAGES]
        naip = None
        if cands or site.get("pdfs"):
            try:
                img, meta = naip_for(slug, work)
                naip = (NaipFeatures(img), meta)
            except Exception:  # noqa: BLE001
                rec["naip_error"] = traceback.format_exc()[-800:]
        if naip:
            feats, meta = naip
            todo = [(c["url"], c, None) for c in cands]
            for p in site.get("pdfs", [])[:6]:
                n_img, ims = pdf_pages(p["_content"], work)
                p_rec = next(x for x in rec["site"]["pdfs"] if x["url"] == p["url"])
                p_rec["embedded_images"] = n_img
                for i, im in enumerate(ims):
                    todo.append((f"{p['url']}#page={i + 1}", dict(kind="pdf_page", hole=p.get("hole"),
                                                                 page=p["url"], alt=p.get("label", "")), im))
            for url, c, im in todo:
                rr = dict(url=url, kind=c["kind"], hole=c.get("hole"), page=c.get("page"), alt=c.get("alt"))
                if im is None:
                    r = P.get(url, timeout=40)
                    if r is None or r.status_code != 200 or len(r.content) > IMG_MAX_BYTES:
                        rr["status"] = "download_failed" if r is None else r.status_code
                        regs.append(rr)
                        continue
                    im = decode_image(r.content)
                if im is None or min(im.shape[:2]) < 200:
                    rr["status"] = "too_small_or_undecodable"
                    regs.append(rr)
                    continue
                rr["wh"] = [int(im.shape[1]), int(im.shape[0])]
                try:
                    m = feats.match(im)
                except Exception as e:  # noqa: BLE001
                    m = None
                    rr["match_error"] = repr(e)[:200]
                rr["status"] = "matched" if m else "no_match"
                if m:
                    rr["match"] = m
                    if m["sane"] and m["inliers"] >= 12:
                        rr["ocr"] = ocr_numbers(im) if c["kind"] in ("layout", "pdf_page", "scorecard", "other") \
                            else []
                regs.append(rr)
            rec["naip"] = dict(year=meta.get("year"), crs=meta["crs"], lo=meta["lo"])
    rec["registrations"] = regs
    rec["seconds"] = round(time.time() - t0, 1)
    rec["http_log_n"] = len(P.log)
    rec["robots_disallowed"] = sum(1 for x in P.log if x["status"] == "robots_disallow")
    with open(os.path.join(out_dir, f"{slug}.json"), "w") as fh:
        json.dump(rec, fh, indent=1, default=str)
    return rec


def summarize_site(site):
    if not site:
        return dict(has_website=False)
    ims = site.get("images", [])
    return dict(has_website=True, reachable=site.get("reachable", False), robots_ok=site.get("robots_ok"),
                pages=len(site.get("pages", [])), hole_pages=len(site.get("hole_pages", {})),
                hole_images=len({im["hole"] for im in ims if im.get("kind") == "hole" and im.get("hole")}),
                layout_images=sum(1 for im in ims if im.get("kind") == "layout"),
                scorecard_images=sum(1 for im in ims if im.get("kind") == "scorecard"),
                pdfs=len(site.get("pdfs", [])), videos=len(site.get("videos", [])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slugs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-register", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for slug in [s for s in a.slugs.split(",") if s]:
        log("=====", slug)
        try:
            r = probe_course(slug, a.out, not a.no_register)
            log(json.dumps(r.get("site_summary")), "regs", len(r.get("registrations", [])), r.get("seconds"))
        except Exception:  # noqa: BLE001
            log(traceback.format_exc())
            with open(os.path.join(a.out, f"{slug}.json"), "w") as fh:
                json.dump(dict(slug=slug, error=traceback.format_exc()[-1500:]), fh, indent=1)


if __name__ == "__main__":
    main()
