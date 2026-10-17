# Hand-map answers vs three truths (Black tees, Black-box tees)

Same club on the tee shots of the hand map (Black: 2F / 9F).

| Geometry | answers (changing) | final_decision.json | QA hand map, quick | same plan on the hand map |
|---|---|---|---|---|
| auto package (before) | - | 5/14 | 9/14 | 8/14 |
| answer the red items | 15 (11) | 7/14 | 11/14 | 10/14 |
| answer the red + amber items | 50 (38) | 9/14 | 9/14 | 8/14 |
| answer every tested item | 135 (86) | 11/14 | 11/14 | 10/14 |
| hand Black-box tees, every hole | - | 7/14 | 11/14 | 10/14 |
| hand zones, every hole | - | 11/14 | 13/14 | 14/14 |
| hand tees + zones, every hole | - | 11/14 | 13/14 | 14/14 |

Per hole (club picks):

| Hole | before | after red | after red_amber | after all | hand all | final | QA hand | 
|---|---|---|---|---|---|---|---|
| 4 | 4-wood | 4-wood | 4-wood | 4-wood | Driver | Driver | Driver |
| 5 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 1 | Long iron | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 2 | Driver | Driver | Driver | Driver | Driver | Driver | Driver |
| 8 | Long iron | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 6 | 4-wood | 4-wood | 4-wood | 4-wood | 2-wood | 2-wood | 4-wood |
| 9 | 4-wood | 4-wood | Long iron | 4-wood | 4-wood | 4-wood | 4-wood |
| 10 | 4-wood | 4-wood | Driver | Driver | 4-wood | Driver | 4-wood |
| 13 | Long iron | Long iron | 4-wood | Driver | Driver | Driver | Driver |
| 11 | Long iron | Long iron | Long iron | Long iron | Long iron | Long iron | Long iron |
| 16 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood |
| 14 | 4-wood | 4-wood | 2-wood | 2-wood | 4-wood | 2-wood | 4-wood |
| 17 | 4-wood | 4-wood | Driver | Driver | Driver | Driver | Driver |
| 18 | 4-wood | 4-wood | 4-wood | 4-wood | 4-wood | 2-wood | 4-wood |

## Answers: red

| Item | Sev | Answer |
|---|---|---|
| 1-native-left | red | moved {'shift': -14.6} |
| 14-tee | red | moved {'dx': 21.5, 'dy': -3.4} |
| 4-native-across | red | moved {'shift': -10.0} |
| 8-native-left | red | absent  |
| 2-tee | red | confirm  |
| 6-tee | red | moved {'dx': -12.7, 'dy': -2.2} |
| 13-tee | red | confirm  |
| 9-tee | red | moved {'dx': 1.4, 'dy': -8.9} |
| 8-tee | red | confirm  |
| 10-tee | red | moved {'dx': -5.9, 'dy': 1.2} |
| 1-tee | red | moved {'dx': -23.9, 'dy': -9.5} |
| 11-tee | red | confirm  |
| 18-tee | red | moved {'dx': 4.5, 'dy': 4.2} |
| 4-tee | red | moved {'dx': -0.5, 'dy': 10.8} |
| 5-tee | red | moved {'dx': -10.5, 'dy': 1.2} |

## Answers: red + amber

