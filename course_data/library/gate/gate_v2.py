"""Gate v2: can an auto-built course page be trusted without a human tap?  Reads only a page's qa.json (the output of
course_data/library/picture_checks.py, one block per solved tee set) and decides, per hole x tee set and per course,
AUTO (trust it) or CONFIRM (golfer / reviewer taps first). Interpretable rules; the numbers behind them are in
GATE_V2.md (gate_v2_eval.py builds them from the review.json verdicts and the hand-truth gate builds).

  python3 course_data/library/gate/gate_v2.py course_data/library/<slug>/qa.json [--json]

Course red flags (any one -> every hole CONFIRM):
  no_card        no web scorecard matched (card_holes 0, or the solved set is 'osm_back'): tees are guessed from OSM
  holes_vs_card  holes built != card holes
  par_sum        pars do not sum to the card total, after taking out holes whose own par check already fails
                 (those holes are CONFIRM on their own)
  page_errors    the page smoke test reported problems / errors
  tee_fits       more than MAX_COURSE_TEE_FITS holes (any set) where the tee had to be walked back / put on a pad
                 to fit the card, or the yardage is off the card: a sign the card is scrambled or the wrong version
Hole x set (on a course with no red flag): AUTO when the hole is PASS, or every failed check is benign:
  tee      benign when OSM maps no tee boxes on the course (PAD_MODE), the tee is on a lidar / texture pad or the tee
           axis (not a walk-back, not the bare hole-line start) AND the measured yardage is within YARD_OK of the card.
           Where OSM does map tees, a pad tee means the build disagreed with OSM: CONFIRM (15% wrong vs 5% for PASS)
  aim      benign when no fairway is mapped and the pick lands in rough, or (AIM_ROUGH_OK > 0) it lands in rough
           within AIM_ROUGH_OK yds of a mapped fairway; never water / OB / sand / recovery
  par3_box benign (no OSM green outline: the box is on the estimated green; the yardage check still applies)
  anything else (yardage off the card, par vs card, oval over the hazard limit) -> CONFIRM
A course is AUTO when it has no red flag and every hole x set is AUTO; else the CONFIRM holes are the tap list.
"""
import argparse
import json
import re
import sys

YARD_OK = 10            # |measured - card| yds for a pad tee to count as the card tee
AIM_ROUGH_OK = 0        # yds from fairway for a rough landing to be harmless
MAX_COURSE_TEE_FITS = 6  # walk-backs + yardage misses across all sets before the card itself is suspect
PAD_KINDS = ("lidar_pad", "texture_pad", "tee_axis")
PAD_MODE = "no_osm_tees"  # pad tee benign: "never" | "no_osm_tees" (only where OSM maps no tee boxes) | "always"

_NUM = r"([-+]?\d+(?:\.\d+)?)"


def hole_features(h):
    """Flatten one qa hole into the fields the rules use."""
    ck = h.get("checks") or {}
    f = dict(status=h.get("status"), par=h.get("par"), failed=sorted(k for k, c in ck.items() if not c.get("ok")))
    y = (ck.get("yardage") or {}).get("why", "")
    m = re.search(r"measured " + _NUM + r" vs card " + _NUM, y)
    f["yard_delta"] = (float(m.group(1)) - float(m.group(2))) if m else None
    f["no_card_yards"] = "no card yardage" in y
    p = (ck.get("par") or {}).get("why", "")
    f["no_card_par"] = "no card par" in p
    t = ck.get("tee") or {}
    tw = t.get("why", "")
    m = re.search(r"\(([^;]+);", tw)
    f["tee_kind"] = None if t.get("ok", True) else (m.group(1).strip() if m else "other")
    m = re.search(_NUM + r" yds from the nearest OSM tee", tw)
    f["tee_dist"] = float(m.group(1)) if m else None
    f["osm_no_tees"] = "OSM maps no tee boxes" in tw
    a = (ck.get("aim") or {}).get("why", "")
    m = re.search(r"lands(?: .*?)? in (\w+)(?: \(" + _NUM + r" yds from fairway\))?", a)
    f["aim_lie"] = m.group(1) if m else None
    f["aim_from_fw"] = float(m.group(2)) if m and m.group(2) else None
    f["no_fairway"] = "no fairway mapped" in a
    o = (ck.get("oval") or {}).get("why", "")
    m = re.search(r"pattern " + _NUM + "%", o)
    f["oval_pct"] = float(m.group(1)) if m else None
    return f


