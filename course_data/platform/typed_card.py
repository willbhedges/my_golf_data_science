"""A golfer-typed scorecard: 9 / 18 yardages (one tee set) and optionally the pars, strictly validated.

    from typed_card import parse_typed_card
    card, issues = parse_typed_card("391 175 520 402 ... ", pars="4 3 5 4 ...", tee="White")
    # card: scorecard/1 (scorecard.py's normalised shape) or None; issues: [{level, code, msg, hole?}]

Used when no card is online (routing then has no yardage sequence and hole numbers are a guess: REPORT.md).
Accepted input (yards and pars alike):
  * numbers separated by spaces, commas, semicolons, slashes, tabs or new lines ("391, 175 / 520 ...")
  * "hole: value" pairs in any order ("1: 391  2: 175 ..." or "1-391, 2-175"): every hole exactly once
  * the card's subtotal columns: 9 + OUT (+ 9 + IN (+ TOT)) - recognised only when the subtotal equals the sum
    of the 9 before it, then removed
  * metres with unit="m" (converted to yards)
Strict validation - an `error` returns card None (the app re-asks, pointing at the hole):
  count       9 or 18 values (after subtotals); 27 / 36 -> pick the nine / eighteen played (error)
  number      digits only per value; a value > 999 is two values typed together (error: "hole 4: 3912")
  range       yards 50..720 per hole; pars 3..6
  pars        same count as the yards; total 27..38 (9) / 54..76 (18)
  totals      a stated total (total=...) must equal the sum
Warnings (accepted, shown to the golfer for a second look):
  par fit     par 3 > 270 yds, par 4 < 230 or > 520, par 5 < 400 yds (typo or a mis-ordered list)
  repeats     the same 9 values twice on an 18 (a 9-hole course played twice: fine, routing handles it)
  front/back  OUT / IN subtotals stated but they disagree (a typo somewhere in that nine)
"""
from __future__ import annotations

import re

YARD_MIN, YARD_MAX = 50, 720
PAR_FIT = {3: (0, 270), 4: (230, 520), 5: (400, 720), 6: (520, 900)}
SEP = re.compile(r"[\s,;/|\t]+")
PAIR = re.compile(r"(?:hole\s*)?#?(\d{1,2})\s*[:=\-)]\s*(\d+)", re.I)


def _issue(level, code, msg, hole=None):
    d = dict(level=level, code=code, msg=msg)
    if hole is not None:
        d["hole"] = hole
    return d


def tokens(text):
    """Text -> ([int values in hole order], issues). Handles hole:value pairs and plain lists."""
    if isinstance(text, (list, tuple)):
        text = " ".join(str(x) for x in text)
    text = str(text or "").strip()
    issues = []
    if not text:
        return [], [_issue("error", "empty", "nothing typed")]
    pairs = PAIR.findall(text)
    rest = PAIR.sub(" ", text).strip(" ,;/|\t\n")
    if pairs and not re.search(r"\d", rest):
        by = {}
        for h, v in pairs:
            h = int(h)
            if h in by:
                issues.append(_issue("error", "duplicate_hole", f"hole {h} typed twice", h))
            by[h] = int(v)
        n = max(by)
        missing = [h for h in range(1, n + 1) if h not in by]
        if missing:
            issues.append(_issue("error", "missing_hole", f"no value for hole(s) {', '.join(map(str, missing))}",
                                 missing[0]))
        return [by.get(h) for h in range(1, n + 1)], issues
    vals = []
    for i, tok in enumerate(t for t in SEP.split(text) if t):
        tok = tok.strip(".")
        if re.fullmatch(r"\d+", tok):
            vals.append(int(tok))
        elif re.fullmatch(r"(out|in|tot|total|front|back)", tok, re.I):
            continue                                # a subtotal label typed along with the numbers
        else:
            issues.append(_issue("error", "not_a_number", f"'{tok}' is not a number (value {len(vals) + 1})",
                                 len(vals) + 1))
    return vals, issues


def strip_subtotals(vals):
    """Remove OUT / IN / TOT columns when they equal the sums they stand for. -> (holes, subtotals dict)."""
    v = list(vals)
    sub = {}
    if len(v) in (10, 11) and v[9] == sum(v[:9]):
        sub["out"] = v[9]
        v = v[:9] + v[10:]
        if len(v) == 10 and v[9] == sub["out"]:
            v = v[:9]
    elif len(v) in (20, 21) and v[9] == sum(v[:9]) and v[19] == sum(v[10:19]):
        sub["out"], sub["in"] = v[9], v[19]
        tot = v[20] if len(v) == 21 else None
        v = v[:9] + v[10:19]
        if tot is not None:
            sub["total"] = tot
    elif len(v) == 19 and v[18] == sum(v[:18]):
        sub["total"] = v[18]
        v = v[:18]
    return v, sub