| Item | Sev | Answer |
|---|---|---|
| 1-native-left | red | moved {'shift': -14.6} |
| 14-tee | red | moved {'dx': 21.5, 'dy': -3.4} |
| 4-native-across | red | moved {'shift': -10.0} |
| 8-native-left | red | absent  |
| 2-tee | red | confirm  |
| 6-tee | red | moved {'dx': -12.7, 'dy': -2.2} |
| 13-tee | red | confirm  |
| 9-tee | red | moved {'dx': 1.4, 'dy': -8.9} |
| 8-tee | red | confirm  |
| 10-tee | red | moved {'dx': -5.9, 'dy': 1.2} |
| 1-tee | red | moved {'dx': -23.9, 'dy': -9.5} |
| 11-tee | red | confirm  |
| 18-tee | red | moved {'dx': 4.5, 'dy': 4.2} |
| 4-tee | red | moved {'dx': -0.5, 'dy': 10.8} |
| 5-tee | red | moved {'dx': -10.5, 'dy': 1.2} |
| 11-native-left | amber | confirm  |
| 14-native-across | amber | moved {'shift': -21.0} |
| 13-native-right | amber | absent  |
| 18-water-across | amber | confirm {'why': 'other hand trouble there'} |
| 14-cut | amber | present {'area': 3708} |
| 10-water-left | amber | moved {'shift': -8.9} |
| 10-native-right | amber | absent  |
| 1-fairway-right | amber | moved {'shift': -7.3} |
| 18-native-across | amber | moved {'shift': -20.0} |
| 13-native-across | amber | absent  |
| 17-native-left | amber | absent  |
| 8-native-across | amber | absent  |
| 10-cut | amber | present {'area': 1850} |
| 2-native-across | amber | confirm {'why': 'other hand trouble there'} |
| 17-fairway-left | amber | moved {'shift': -13.3} |
| 8-fairway-left | amber | moved {'shift': -18.5} |
| 5-native-left | amber | moved {'shift': -9.3} |
| 1-recovery-across | amber | moved {'shift': -8.9} |
| 9-fairway-left | amber | moved {'shift': -15.4} |
| 9-native-left | amber | confirm  |
| 16-native-left | amber | moved {'shift': -7.7} |
| 11-fairway-left | amber | moved {'shift': -6.2} |
| 2-native-right | amber | moved {'shift': -11.8} |
| 6-native-across | amber | confirm  |
| 11-fairway-right | amber | moved {'shift': -16.4} |
| 2-water-left | amber | confirm  |
| 9-water-right | amber | moved {'shift': 5.5} |
| 9-fairway-right | amber | confirm  |
| 16-recovery-right | amber | confirm  |
| 9-native-right | amber | moved {'shift': 30.0} |
| 2-cut | amber | present {'area': 3655} |
| 8-fairway-right | amber | moved {'shift': -15.5} |
| 9-recovery-across | amber | moved {'shift': 28.7} |
| 6-fairway-left | amber | moved {'shift': -10.9} |
| 18-fairway-right | amber | moved {'shift': -30.0} |

## Answers: all

