"""What-if checks on top of tee_strategy.py (run: python3 mozingo/scenarios.py)."""
import copy
import tee_strategy as t

BASE_CLUBS = dict(t.CLUBS)
BASE_HOLES = copy.deepcopy(t.HOLES)


def compare(hole_no, label):
    r = {c: t.best_aim(hole_no, c) for c in t.CLUBS}
    best = min(r, key=lambda c: r[c]["ev"])
    cells = ", ".join(f"{c} {r[c]['ev'] - r[best]['ev']:+.3f} (aim {r[c]['aim']:+.1f})" for c in r)
    print(f"  {label:<38} best={best:<7} | {cells}")


print("1) Wider-than-app dispersion (all clubs x1.3)")
t.CLUBS = {k: (c, tot, w * 1.3, d) for k, (c, tot, w, d) in BASE_CLUBS.items()}
for h in t.HOLES:
    compare(h, f"hole {h}")
t.CLUBS = dict(BASE_CLUBS)

print("\n2) Hole 2: how much does the driver's carry matter?")
for carry in (265, 275, 290, 305):
    t.CLUBS = dict(BASE_CLUBS, Driver=(carry, carry + 25, 65, 28))
    compare(2, f"driver carry {carry} / total {carry + 25}")
t.CLUBS = dict(BASE_CLUBS)

print("\n3) Hole 4: move the left prairie toward the line until 2-wood wins")
# traced edge sits ~40 yds left of the app line at 300 yds; push its right edge in.
ppy = t.hole_frame(t.HOLES[4])[3]
for yds_in in (0, 10, 15, 20, 25, 30):
    t.HOLES = copy.deepcopy(BASE_HOLES)
    zones = t.HOLES[4]["zones"]
    i = next(i for i, z in enumerate(zones) if z[0] == "native")
    dx = yds_in * ppy
    zones[i] = ("native", [(200, 550), (370 + dx, 550), (365 + dx, 900), (200, 900)])
    compare(4, f"prairie edge {40 - yds_in} yds left of line")
t.HOLES = copy.deepcopy(BASE_HOLES)

print("\n4) Hole 1: 4-wood shorter & tighter (240 carry / 260 total, 45 wide)")
t.CLUBS = dict(BASE_CLUBS, **{"4-wood": (240, 260, 45, 22)})
compare(1, "4-wood 240/260")
t.CLUBS = dict(BASE_CLUBS)
