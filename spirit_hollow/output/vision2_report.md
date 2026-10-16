# Spirit Hollow — hazard classifier v2 (leave-one-hole-out)

Every number is out-of-sample: each hole is scored with a model trained only on the other 15 holes. Calibration maps (when run, `--calib`) are fitted on inner 2-group-fold predictions over those 15 training holes, so the held-out hole contributes nothing to training, feature scaling, calibration or ensemble weights (the ensemble is a fixed 50/50 average). Pixel methods are 7x7-smoothed before scoring, as in vision.py. Regions for (d)/pooling: **SAM** (SAM masks for all photos; gaps filled with SLIC cells).

Penal = trees/native/water/sand, playable = fairway/rough. 'bal' = mean per-class recall. Landing zones = 220-340 yds, +/-45 yds of the line.

| Method | LZ 6-class | LZ bal | LZ penal-vs-playable | LZ penal recall | LZ penal precision | Hole 6-class | Hole penal-vs-playable | Hole penal recall | Hole penal precision | NLL | ECE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vision.py baseline (as reported) | 59.4% | | 79.2% | 69% | 55% | 52.4% | 72.5% | 72% | 75% | | |
| Handcrafted + HGB (baseline features, this script's sampler) | 62.2% | 57.9% | 82.3% | 72% | 70% | 54.4% | 75.2% | 75% | 80% | 1.27 | 0.109 |
| (a) DINOv2 linear probe (std. multinomial logreg) | 63.3% | 59.6% | 79.6% | 76% | 63% | 56.3% | 77.4% | 81% | 79% | 1.16 | 0.035 |
| (b) DINOv2 + handcrafted, HGB | 67.9% | 57.2% | 83.2% | 70% | 73% | 58.8% | 78.8% | 79% | 83% | 1.14 | 0.117 |
| (c) handcrafted + photo-relative DINOv2 (fairway-corridor median subtracted), HGB | 69.3% | 59.2% | 84.1% | 69% | 75% | 58.2% | 78.0% | 77% | 83% | 1.18 | 0.125 |
| (d) region classifier on SAM regions (mean/std per region, HGB) | 51.1% | 50.8% | 76.5% | 52% | 63% | 48.4% | 68.2% | 61% | 77% | 1.30 | 0.154 |
| (d') region classifier on SLIC superpixels (mean/std per region, HGB) | 67.3% | 56.5% | 82.9% | 66% | 74% | 56.9% | 76.9% | 76% | 82% | 1.17 | 0.132 |
| (c) probabilities mean-pooled per SAM region | 59.4% | 48.8% | 77.4% | 56% | 64% | 49.3% | 70.6% | 65% | 79% | 1.19 | 0.121 |
| (c) probabilities mean-pooled per SLIC superpixel | 70.0% | 59.8% | 84.0% | 70% | 75% | 58.7% | 78.2% | 78% | 83% | 1.14 | 0.106 |
| **(e) ensemble 50/50 of c + b, uncalibrated** | 69.7% | 59.7% | 84.2% | 70% | 75% | 59.2% | 78.8% | 78% | 83% | 1.12 | 0.101 |

Best (by landing-zone penal-vs-playable accuracy, then 6-class): **(e) ensemble 50/50 of c + b, uncalibrated**.

Reliability of confident pixels (p>=0.85, whole hole, labelled pixels):

| Method | share of pixels with p>=0.85 | accuracy of those |
|---|---|---|
| Handcrafted + HGB (baseline features, this script's sampler) | 23.4% | 79.4% |
| (a) DINOv2 linear probe (std. multinomial logreg) | 13.0% | 83.9% |
| (b) DINOv2 + handcrafted, HGB | 34.1% | 82.9% |
| (c) handcrafted + photo-relative DINOv2 (fairway-corridor median subtracted), HGB | 34.3% | 80.9% |
| (d) region classifier on SAM regions (mean/std per region, HGB) | 26.0% | 78.3% |
| (d') region classifier on SLIC superpixels (mean/std per region, HGB) | 31.4% | 81.0% |
| (c) probabilities mean-pooled per SAM region | 24.0% | 83.6% |
| (c) probabilities mean-pooled per SLIC superpixel | 31.4% | 82.3% |
| (e) ensemble 50/50 of c + b, uncalibrated | 32.2% | 83.7% |

Per-hole landing-zone accuracy of the best method (6-class / penal-vs-playable):

| Hole | 1 | 2B | 2F | 4 | 5 | 6 | 8 | 9B | 9F | 10 | 11 | 13 | 14 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6-class | 70% | 62% | 75% | 69% | 66% | 65% | 74% | 70% | 59% | 79% | 69% | 85% | 79% | 75% | 75% | 55% |
| penal | 84% | 81% | 86% | 70% | 90% | 81% | 83% | 87% | 76% | 87% | 84% | 92% | 92% | 86% | 92% | 79% |

## Confusion matrices — best method (LOHO)

#### Whole visible hole

| traced \ seen | fairway | rough | trees | native | water | sand | recall |
|---|---|---|---|---|---|---|---|
| **fairway** | 71% | 15% | 6% | 7% | 1% | 0% | 71% |
| **rough** | 35% | 31% | 17% | 15% | 1% | 1% | 31% |
| **trees** | 7% | 9% | 73% | 10% | 2% | 0% | 73% |
| **native** | 13% | 22% | 23% | 40% | 2% | 0% | 40% |
| **water** | 3% | 4% | 28% | 4% | 60% | 1% | 60% |
| **sand** | 6% | 21% | 2% | 21% | 1% | 49% | 49% |
| precision | 67% | 28% | 72% | 48% | 62% | 60% | |

#### Landing zones

| traced \ seen | fairway | rough | trees | native | water | sand | recall |
|---|---|---|---|---|---|---|---|
| **fairway** | 84% | 10% | 3% | 3% | 0% | 0% | 84% |
| **rough** | 41% | 30% | 18% | 11% | 0% | 0% | 30% |
| **trees** | 12% | 13% | 63% | 11% | 1% | 0% | 63% |
| **native** | 19% | 19% | 15% | 45% | 3% | 0% | 45% |
| **water** | 5% | 7% | 10% | 3% | 75% | 0% | 75% |
| **sand** | 6% | 18% | 2% | 10% | 2% | 62% | 62% |
| precision | 85% | 23% | 46% | 63% | 77% | 93% | |

## Confident landing-zone disagreements with the traced map

From the best method's LOHO maps (the hole's own map was never seen). Regions >= 60 sq yds where p >= 0.85 and the predicted class differs from the un-eroded traced map; x/y are screen px in the 920x2000 frame. Images with the regions in magenta: output/vision2/<hole>.png.

| Hole | Screen x, y | Area (sq yds) | Map says | Classifier sees | mean p |
|---|---|---|---|---|---|
| 1 | 575, 1039 | 339 | rough | trees | 0.93 |
| 1 | 295, 977 | 163 | rough | fairway | 0.91 |
| 1 | 675, 1056 | 68 | rough | trees | 0.91 |
| 2B | 311, 681 | 270 | rough | fairway | 0.91 |
| 2F | 249, 750 | 77 | rough | fairway | 0.95 |
| 4 | 364, 1025 | 68 | native | fairway | 0.91 |
| 5 | — | — | agrees | — | |
| 6 | 249, 719 | 450 | rough | fairway | 0.96 |
| 8 | — | — | agrees | — | |
| 9B | 458, 817 | 109 | trees | fairway | 0.93 |
| 9F | 612, 685 | 528 | native | trees | 0.94 |
| 9F | 472, 692 | 417 | native | trees | 0.92 |
| 9F | 493, 913 | 154 | trees | fairway | 0.93 |
| 9F | 427, 638 | 112 | native | trees | 0.95 |
| 9F | 466, 986 | 66 | rough | fairway | 0.93 |
| 10 | 402, 778 | 418 | native | fairway | 0.95 |
| 11 | 364, 923 | 95 | rough | fairway | 0.89 |
| 13 | — | — | agrees | — | |
| 14 | — | — | agrees | — | |
| 16 | — | — | agrees | — | |
| 17 | — | — | agrees | — | |
| 18 | 257, 864 | 89 | native | trees | 0.93 |
| 18 | 527, 1208 | 65 | fairway | native | 0.87 |

## Notes

- Best = `ens_raw`; top-2 base methods for calibration/ensembling: ['c', 'b'].
- `output/vision2/probs/<hole>.npz` (key `probs`, float16 (1000,460,6), classes in `classes`) come from the best configuration trained on ALL 16 holes — in-sample for every hole, so use them as the deliverable map, not for accuracy claims. The honest out-of-sample maps behind this report are in `output/vision2/probs_loho/`.
- For the all-holes model, calibration parameters are fitted on the LOHO (out-of-fold) predictions of all 16 holes.
- Training sample: 15000 labelled pixels per hole (fixed seeds); HGB max_iter=150, lr 0.08, 48 leaves, balanced class weights.
- (e) calibration: the nested temperature/isotonic calibration (inner group folds over the 15 training holes) is implemented (`--calib`) but was NOT run for this report — it costs 2 extra HGB fits per held-out hole per method and the shared CPU was oversubscribed. Temperature scaling cannot change any argmax, so it would not move the accuracy columns; it would only change the p>=0.85 flag set. The ensemble row is an uncalibrated fixed 50/50 average (no weights tuned).