| Item | Sev | Answer |
|---|---|---|
| 1-native-left | red | moved {'shift': -14.6} |
| 14-tee | red | moved {'dx': 21.5, 'dy': -3.4} |
| 4-native-across | red | moved {'shift': -10.0} |
| 8-native-left | red | absent  |
| 2-tee | red | confirm  |
| 6-tee | red | moved {'dx': -12.7, 'dy': -2.2} |
| 13-tee | red | confirm  |
| 9-tee | red | moved {'dx': 1.4, 'dy': -8.9} |
| 8-tee | red | confirm  |
| 10-tee | red | moved {'dx': -5.9, 'dy': 1.2} |
| 1-tee | red | moved {'dx': -23.9, 'dy': -9.5} |
| 11-tee | red | confirm  |
| 18-tee | red | moved {'dx': 4.5, 'dy': 4.2} |
| 4-tee | red | moved {'dx': -0.5, 'dy': 10.8} |
| 5-tee | red | moved {'dx': -10.5, 'dy': 1.2} |
| 11-native-left | amber | confirm  |
| 14-native-across | amber | moved {'shift': -21.0} |
| 13-native-right | amber | absent  |
| 18-water-across | amber | confirm {'why': 'other hand trouble there'} |
| 14-cut | amber | present {'area': 3708} |
| 10-water-left | amber | moved {'shift': -8.9} |
| 10-native-right | amber | absent  |
| 1-fairway-right | amber | moved {'shift': -7.3} |
| 18-native-across | amber | moved {'shift': -20.0} |
| 13-native-across | amber | absent  |
| 17-native-left | amber | absent  |
| 8-native-across | amber | absent  |
| 10-cut | amber | present {'area': 1850} |
| 2-native-across | amber | confirm {'why': 'other hand trouble there'} |
| 17-fairway-left | amber | moved {'shift': -13.3} |
| 8-fairway-left | amber | moved {'shift': -18.5} |
| 5-native-left | amber | moved {'shift': -9.3} |
| 1-recovery-across | amber | moved {'shift': -8.9} |
| 9-fairway-left | amber | moved {'shift': -15.4} |
| 9-native-left | amber | confirm  |
| 16-native-left | amber | moved {'shift': -7.7} |
| 11-fairway-left | amber | moved {'shift': -6.2} |
| 2-native-right | amber | moved {'shift': -11.8} |
| 6-native-across | amber | confirm  |
| 11-fairway-right | amber | moved {'shift': -16.4} |
| 2-water-left | amber | confirm  |
| 9-water-right | amber | moved {'shift': 5.5} |
| 9-fairway-right | amber | confirm  |
| 16-recovery-right | amber | confirm  |
| 9-native-right | amber | moved {'shift': 30.0} |
| 2-cut | amber | present {'area': 3655} |
| 8-fairway-right | amber | moved {'shift': -15.5} |
| 9-recovery-across | amber | moved {'shift': 28.7} |
| 6-fairway-left | amber | moved {'shift': -10.9} |
| 18-fairway-right | amber | moved {'shift': -30.0} |
| 17-native-right | green | absent  |
| 14-fairway-right | green | moved {'shift': -28.1} |
| 1-cut | green | present {'area': 1900} |
| 13-fairway-right | green | moved {'shift': -10.8} |
| 16-tee | green | moved {'dx': 23.9, 'dy': -9.1} |
| 17-tee | green | moved {'dx': 28.6, 'dy': 3.0} |
| 10-fairway-left | green | moved {'shift': -8.4} |
| 5-fairway-right | green | moved {'shift': 6.0} |
| 16-fairway-left | green | moved {'shift': -18.0} |
| 2-fairway-left | green | moved {'shift': -11.9} |
| 5-fairway-left | green | moved {'shift': -9.7} |
| 17-fairway-right | green | moved {'shift': -11.5} |
| 4-fairway-right | green | confirm  |
| 8-native-right | green | confirm  |
| 5-cut | green | present {'area': 1907} |
| 16-fairway-right | green | moved {'shift': -5.4} |
| 6-native-right | green | absent  |
| 10-fairway-right | green | moved {'shift': -12.7} |
| 18-fairway-left | green | moved {'shift': -11.4} |
| 11-water-across | green | confirm {'why': 'other hand trouble there'} |
| 13-fairway-left | green | moved {'shift': -25.2} |
| 14-recovery-across | green | confirm  |
| 2-fairway-right | green | moved {'shift': -15.5} |
| 16-native-right | green | confirm {'why': 'other hand trouble there'} |
| 14-fairway-left | green | moved {'shift': -8.5} |
| 4-fairway-left | green | confirm  |
| 18-cut | green | present {'area': 1801} |
| 6-fairway-right | green | confirm  |
| 6-cut | green | present {'area': 1316} |
| 10-native-left | green | moved {'shift': -6.0} |
| 17-cut | green | present {'area': 3187} |
| 13-cut | green | present {'area': 3928} |
| 8-cut | green | present {'area': 3097} |
| 16-cut | green | present {'area': 3069} |
| 11-cut | green | present {'area': 2891} |
| 2-sand-right | green | confirm  |
| 1-native-right | green | confirm {'why': 'other hand trouble there'} |
| 5-sand-right | green | confirm  |
| 4-cut | green | present {'area': 460} |
| 1-recovery-left | green | moved {'shift': -10.9} |
| 13-recovery-left | green | moved {'shift': -10.2} |
| 5-native-right | green | absent  |
| 9-cut | green | present {'area': 1669} |
| 8-sand-right | green | confirm  |
| 13-water-right | green | confirm  |
| 17-recovery-right | green | moved {'shift': -13.6} |
| 16-sand-left | green | confirm  |
| 10-recovery-left | green | confirm  |
| 10-water-right | green | confirm  |
| 16-recovery-left | green | absent  |
| 2-recovery-right | green | absent  |
| 16-sand-right | green | confirm  |
| 11-recovery-left | green | moved {'shift': -8.3} |
| 18-native-left | green | moved {'shift': 5.1} |
| 11-recovery-right | green | confirm  |
| 18-recovery-across | green | confirm {'why': 'other hand trouble there'} |
| 6-recovery-left | green | moved {'shift': -18.8} |
| 4-recovery-across | green | confirm {'why': 'other hand trouble there'} |
| 1-ob-across | green | confirm {'why': 'other hand trouble there'} |
| 2-recovery-left | green | confirm {'why': 'other hand trouble there'} |
| 2-ob-right | green | absent  |
| 2-ob-left | green | confirm {'why': 'other hand trouble there'} |
| 2-sand-left | green | confirm  |
| 5-sand-left | green | confirm  |
| 5-recovery-left | green | absent  |
| 5-recovery-right | green | confirm  |
| 6-ob-right | green | absent  |
| 8-ob-right | green | moved {'shift': 13.0} |
| 8-recovery-right | green | absent  |
| 8-sand-left | green | confirm  |
| 8-recovery-left | green | absent  |
| 9-recovery-right | green | confirm  |
| 10-sand-right | green | confirm  |
| 11-native-right | green | confirm  |
| 11-sand-left | green | confirm {'why': 'other hand trouble there'} |
| 11-water-right | green | confirm  |
| 13-sand-left | green | confirm  |
| 13-sand-right | green | confirm  |
| 13-recovery-right | green | absent  |
| 14-water-right | green | confirm {'why': 'other hand trouble there'} |
| 14-native-left | green | confirm {'why': 'other hand trouble there'} |
| 14-sand-left | green | absent  |
| 16-ob-left | green | confirm {'why': 'other hand trouble there'} |
| 17-sand-left | green | confirm  |
| 18-native-right | green | moved {'shift': 9.4} |
