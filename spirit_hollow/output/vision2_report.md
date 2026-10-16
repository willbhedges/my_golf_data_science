# Spirit Hollow — hazard classifier v2 (leave-one-hole-out)

Every number is out-of-sample: each hole is scored with a model trained only on the other 15 holes. Calibration maps (when run, `--calib`) are fitted on inner 2-group-fold predictions over those 15 training holes, so the held-out hole contributes nothing to training, feature scaling, calibration or ensemble weights (the ensemble is a fixed 50/50 average). Pixel methods are 7x7-smoothed before scoring, as in vision.py. Regions: SLIC superpixels (n~2500, compactness 12, on the UI-in-painted half-res photo) and, when deep/sam/ has a mask file for every photo, Segment Anything regions (ViT-B automatic masks; SAM leaves much ground unassigned, so its gaps are split into SLIC cells).

**Labels**: the main table SCORES against the current course.py (label hash `f396950c69`), but the LOHO models were TRAINED on label version `f42fad182c` (course.py after the AUDIT_FIXES landing-zone corrections, commit 8601898). Between the two versions only holes 2B and 2F changed (pond edge and long grass, commit b81bf0e: 4.4k and 2.0k grid px, none of it in the landing-zone geometry). A second table below gives the same models scored on `f42fad182c`, the labels they were trained on. The vision.py baseline row is copied from vision_report.md, which used the earlier pre-audit map. course.py's 'first_cut' bands count as fairway here, as they do in vision.label_map. The final all-holes model behind probs/ is trained on the current labels.

Penal = trees/native/water/sand, playable = fairway/rough. 'bal' = mean per-class recall. Landing zones = 220-340 yds, +/-45 yds of the line.

