# Sequence v3 on D's benchmark: card geometry inside the route DP

Actions run 40950962886 (`.github/workflows/zero_tap_seqv3.yml`, request `course_data/requests/zt_seqv3_v3.json`).
Method `sequence_v3` (`course_data/zero_tap/results/sequence_v3/<tier>/`). Rows: `zrows.json.gz` (chosen),
`zrows_c0.json.gz` (card term off = v2's card prior, same run). Variant choice in `pick_card.json`, gate in
`gate_params.json`, board in `bench_d_table.md`. **The card parameters, the variant and the gate were fitted on dev only
(dev uses out-of-fold A pairs from run 39054373440). Test was scored once.**

## What changed (`sequence/cardgeo.py`, `joint.py`)

Per (green, tee hypothesis, card number), using every tee set on the card at once:

- **back:** the back box vs a set's yardage, with dog-leg slack.
- **nest:** each shorter distinct yardage needs a box on the same line of play at the spacing the card's differences
  predict.
- **par / handicap:** par-by-length per set, plus a weak handicap-order term.

The term enters the route DP inside each position's tee sum (per-position transition matrices), so the card chooses
the tee as well as the hole number. v2 marginalised the longest set's yardage over the tees, so its card never chose
between two tees of one green.

Courses without A's pairs (benchmark v1's new states) fall back to the structure hypotheses.

The physical parameters were fitted on dev with oracle numbering (`fit_cardgeo.py`). Card-only top-1 among a green's
candidate tees went from 91.3 % (v2 term) to 93.2 % (92.7 % without nesting).

## Variant choice (dev card-tier courses, fully right of 198)

| c0 (v2 prior) | c0.5 | c1 | c1 without nesting | c2 |
|---|---|---|---|---|
| 46 | 46 | 50 | 50 | **51 (chosen)** |

## Before / after on test (fully right = every number and par right; D's per-course scorer)

| tier | courses | c0: fully right / holes numbered right | v3 (c2): fully right / holes numbered right |
|---|---|---|---|
| osm_card, all v1 | 153 | 17.0 % / 63.9 % | **22.2 %** / 66.3 % |
| osm_card, v0 subset | 84 | 16.7 % / 72.2 % (published v2: 14.3 % / 71.8 %) | **23.8 %** / 75.1 % |
| unmapped_card | 17 | 17.6 % / 73.9 % | **23.5 %** / 77.1 % |

No-card tiers are unchanged: they come from c0.

On test, the gate certifies 3 osm_card courses, all right (dev: 2 + 1, all right). The ≥ 99 % coverage is still small:
2.6 % osm_card, 11.8 % unmapped_card.

Pairing is still the main failure: formed holes on test v0 went only from 82.3 % to 83.6 %. The card mostly fixes the
1-2 wrong holes on otherwise-right courses; it cannot add a tee that the candidates lack.
