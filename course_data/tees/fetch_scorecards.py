"""Fetch public scorecard pages for a course (run in GitHub Actions: the dev sandbox has no web).

Saves each page's raw bytes and a tag-stripped text version under course_data/tees/raw/,
plus index.json (url -> status, file). Follows links that look like scorecards / PDFs on the
club's own site one level deep. PDFs are converted with `pdftotext -layout` when available.
"""
import hashlib
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests

OUT = Path(__file__).resolve().parent / "raw"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")

URLS = [
    # club
    "https://www.spirithollowgolfcourse.com/",
    "https://www.spirithollowgolfcourse.com/golf/hole-by-hole",
    # aggregators
    "https://www.golflink.com/golf-courses/ia/burlington/spirit-hollow-golf-course",
    "https://offcourse.co/courses/scorecard/spirit-hollow-golf-course/",
    "https://www.mscorecard.com/mscorecard/showcourse.php?cid=141520763138614737",
    "https://course.bluegolf.com/bluegolf/course/course/spirithollowgc/detailedscorecard.htm",
    "https://course.bluegolf.com/bluegolf/course/course/spirithollowgc/",
    "https://www.birdierally.com/courses/spirit-hollow-golf-course-burlington-ia",
    "https://www.golfify.io/courses/spirit-hollow-golf-course",
    "https://courses.opengolfapi.org/courses/IA/spirit-hollow-golf-course",
    "https://stymie.golf/golf-courses/iowa/des-moines-county/burlington/spirit-hollow-golf-course-burlington",
    "https://www.golfpass.com/travel-advisor/courses/29590-spirit-hollow-golf-course/scorecard-and-layout",
    "https://www.golfpass.com/travel-advisor/courses/29590-spirit-hollow-golf-course",
    "https://www.golfnow.com/courses/1505820-spirit-hollow-golf-course-details",
    "https://foretee.com/courses/iowa/burlington/usa/spirit-hollow-golf-course/5581/",
    "https://1golf.eu/en/club/spirit-hollow-golf-course",
    "https://freegolftracker.com/courses/Spirit-Hollow_6093.htm",
    "https://www.top100golfcourses.com/golf-course/spirit-hollow",
    "https://pluggedingolf.com/spirit-hollow-golf-course-review/",
    "https://golfcoursegurus.com/reviews/spirit-hollow-golf-course/",
    "https://www.golfn.com/courses/united-states-of-america/iowa/spirit-hollow-golf-course",
    "https://courses.swingbyswing.com/courses/United-States-of-America/Iowa/Burlington/Spirit-Hollow-Golf-Course/27711",
    "https://www.allsquaregolf.com/golf-courses/iowa/spirit-hollow-golf-course",
    "https://www.golfsmash.com/golf-course/spirit-hollow-golf-course/courses/573bf8877d813199.html",
    "https://golftraxx.com/scorecard?course_name=Spirit+Hollow+Golf+Course&static=true&zipcode=52601",
    "https://www.golfadvisor.com/courses/29590-spirit-hollow-golf-course",
    "https://www.18birdies.com/golf-courses/club/spirit-hollow-golf-course-burlington-ia",
    "https://www.golflogix.com/golf-course-gps/us/ia/burlington/spirit-hollow-golf-course",
    # USGA NCRDB search (state + name)
    "https://ncrdb.usga.org/courseTeeInfo?CourseName=Spirit%20Hollow&State=US-IA",
    "https://ncrdb.usga.org/NCRDB/rest/v1/courses/search?name=Spirit%20Hollow&state=US-IA",
]


def text_of(body: str) -> str:
    body = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", body)
    body = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d|table)>", "\n", body)
    body = re.sub(r"(?i)</t[dh]>", "\t", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body)
    body = re.sub(r"[ \t\r\f\v]+", " ", body)
    return re.sub(r"\n\s*\n+", "\n", body).strip()


def save(url, r, idx):
    key = hashlib.sha1(url.encode()).hexdigest()[:10]
    ctype = r.headers.get("content-type", "")
    ext = ".pdf" if "pdf" in ctype or url.lower().endswith(".pdf") else ".html"
    raw = OUT / f"{key}{ext}"
    if ext == ".pdf":
        raw.write_bytes(r.content)
    txt = OUT / f"{key}.txt"
    if ext == ".pdf":
        try:
            subprocess.run(["pdftotext", "-layout", str(raw), str(txt)], check=True)
        except Exception as e:  # noqa: BLE001
            txt.write_text(f"pdftotext failed: {e}")
    else:
        txt.write_text(f"URL: {url}\n\n" + text_of(r.text))
        # JSON embedded in the page (Next.js / nuxt / ld+json) often carries the per-hole card
        blobs = re.findall(r'(?is)<script[^>]*(?:__NEXT_DATA__|application/(?:ld\+)?json)[^>]*>(.*?)</script>', r.text)
        if blobs:
            (OUT / f"{key}.json.txt").write_text("\n\n".join(b[:400000] for b in blobs))
    idx[url] = dict(status=r.status_code, final=r.url, ctype=ctype, file=raw.name, bytes=len(r.content))
    return r.text if ext == ".html" else ""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    idx, extra = {}, []
    for url in URLS + sys.argv[1:]:
        try:
            r = s.get(url, timeout=30)
            body = save(url, r, idx)
            print(r.status_code, len(r.content), url)
            if "spirithollow" in url and body:
                for href in re.findall(r'href="([^"]+)"', body):
                    if re.search(r"(?i)score|card|\.pdf|hole|tee|yard", href) and not re.search(
                            r"(?i)instagram|facebook|twitter|foreup|\.css|\.js", href):
                        extra.append(urljoin(r.url, html.unescape(href)))
        except Exception as e:  # noqa: BLE001
            idx[url] = dict(error=str(e))
            print("ERR", url, e)
        time.sleep(1)
    for url in sorted(set(extra) - set(idx))[:40]:
        try:
            r = s.get(url, timeout=30)
            save(url, r, idx)
            print(r.status_code, len(r.content), url)
        except Exception as e:  # noqa: BLE001
            idx[url] = dict(error=str(e))
        time.sleep(1)
    (OUT / "index.json").write_text(json.dumps(idx, indent=1))


if __name__ == "__main__":
    main()
