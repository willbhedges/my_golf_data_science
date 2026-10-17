# Hand-map answers vs three truths (Black tees, Black-box tees)

Same club on the tee shots of the hand map (Black: 2F / 9F).

| Geometry | answers (changing) | final_decision.json | QA hand map, quick | same plan on the hand map |
|---|---|---|---|---|
| auto package (before) | - | 9/14 | 6/14 | 10/14 |
| answer the red items | 11 (7) | 9/14 | 6/14 | 10/14 |
| answer the red + amber items | 36 (23) | 8/14 | 5/14 | 11/14 |
| answer every tested item | 131 (79) | 9/14 | 5/14 | 9/14 |
| hand Black-box tees, every hole | - | 8/14 | 5/14 | 11/14 |
| hand zones, every hole | - | 7/14 | 7/14 | 12/14 |
| hand tees + zones, every hole | - | 7/14 | 5/14 | 14/14 |

Per hole (club picks):

| Hole | before | after red | after red_amber | after all | hand all | final | QA hand | 
|---|---|---|---|---|---|---|---|
| 4 | Driver | Driver | Driver | Driver | 4-wood | Driver | Driver |
| 5 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 2-wood | 4-wood |
| 2 | Driver | Driver | Driver | Driver | Driver | Driver | Driver |
| 1 | Driver | Driver | Driver | 2-wood | 4-wood | 4-wood | 4-wood |
| 9 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 6 | Driver | Driver | Driver | Driver | 4-wood | Driver | 2-wood |
| 8 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 11 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | Long iron |
| 13 | Driver | Driver | 4-wood | 2-wood | 4-wood | Driver | Driver |
| 10 | Driver | Driver | Driver | Driver | Driver | 4-wood | 4-wood |
| 16 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | Driver | 2-wood |
| 17 | Driver | Driver | Driver | Driver | Driver | Driver | 2-wood |
| 14 | 2-wood | 2-wood | 2-wood | 2-wood | 2-wood | 2-wood | 4-wood |
| 18 | Driver | Driver | Driver | 2-wood | Driver | 2-wood | 4-wood |

## Answers: red

| Item | Sev | Answer |
|---|---|---|
| 11-tee | red | confirm  |
| 14-tee | red | moved {'dx': 21.5, 'dy': -3.4} |
| 14-native-across | red | moved {'shift': -5.9} |
| 14-check | red | - {'why': 'no oracle'} |
| 11-cut | red | present {'area': 2891} |
| 2-tee | red | confirm  |
| 13-tee | red | confirm  |
| 8-tee | red | confirm  |
| 1-tee | red | moved {'dx': -23.9, 'dy': -9.5} |
| 6-tee | red | moved {'dx': -12.7, 'dy': -2.2} |
| 16-tee | red | moved {'dx': 23.9, 'dy': -9.1} |
| 5-tee | red | moved {'dx': -10.5, 'dy': 1.2} |

## Answers: red + amber

| Item | Sev | Answer |
|---|---|---|
| 11-tee | red | confirm  |
| 14-tee | red | moved {'dx': 21.5, 'dy': -3.4} |
| 14-native-across | red | moved {'shift': -5.9} |
| 14-check | red | - {'why': 'no oracle'} |
| 11-cut | red | present {'area': 2891} |
| 2-tee | red | confirm  |
| 13-tee | red | confirm  |
| 8-tee | red | confirm  |
| 1-tee | red | moved {'dx': -23.9, 'dy': -9.5} |
| 6-tee | red | moved {'dx': -12.7, 'dy': -2.2} |
| 16-tee | red | moved {'dx': 23.9, 'dy': -9.1} |
| 5-tee | red | moved {'dx': -10.5, 'dy': 1.2} |
| 4-native-left | amber | moved {'shift': -7.2} |
| 18-water-across | amber | confirm {'why': 'other hand trouble there'} |
| 11-water-across | amber | confirm {'why': 'other hand trouble there'} |
| 11-recovery-left | amber | confirm  |
| 17-native-left | amber | confirm  |
| 13-recovery-right | amber | confirm  |
| 13-fairway-right | amber | moved {'shift': -10.8} |
| 13-native-left | amber | absent  |
| 16-native-right | amber | confirm {'why': 'other hand trouble there'} |
| 6-recovery-left | amber | confirm  |
| 4-native-right | amber | moved {'shift': 9.7} |
| 2-water-left | amber | confirm  |
| 17-tee | amber | moved {'dx': 28.6, 'dy': 3.0} |
| 5-fairway-right | amber | moved {'shift': 6.0} |
| 11-fairway-left | amber | moved {'shift': -7.5} |
| 5-fairway-left | amber | moved {'shift': -9.7} |
| 8-fairway-left | amber | moved {'shift': -18.5} |
| 10-tee | amber | moved {'dx': -5.9, 'dy': 1.2} |
| 10-water-left | amber | confirm  |
| 16-fairway-left | amber | moved {'shift': -18.0} |
| 16-cut | amber | present {'area': 3069} |
| 8-fairway-right | amber | moved {'shift': -15.5} |
| 18-tee | amber | moved {'dx': 4.5, 'dy': 4.2} |
| 16-recovery-right | amber | moved {'shift': 6.4} |
| 9-fairway-left | amber | moved {'shift': -15.4} |