| Method | LZ 6-class | LZ bal | LZ penal-vs-playable | LZ penal recall | LZ penal precision | Hole 6-class | Hole penal-vs-playable | Hole penal recall | Hole penal precision | NLL | ECE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vision.py baseline (as reported) | 59.4% | | 79.2% | 69% | 55% | 52.4% | 72.5% | 72% | 75% | | |
| Handcrafted + HGB (baseline features, this script's sampler) | 62.3% | 57.8% | 82.4% | 72% | 70% | 54.5% | 75.4% | 75% | 80% | 1.27 | 0.108 |
| (a) DINOv2 linear probe (std. multinomial logreg) | 63.4% | 59.7% | 79.7% | 76% | 64% | 56.4% | 77.6% | 81% | 80% | 1.16 | 0.034 |
| (b) DINOv2 + handcrafted, HGB | 67.9% | 57.2% | 83.2% | 70% | 73% | 58.9% | 78.9% | 79% | 83% | 1.14 | 0.117 |
| (c) handcrafted + photo-relative DINOv2 (fairway-corridor median subtracted), HGB | 69.4% | 59.3% | 84.1% | 69% | 75% | 58.3% | 78.1% | 77% | 83% | 1.18 | 0.125 |
| (d) region classifier on SAM regions (mean/std per region, HGB) | 51.0% | 50.6% | 76.5% | 52% | 63% | 48.5% | 68.3% | 62% | 78% | 1.30 | 0.154 |
| (d') region classifier on SLIC superpixels (mean/std per region, HGB) | 67.4% | 56.6% | 83.0% | 66% | 74% | 56.9% | 77.0% | 76% | 82% | 1.17 | 0.131 |
| (c) probabilities mean-pooled per SAM region | 59.4% | 48.7% | 77.4% | 56% | 64% | 49.2% | 70.7% | 65% | 79% | 1.19 | 0.122 |
| (c) probabilities mean-pooled per SLIC superpixel | 70.0% | 59.9% | 84.0% | 70% | 75% | 58.7% | 78.3% | 78% | 83% | 1.14 | 0.106 |
| **(e) ensemble 50/50 of c + b, uncalibrated** | 69.7% | 59.7% | 84.2% | 70% | 76% | 59.3% | 79.0% | 78% | 83% | 1.13 | 0.102 |

Best (by landing-zone penal-vs-playable accuracy, then 6-class): **(e) ensemble 50/50 of c + b, uncalibrated**.

Reliability of confident pixels (p>=0.85, whole hole, labelled pixels):

| Method | share of pixels with p>=0.85 | accuracy of those |
|---|---|---|
| Handcrafted + HGB (baseline features, this script's sampler) | 23.5% | 79.3% |
| (a) DINOv2 linear probe (std. multinomial logreg) | 13.0% | 83.8% |
| (b) DINOv2 + handcrafted, HGB | 34.1% | 82.9% |
| (c) handcrafted + photo-relative DINOv2 (fairway-corridor median subtracted), HGB | 34.3% | 80.8% |
| (d) region classifier on SAM regions (mean/std per region, HGB) | 26.1% | 78.2% |
| (d') region classifier on SLIC superpixels (mean/std per region, HGB) | 31.4% | 81.0% |
| (c) probabilities mean-pooled per SAM region | 24.0% | 83.6% |
| (c) probabilities mean-pooled per SLIC superpixel | 31.4% | 82.2% |
| (e) ensemble 50/50 of c + b, uncalibrated | 32.2% | 83.6% |

Per-hole landing-zone accuracy of the best method (6-class / penal-vs-playable):

| Hole | 1 | 2B | 2F | 4 | 5 | 6 | 8 | 9B | 9F | 10 | 11 | 13 | 14 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6-class | 70% | 61% | 76% | 69% | 66% | 65% | 74% | 70% | 59% | 79% | 69% | 85% | 79% | 75% | 75% | 55% |
| penal | 84% | 80% | 87% | 70% | 90% | 81% | 83% | 87% | 76% | 87% | 84% | 92% | 92% | 86% | 92% | 79% |

## Confusion matrices — best method (LOHO)

#### Whole visible hole

| traced \ seen | fairway | rough | trees | native | water | sand | recall |
|---|---|---|---|---|---|---|---|
| **fairway** | 72% | 15% | 5% | 7% | 1% | 0% | 72% |
| **rough** | 36% | 31% | 17% | 15% | 1% | 1% | 31% |
| **trees** | 7% | 9% | 73% | 10% | 2% | 0% | 73% |
| **native** | 13% | 22% | 23% | 40% | 2% | 0% | 40% |
| **water** | 3% | 4% | 28% | 4% | 60% | 1% | 60% |
| **sand** | 6% | 21% | 2% | 21% | 1% | 49% | 49% |
| precision | 67% | 28% | 72% | 49% | 63% | 60% | |

#### Landing zones

| traced \ seen | fairway | rough | trees | native | water | sand | recall |
|---|---|---|---|---|---|---|---|
| **fairway** | 84% | 10% | 3% | 3% | 0% | 0% | 84% |
| **rough** | 41% | 30% | 18% | 11% | 0% | 0% | 30% |
| **trees** | 13% | 13% | 63% | 11% | 1% | 0% | 63% |
| **native** | 19% | 19% | 15% | 45% | 3% | 0% | 45% |
| **water** | 5% | 7% | 10% | 3% | 75% | 0% | 75% |
| **sand** | 6% | 18% | 2% | 10% | 2% | 62% | 62% |
| precision | 85% | 23% | 46% | 64% | 79% | 93% | |

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
## Same LOHO maps scored on the labels they were trained on (`f42fad182c`)

| Method | LZ 6-class | LZ penal-vs-playable | LZ penal recall | LZ penal precision | Hole 6-class | Hole penal-vs-playable | Hole penal recall | Hole penal precision |
|---|---|---|---|---|---|---|---|---|
| Handcrafted + HGB (baseline features, this script's sampler) | 62.2% | 82.3% | 72% | 70% | 54.4% | 75.2% | 75% | 80% |
| (a) DINOv2 linear probe (std. multinomial logreg) | 63.3% | 79.6% | 76% | 63% | 56.3% | 77.4% | 81% | 79% |
| (b) DINOv2 + handcrafted, HGB | 67.9% | 83.2% | 70% | 73% | 58.8% | 78.8% | 79% | 83% |
| (c) handcrafted + photo-relative DINOv2 (fairway-corridor median subtracted), HGB | 69.3% | 84.1% | 69% | 75% | 58.2% | 78.0% | 77% | 83% |
| (d) region classifier on SAM regions (mean/std per region, HGB) | 51.1% | 76.5% | 52% | 63% | 48.4% | 68.2% | 61% | 77% |
| (d') region classifier on SLIC superpixels (mean/std per region, HGB) | 67.3% | 82.9% | 66% | 74% | 56.9% | 76.9% | 76% | 82% |
| (c) probabilities mean-pooled per SAM region | 59.4% | 77.4% | 56% | 64% | 49.3% | 70.6% | 65% | 79% |
| (c) probabilities mean-pooled per SLIC superpixel | 70.0% | 84.0% | 70% | 75% | 58.7% | 78.2% | 78% | 83% |
| (e) ensemble 50/50 of c + b, uncalibrated | 69.7% | 84.2% | 70% | 75% | 59.2% | 78.8% | 78% | 83% |

## Same methods on the earlier map (before AUDIT_FIXES)

LOHO trained and scored on the labels in course.py as of 17:58 today. Only the first three methods finished before the map changed. Same protocol and seeds, so the difference from the main table comes from the labels.

| Method | LZ 6-class | LZ penal-vs-playable | LZ penal recall | LZ penal precision | Hole 6-class | Hole penal-vs-playable |
|---|---|---|---|---|---|---|
| Handcrafted + HGB (baseline features, this script's sampler) | 59.5% | 80.1% | 73% | 56% | 52.5% | 73.4% |
| (a) DINOv2 linear probe (std. multinomial logreg) | 59.6% | 75.1% | 72% | 48% | 54.7% | 74.9% |
| (b) DINOv2 + handcrafted, HGB | 66.2% | 83.1% | 69% | 63% | 57.9% | 78.2% |


## Notes

- Best = `ens_raw`; top-2 base methods for calibration/ensembling: ['c', 'b'].
- `output/vision2/probs/<hole>.npz` (key `probs`, float16 (1000,460,6), classes in `classes`) come from the best configuration trained on ALL 16 holes — in-sample for every hole, so use them as the deliverable map, not for accuracy claims. The honest out-of-sample maps behind this report are in `output/vision2/probs_loho/`.
- If a calibrated method is chosen as best, the all-holes model's calibration is fitted on the LOHO (out-of-fold) predictions of all 16 holes.
- HGB uses early stopping on a random 10% of the TRAINING pixels (n_iter_no_change=10).
- SAM regions (method d and SAM pooling) do worse than SLIC. There are only 60-110 SAM masks per photo and 36-82% of the ground has none, so the regions are large, cross class boundaries (fairway into rough, tree line into native), and the 70% purity rule drops most of them from training.
- Training sample: 15000 labelled pixels per hole (fixed seeds); HGB max_iter=150, lr 0.08, 48 leaves, balanced class weights.
- (e) calibration: the nested temperature/isotonic calibration (inner group folds over the 15 training holes) is implemented (`--calib`) but was NOT run for this report — it costs 2 extra HGB fits per held-out hole per method and the shared CPU was oversubscribed. Temperature scaling cannot change any argmax, so it would not move the accuracy columns; it would only change the p>=0.85 flag set. The ensemble row is an uncalibrated fixed 50/50 average (no weights tuned).
