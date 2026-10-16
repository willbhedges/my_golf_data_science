# Spirit Hollow — hazard detection (leave-one-hole-out)

Each hole is predicted by a model trained only on the *other* holes, so these are out-of-sample numbers. Rows are the traced (reviewed) label, columns what the classifier sees.

### Whole visible hole

| traced \ seen | fairway | rough | trees | native | water | sand | recall |
|---|---|---|---|---|---|---|---|
| **fairway** | 61% | 20% | 11% | 7% | 1% | 0% | 61% |
| **rough** | 28% | 33% | 21% | 17% | 1% | 0% | 33% |
| **trees** | 10% | 15% | 63% | 7% | 5% | 0% | 63% |
| **native** | 13% | 25% | 21% | 36% | 4% | 1% | 36% |
| **water** | 1% | 6% | 26% | 4% | 63% | 0% | 63% |
| **sand** | 3% | 13% | 3% | 25% | 1% | 55% | 55% |
| precision | 64% | 27% | 64% | 45% | 44% | 57% | |

Overall pixel accuracy (6 classes): **52.4%**
Penal (trees/long grass/water/sand) vs playable (fairway/rough): accuracy **72.5%**, penal recall 72%, penal precision 75%

### Landing zones only (220-340 yds, +/-45 yds)

| traced \ seen | fairway | rough | trees | native | water | sand | recall |
|---|---|---|---|---|---|---|---|
| **fairway** | 71% | 17% | 7% | 4% | 1% | 0% | 71% |
| **rough** | 30% | 31% | 24% | 14% | 1% | 0% | 31% |
| **trees** | 13% | 17% | 52% | 11% | 7% | 0% | 52% |
| **native** | 14% | 25% | 20% | 37% | 5% | 0% | 37% |
| **water** | 2% | 9% | 16% | 2% | 72% | 0% | 72% |
| **sand** | 4% | 16% | 2% | 10% | 2% | 65% | 65% |
| precision | 86% | 23% | 18% | 49% | 60% | 92% | |

Overall pixel accuracy (6 classes): **59.4%**
Penal (trees/long grass/water/sand) vs playable (fairway/rough): accuracy **79.2%**, penal recall 69%, penal precision 55%

## Confident disagreements in the landing zones

Regions >= 60 sq yds where the classifier is >= 80% sure and disagrees with the map. Each was checked by eye at full zoom (see the strategy README for outcomes).

| Hole | Where (screen x, y) | Size (sq yds) | Map says | Classifier sees |
|---|---|---|---|---|
| 1 | 571, 1027 | 393 | rough | trees |
| 1 | 297, 1005 | 301 | native | fairway |
| 1 | 280, 1347 | 149 | native | trees |
| 1 | 304, 1200 | 60 | native | rough |
| 2B | 537, 664 | 126 | native | trees |
| 2B | 314, 687 | 106 | rough | fairway |
| 2F | 250, 963 | 274 | rough | water |
| 2F | 246, 775 | 112 | rough | fairway |
| 4 | — | — | agrees | — |
| 5 | 573, 1110 | 237 | rough | fairway |
| 5 | 581, 959 | 70 | sand | native |
| 6 | 248, 722 | 494 | rough | fairway |
| 6 | 550, 956 | 130 | rough | fairway |
| 8 | 301, 1065 | 120 | rough | native |
| 9B | — | — | agrees | — |
| 9F | 457, 691 | 366 | native | trees |
| 9F | 579, 674 | 117 | native | trees |
| 9F | 427, 638 | 112 | native | trees |
| 10 | 375, 749 | 146 | trees | fairway |
| 10 | 382, 947 | 90 | water | trees |
| 10 | 659, 1132 | 89 | fairway | rough |
| 10 | 386, 1023 | 78 | water | trees |
| 11 | 460, 568 | 69 | fairway | trees |
| 13 | 322, 770 | 120 | rough | trees |
| 14 | 323, 1043 | 584 | rough | trees |
| 14 | 307, 754 | 422 | rough | fairway |
| 14 | 576, 852 | 153 | native | water |
| 14 | 529, 744 | 77 | native | water |
| 16 | — | — | agrees | — |
| 17 | — | — | agrees | — |
| 18 | 334, 1142 | 393 | fairway | trees |
| 18 | 518, 866 | 245 | native | trees |
| 18 | 281, 917 | 97 | native | trees |