## Answers: all

| Item | Sev | Answer |
|---|---|---|
| 11-tee | red | confirm  |
| 14-tee | red | moved {'dx': 21.5, 'dy': -3.4} |
| 14-native-across | red | moved {'shift': -5.9} |
| 14-check | red | - {'why': 'no oracle'} |
| 11-cut | red | present {'area': 2891} |
| 2-tee | red | confirm  |
| 13-tee | red | confirm  |
| 8-tee | red | confirm  |
| 1-tee | red | moved {'dx': -23.9, 'dy': -9.5} |
| 6-tee | red | moved {'dx': -12.7, 'dy': -2.2} |
| 16-tee | red | moved {'dx': 23.9, 'dy': -9.1} |
| 5-tee | red | moved {'dx': -10.5, 'dy': 1.2} |
| 4-native-left | amber | moved {'shift': -7.2} |
| 18-water-across | amber | confirm {'why': 'other hand trouble there'} |
| 11-water-across | amber | confirm {'why': 'other hand trouble there'} |
| 11-recovery-left | amber | confirm  |
| 17-native-left | amber | confirm  |
| 13-recovery-right | amber | confirm  |
| 13-fairway-right | amber | moved {'shift': -10.8} |
| 13-native-left | amber | absent  |
| 16-native-right | amber | confirm {'why': 'other hand trouble there'} |
| 6-recovery-left | amber | confirm  |
| 4-native-right | amber | moved {'shift': 9.7} |
| 2-water-left | amber | confirm  |
| 17-tee | amber | moved {'dx': 28.6, 'dy': 3.0} |
| 5-fairway-right | amber | moved {'shift': 6.0} |
| 11-fairway-left | amber | moved {'shift': -7.5} |
| 5-fairway-left | amber | moved {'shift': -9.7} |
| 8-fairway-left | amber | moved {'shift': -18.5} |
| 10-tee | amber | moved {'dx': -5.9, 'dy': 1.2} |
| 10-water-left | amber | confirm  |
| 16-fairway-left | amber | moved {'shift': -18.0} |
| 16-cut | amber | present {'area': 3069} |
| 8-fairway-right | amber | moved {'shift': -15.5} |
| 18-tee | amber | moved {'dx': 4.5, 'dy': 4.2} |
| 16-recovery-right | amber | moved {'shift': 6.4} |
| 9-fairway-left | amber | moved {'shift': -15.4} |
| 16-fairway-right | green | moved {'shift': -5.4} |
| 14-fairway-right | green | moved {'shift': -28.1} |
| 13-native-across | green | absent  |
| 4-fairway-right | green | confirm  |
| 17-fairway-right | green | moved {'shift': -11.5} |
| 10-fairway-left | green | moved {'shift': -8.4} |
| 13-water-right | green | confirm  |
| 13-cut | green | present {'area': 3928} |
| 14-fairway-left | green | moved {'shift': -8.5} |
| 9-fairway-right | green | confirm  |
| 2-fairway-left | green | moved {'shift': -11.9} |
| 5-cut | green | present {'area': 1907} |
| 11-fairway-right | green | moved {'shift': -15.5} |
| 17-fairway-left | green | moved {'shift': -13.3} |
| 6-fairway-left | green | moved {'shift': -10.9} |
| 2-ob-right | green | moved {'shift': -15.8} |
| 10-water-right | green | confirm  |
| 6-native-left | green | moved {'shift': 14.9} |
| 6-fairway-right | green | confirm  |
| 4-fairway-left | green | confirm  |
| 10-recovery-left | green | moved {'shift': 7.3} |
| 18-fairway-left | green | moved {'shift': -11.4} |
| 8-gap-left | green | confirm {'cov': 0.27} |
| 4-recovery-right | green | confirm {'why': 'other hand trouble there'} |
| 10-fairway-right | green | moved {'shift': -12.7} |
| 1-recovery-across | green | moved {'shift': 13.5} |
| 6-native-right | green | confirm  |
| 9-tee | green | moved {'dx': 1.4, 'dy': -8.9} |
| 4-tee | green | moved {'dx': -0.5, 'dy': 10.8} |
| 4-cut | green | present {'area': 460} |
| 8-cut | green | present {'area': 3097} |
| 5-sand-right | green | confirm  |
| 17-recovery-right | green | confirm  |
| 18-recovery-left | green | confirm {'why': 'other hand trouble there'} |
| 2-cut | green | present {'area': 3655} |
| 18-fairway-right | green | moved {'shift': -30.0} |
| 9-recovery-right | green | moved {'shift': 8.6} |
| 16-sand-left | green | confirm  |
| 16-recovery-left | green | confirm  |
| 1-cut | green | present {'area': 1900} |
| 18-cut | green | present {'area': 1801} |
| 13-sand-left | green | confirm  |
| 9-recovery-across | green | moved {'shift': 30.0} |
| 10-cut | green | present {'area': 1850} |
| 1-fairway-left | green | moved {'shift': -10.7} |
| 2-fairway-right | green | moved {'shift': -15.5} |
| 6-cut | green | present {'area': 1316} |
| 13-fairway-left | green | moved {'shift': -25.2} |
| 9-cut | green | present {'area': 1669} |
| 14-recovery-left | green | moved {'shift': 6.7} |
| 14-cut | green | present {'area': 3708} |
| 1-fairway-right | green | moved {'shift': -7.3} |
| 17-cut | green | present {'area': 3187} |
| 1-recovery-right | green | confirm  |
| 2-sand-right | green | confirm  |
| 9-water-right | green | confirm  |
| 16-ob-left | green | confirm {'why': 'other hand trouble there'} |
| 8-sand-right | green | confirm  |
| 16-sand-right | green | confirm  |
| 8-recovery-right | green | confirm  |
| 14-water-right | green | confirm {'why': 'other hand trouble there'} |
| 9-native-left | green | moved {'shift': 30.0} |
| 16-native-left | green | confirm  |
| 17-sand-left | green | confirm  |
| 1-ob-right | green | absent  |
| 5-native-right | green | absent  |
| 8-native-right | green | confirm  |
| 18-native-right | green | moved {'shift': 21.6} |
| 11-water-right | green | confirm  |
| 2-recovery-right | green | absent  |
| 11-recovery-across | green | moved {'shift': 30.0} |
| 1-native-left | green | moved {'shift': 30.0} |
| 1-recovery-left | green | confirm  |
| 2-recovery-left | green | moved {'shift': 10.0} |
| 2-native-across | green | moved {'shift': -6.6} |
| 2-ob-left | green | confirm {'why': 'other hand trouble there'} |
| 2-native-right | green | confirm  |
| 2-sand-left | green | confirm  |
| 5-sand-left | green | confirm  |
| 5-recovery-left | green | absent  |
| 5-recovery-right | green | moved {'shift': -5.4} |
| 8-ob-right | green | moved {'shift': 15.0} |
| 8-native-left | green | confirm  |
| 8-recovery-left | green | absent  |
| 9-native-right | green | moved {'shift': 26.1} |
| 10-native-right | green | absent  |
| 10-sand-right | green | confirm  |
| 11-native-across | green | moved {'shift': 30.0} |
| 11-native-right | green | absent  |
| 11-native-left | green | confirm  |
| 11-sand-left | green | confirm {'why': 'other hand trouble there'} |
| 14-recovery-across | green | confirm  |
| 14-native-left | green | confirm {'why': 'other hand trouble there'} |
| 14-sand-left | green | absent  |
| 14-native-right | green | confirm  |