def benign(f, failed_check):
    if failed_check == "tee":
        if PAD_MODE == "never" or (PAD_MODE == "no_osm_tees" and not f["osm_no_tees"]):
            return False
        return (f["tee_kind"] in PAD_KINDS and f["yard_delta"] is not None and abs(f["yard_delta"]) <= YARD_OK)
    if failed_check == "aim":
        if f["aim_lie"] != "rough":
            return False
        return f["no_fairway"] or (f["aim_from_fw"] is not None and f["aim_from_fw"] <= AIM_ROUGH_OK)
    if failed_check == "par3_box":
        return True
    return False


def hole_decision(f):
    if f["status"] == "PASS":
        return "AUTO", []
    bad = [c for c in f["failed"] if not benign(f, c)]
    return ("AUTO" if not bad else "CONFIRM"), bad


def course_flags(qa):
    flags = []
    page = qa.get("page") or {}
    for w, blk in (qa.get("checks") or {}).items():
        c = blk.get("course") or {}
        if not c.get("card_holes") or blk.get("set") == "osm_back":
            flags.append("no_card")
        elif c.get("holes") != c.get("card_holes"):
            flags.append("holes_vs_card")
        if c.get("card_par_total") and (c.get("par_total") != c.get("card_par_total") or not c.get("pars_ok")):
            # a sum that is off only by holes whose own par check already fails is a hole problem, not a course one
            dp = 0
            for h in (blk.get("holes") or {}).values():
                m = re.search(r"par (\d+) vs card (\d+)", ((h.get("checks") or {}).get("par") or {}).get("why", ""))
                if m and not h["checks"]["par"].get("ok"):
                    dp += int(m.group(1)) - int(m.group(2))
            if (c.get("par_total") or 0) - dp != c.get("card_par_total") or c.get("holes") != c.get("card_holes"):
                flags.append("par_sum")
    for s, p in page.items():
        if (p or {}).get("rc") or (p or {}).get("problems") or (p or {}).get("errors"):
            flags.append("page_errors")
    fits = set()
    for w, blk in (qa.get("checks") or {}).items():
        for n, h in (blk.get("holes") or {}).items():
            f = hole_features(h)
            if f["tee_kind"] == "walkback" or "yardage" in f["failed"] and not f["no_card_yards"]:
                fits.add((w, n))
    if len(fits) > MAX_COURSE_TEE_FITS:
        flags.append("tee_fits")
    return sorted(set(flags))


def gate(qa):
    """-> dict(course='AUTO'|'CONFIRM', flags=[...], holes={set: {hole: (decision, [bad checks])}}, confirm=[...])"""
    flags = course_flags(qa)
    holes, confirm = {}, set()
    for w, blk in (qa.get("checks") or {}).items():
        s = blk.get("set") or w
        holes[s] = {}
        for n, h in (blk.get("holes") or {}).items():
            d, bad = hole_decision(hole_features(h))
            if flags:
                d = "CONFIRM"
            holes[s][n] = (d, bad)
            if d != "AUTO":
                confirm.add(n)
    key = lambda x: (int(x) if str(x).isdigit() else 999, str(x))
    return dict(course="CONFIRM" if flags or confirm else "AUTO", flags=flags, holes=holes,
                confirm=sorted(confirm, key=key))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qa")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    g = gate(json.load(open(a.qa)))
    if a.json:
        json.dump(g, sys.stdout, indent=1)
        return
    print("course:", g["course"], ("flags: " + ", ".join(g["flags"])) if g["flags"] else "")
    for s, hs in g["holes"].items():
        bad = {n: b for n, (d, b) in hs.items() if d != "AUTO"}
        print(f"  {s}: {len(hs) - len(bad)}/{len(hs)} holes AUTO" +
              ("; confirm " + ", ".join(f"{n}({'/'.join(b) or 'course'})" for n, b in bad.items()) if bad else ""))


if __name__ == "__main__":
    main()
