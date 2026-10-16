"""What the DECADE 65-70 yd 'dead-zone corridor' rule implies in this model's terms.

Stylised: dead zones on both sides, gap C yds, aim at the centre, lateral N(0, (W/4)^2).
Driver width W, 4-wood width W*50/65 (decision.py's fixed ratio), driver 30 yds longer.
Cost of a dead ball K strokes vs in play; value of the extra 30 yds G strokes.
Break-even corridor C*: K * [P_dead(driver) - P_dead(4w)] = G.
Also: P(dead) for driver at C = 70 for several W.
"""
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm


def p_dead(C, W):
    return 2 * norm.cdf(-C / 2 / (W / 4))


def c_star(W, ratio, K, G):
    """Widest corridor at which the shorter club still wins (driver wins for any C above it);
    nan = driver wins at every corridor width (the dispersion saving never pays for 30 yds)."""
    f = lambda C: K * (p_dead(C, W) - p_dead(C, W * ratio)) - G
    Cs = np.linspace(5, 300, 2951)
    v = f(Cs)
    if v.max() <= 0:
        return float("nan")
    i = int(np.flatnonzero(v > 0).max())
    return brentq(f, Cs[i], Cs[i + 1])


if __name__ == "__main__":
    print("P(dead) driver, centred, C=70:", {W: round(p_dead(70, W), 3) for W in (65, 70, 80, 84)})
    print("P(dead) driver, centred, C=84:", {W: round(p_dead(84, W), 3) for W in (65, 70, 80, 84)})
    for ratio in (50 / 65, 60 / 65, 0.9):
        for K in (0.8, 1.0, 1.3):
            for G in (0.08, 0.12):
                row = {W: round(c_star(W, ratio, K, G), 1) for W in (65, 70, 84)}
                print(f"ratio {ratio:.2f} K {K} G {G}: C* by driver width {row}")