def _check_count(vals, what):
    n = len(vals)
    if n in (9, 18):
        return []
    if n in (27, 36):
        return [_issue("error", "too_many_holes", f"{n} {what} - a {n}-hole facility: type the "
                       f"{'nine' if n == 27 else 'eighteen'}s you are playing (18 values)")]
    near = 9 if abs(n - 9) < abs(n - 18) else 18
    return [_issue("error", "count", f"{n} {what} typed, expected 9 or 18 ({'one missing' if n == near - 1 else ('one extra' if n == near + 1 else f'{abs(n - near)} off')})")]


def parse_typed_card(yards, pars=None, tee="Typed", unit="yd", total=None, out_total=None, in_total=None,
                     source="typed by golfer"):
    """-> (scorecard/1 card or None, issues). `yards` / `pars`: text or a list."""
    issues = []
    yv, iss = tokens(yards)
    issues += iss
    yv, sub = strip_subtotals([y for y in yv if y is not None]) if not any(i["level"] == "error" for i in iss) else (yv, {})
    out_total = out_total or sub.get("out")
    in_total = in_total or sub.get("in")
    total = total or sub.get("total")
    issues += _check_count(yv, "yardages")
    if unit == "m":
        yv = [int(round(y / 0.9144)) if y is not None else None for y in yv]
    for i, y in enumerate(yv):
        if y is None:
            continue
        if y > 999:
            issues.append(_issue("error", "joined", f"hole {i + 1}: {y} looks like two values typed together", i + 1))
        elif not YARD_MIN <= y <= YARD_MAX:
            issues.append(_issue("error", "range", f"hole {i + 1}: {y} yds is outside {YARD_MIN}-{YARD_MAX}", i + 1))
    pv = None
    if pars is not None and str(pars).strip() not in ("", "[]"):
        pv, iss = tokens(pars)
        issues += [dict(i, msg="pars: " + i["msg"]) for i in iss]
        if not any(i["level"] == "error" for i in iss):
            pv, psub = strip_subtotals(pv)
        # a run of single digits typed without separators ("443545344")
        if pv and len(pv) == 1 and len(str(pv[0])) in (9, 18):
            pv = [int(ch) for ch in str(pv[0])]
        if len(pv) != len(yv):
            issues.append(_issue("error", "par_count", f"{len(pv)} pars for {len(yv)} yardages"))
        for i, p in enumerate(pv):
            if p is not None and not 3 <= p <= 6:
                issues.append(_issue("error", "par_range", f"hole {i + 1}: par {p}", i + 1))
        tp = sum(p for p in pv if p)
        lo, hi = (27, 38) if len(pv) == 9 else (54, 76)
        if len(pv) in (9, 18) and not lo <= tp <= hi:
            issues.append(_issue("error", "par_total", f"pars add up to {tp}, expected {lo}-{hi}"))
    if any(i["level"] == "error" for i in issues):
        return None, issues
    n = len(yv)
    if total is not None and sum(yv) != int(total):
        issues.append(_issue("error", "total", f"yardages add up to {sum(yv)}, the card says {total}"))
    if out_total is not None and n == 18 and sum(yv[:9]) != int(out_total):
        issues.append(_issue("warning", "out_total", f"front nine adds up to {sum(yv[:9])}, OUT says {out_total}"))
    if in_total is not None and n == 18 and sum(yv[9:]) != int(in_total):
        issues.append(_issue("warning", "in_total", f"back nine adds up to {sum(yv[9:])}, IN says {in_total}"))
    if any(i["level"] == "error" for i in issues):
        return None, issues
    if pv:
        for i, (y, p) in enumerate(zip(yv, pv)):
            lo, hi = PAR_FIT.get(p, (0, 999))
            if not lo <= y <= hi:
                issues.append(_issue("warning", "par_fit", f"hole {i + 1}: {y} yds for a par {p} - check this hole",
                                     i + 1))
    if n == 18 and yv[:9] == yv[9:]:
        issues.append(_issue("warning", "repeat_nine", "the same nine twice (a 9-hole course played twice?)"))
    card = dict(schema="scorecard/1", source=source, par=list(pv) if pv else None, handicap=None,
                tee_sets={tee: dict(colour=tee.lower(), aliases=[tee.lower()], yards=list(yv), total=sum(yv),
                                    source=source)},
                typed=dict(unit=unit, subtotals=sub or None))
    return card, issues
