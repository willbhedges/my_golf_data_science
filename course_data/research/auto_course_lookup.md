# Automatic course lookup: how the GPS apps do it, what we can legally use, and the plan

Research spike, 2026-10-16 (research scientist). Question: how do we get to "the golfer types a US course
name and picks a tee set, and in under 15 minutes gets a verified package (holes, greens, hazards, the
exact tee boxes for that set) and a DECADE strategy book"? Sources are linked inline and listed in
section 10. The machine-readable source list is `auto_course_lookup.json`. The prototype is
`open_sources.py` with `.github/workflows/research_fetch.yml`. Its results are in section 6 and
`probe.json`.

Pipeline baseline (from `ARCHITECTURE.md` §8 and `qa/REPORT.md`, Spirit Hollow golden):

- The club matches the hand map on 50-69% of tee shots, against a bar of 80%.
- Greens land within 10 yds on 75% of holes.
- Tees land within 10 yds on 25-50% of holes.
- Landing-zone IoU is about 0.15-0.23 for trees, about 0.09 for long grass and about 0.3-0.4 for water, against a bar of 0.6.
- OSM gives no trees, no native grass, no OB and no tee colours.

---

## 0. Top findings

1. **Nobody in the industry does this fully automatically.** Every major app relies on humans, an
   aerial-imagery tracing workflow and a feedback loop from golfers.
   - Shot Scope says it maps "in house" from satellite imagery in "20 minutes to 2 hours" per course,
     and turns updates around in 48 h.
   - Hole19 answers mapping requests within 48 h.
   - Golfshot promises 14 days and publishes monthly update lists (320 courses in September 2026).
   - SkyCaddie walks courses.
   - Arccos crowdsources pin positions and fixes maps from user email.

   Our "18 Birdies-style experience" is therefore realistic only as **auto-draft + targeted human
   confirmation**. The automation decides *what* the golfer has to check.
2. **18Birdies itself does not place tees per colour automatically.** Its help centre says: "tee box
   locations are manually set by our team, and they set the tee location at the farthest back set
   of tees". The golfer is told to drag the tee icon if it is wrong.
   ([18Birdies help 588](https://help.18birdies.com/article/588-gps-shows-a-different-set-of-tees-than-what-i-selected))
   This matters for our metrics. Our hand-traced Spirit Hollow "truth" came from 18Birdies screenshots,
   and on holes 2 and 9 the app was showing the Gold boxes (`tees/README.md`: 2B = 609 vs Gold 607, 9B
   = 399 vs Gold 410). **A good part of the "30-100 yd tee error" is the reference's own tee, not
   ours.** Acceptance has to label each traced hole with the card set it actually shows before it
   scores tee placement (plan item Q1).
3. **There is a free, key-less, ODbL scorecard API: OpenGolfAPI** ([api](https://github.com/opengolfapi/api),
   [data](https://github.com/opengolfapi/data)).
   - Anonymous use allows 1,000 calls/day.
   - Search, tees (name, colour, rating, slope, yardage) and per-hole yardages by colour.
   - About 16k US courses.
   - Its own per-hole geometry layer ("OpenGolfGeo": tee coordinates, green F/C/B, polygons) is
     gated as paid. It is not available, and its accuracy is unvalidated by the vendor.
   - Its bulk dump is weak for scorecards: only 22 of 15,667 rows have all 18 pars. It is fine as a
     name/coordinate/OSM-id resolver.

   Prototype results (§6):
   - **Veenker** matches our card to 0.9-3.1 yd MAE per set, with 16-17/18 holes within 3 yd.
   - **Spirit Hollow** has current tee totals but *stale* per-hole Gold (17 yd MAE) and stroke index.
     The stale data is detectable because the per-hole sums don't equal the totals.
   - **Mozingo's 18 is missing.**
4. **Per-colour tee GPS points exist only in licensed databases.**
   - iGolf Connect offers "tee box center points for up to 5 tees per hole", plus F/C/B green points
     and 4 hazard points ([iGolf Connect](https://igolfconnect.com/golf-data)).
   - GolfAPI.io has tee and POI coordinates, behind a key on request.
   - Golfbert has hole polygons and tee boxes, behind a key.
   - Golf Intelligence has tee, fairway, bunker, penalty and green polygons, at $49 test credits and
     $399/mo, and **its terms forbid bulk caching and training models on the data**.

   None of them is free. Every one restricts redistribution, which conflicts with our open/ODbL stack.
   The USGA NCRDB gives the official tee sets with rating, slope, bogey rating and *total* length,
   but no per-hole data, and it blocks scripts. GHIN is gated behind the USGA GPA programme.
5. **A ready-made, NAIP-native golf segmentation model exists.**
   [`ariadgolf/golf-course-segmentation`](https://huggingface.co/ariadgolf/golf-course-segmentation)
   is a U-Net/ResNet-34 trained on 4,665 NAIP 0.6 m RGB+NIR tiles from 790 US courses, with OSM
   labels. It reports validation IoU of green 0.69, fairway 0.64, bunker 0.56, tee 0.33 and water
   0.03. It runs on a CPU in about a minute per course (estimate; section 3.3).
   - Weights licence: not confirmed. Check before use.
   - It does not cover trees, native grass or OB, which are our real gaps. It does give fairway edges
     and **tee candidates where OSM is missing boxes** (Spirit Hollow 2 at 607, 15 at 215, 17).
6. **Trees and long grass are a label-definition problem as much as a model problem.**
   - The hand map draws tree lines at the trunks, while lidar HAG draws them at the canopy edge.
   - Hand-to-NAIP registration is itself weak (ECC corr 0.2-0.45 in `vision_any/spirit_hollow/validation.md`).
   - The cheapest gain is to calibrate the layer to the hand-map convention (erode the canopy by a
     few yards; native = unmown and not tree) and to score with a 5-yd tolerance. A new architecture
     comes after that.
   - For native grass, the best untried signals are: multi-date NAIP phenology (native grass browns
     out or cures earlier than irrigated rough), lidar 0.3-1.5 m returns, texture, and free
     [Clay v1.5 NAIP embeddings](https://source.coop/clay/clay-v1-5-naip) (CC-BY, precomputed, so no
     inference).
7. **Imagery licences.**
   - **NAIP**, **USGS 3DEP lidar** and **Iowa county/state orthos** are usable for automated
     derivation: public domain or CC BY. Iowa has NAIP 2025 at 30 cm and spring 2023-2025 county
     orthos on [ortho.gis.iastate.edu](https://ortho.gis.iastate.edu/).
   - **Google** satellite tiles are not usable: no tracing or derivation, and no programmatic
     measurement of 3D tiles.
   - **Mapbox** permits tracing for OSM only. Commercial derivation needs a Commercial Satellite licence.
   - **Esri World Imagery** is display and in-ArcGIS editing only. Export is limited. Fine for the
     golfer's review basemap, not for our classifier.

---

## 1. How the apps build and maintain course maps

| App / vendor | How maps are made | Coverage claim | Accuracy claim | Tees per colour | Sources |
|---|---|---|---|---|---|
| **18Birdies** | Team-built. Golfers submit the scorecard and course map, or a shared Google Map with tee and hole pins. Golfers can drag the tee icon and report errors. | 40,000+ | none published | **Set manually; default = farthest-back tee** | [help 588](https://help.18birdies.com/article/588-gps-shows-a-different-set-of-tees-than-what-i-selected), [help 678](https://help.18birdies.com/article/678-how-can-i-show-18birdies-the-map-of-my-home-course), [help 242](https://help.18birdies.com/article/242-my-course-is-wrong) |
| **Golfshot** (ShotZoom; GolfNow family) | "Mapping team" from aerial imagery. Remaps are put on hold when imagery is outdated. Monthly update posts. | 40,000+ ([support](https://shotzoom.zendesk.com/hc/en-us/articles/360017711754-What-courses-are-mapped-in-Golfshot)) | none | Scorecard via scorecard@golfshot.com, update within 14 days | [support](https://shotzoom.zendesk.com/hc/en-us/articles/360000958554-How-do-I-correct-or-add-a-course), [Sep 2026 update](https://golfshot.com/blog/course-update-request-september-2026), [Apr 2022](https://golfshot.com/blog/course-update-report-april-2022) |
| **Arccos** | In-house mapping and user email fixes ("update within a couple of business days"). Crowd-sourced daily pin positions. Microsoft built a U-Net "playable vs non-playable (trees)" segmentation from fewer than 100 labelled satellite images. | 40,000+, "every tee, tree and trouble spot" | "highly accurate" pins (own claim) | not documented | [App Store](https://apps.apple.com/us/app/arccos-golf/id841396631), [crowd pins](https://au.arccosgolf.com/blogs/community/arccos-golf-premiers-crowd-sourced-hole-locations-siri-shortcuts-and-enhanced-putting-ux-for-arccos-caddie-platform), [Microsoft ISE](https://devblogs.microsoft.com/ise/semantic-segmentation-small-data-using-keras-azure-deep-learning-virtual-machine/), [golf.com](https://golf.com/gear/tap-and-shoot-four-apps-that-take-playing-on-your-phone-to-the-next-level/) |
| **Hole19** | Mapping team. In-app "Request Mapping", answered within 48 h. "Depends on … the national golf federation and the quality of the aerial imagery". | 42,000+ | none | via request | [help](https://help.hole19golf.com/hc/en-us/articles/16515391224348-Request-a-New-Course-or-a-Course-Update), [App Store](https://apps.apple.com/nz/app/hole19-golf-shot-gps-tracer/id794462227) |
| **SwingU** (Golf Genius) | Not documented. Green maps licensed from StrackaLine (laser-mapped greens). | 34,000+ | "community-verified" (marketing) | n/a | [swingu.com](https://swingu.com/), [App Store](https://apps.apple.com/us/app/swingu-golf-gps-range-finder/id332116103) |
| **GolfLogix** | "A variety of aerial and satellite imagery". Each map reviewed annually. Licenses its maps to others. | 40,000+ | "0-3 yards" (FAQ) | n/a | [FAQ](https://www.golfgps.com/golfgps/faqs.aspx), [map licensing](https://www.golflogix.com/page/map-licensing-inquiries/), [Critical Golf](https://criticalgolf.com/reviews/archived-products/golflogix-review/) |
| **TheGrint** | Started as member-mapped with a Course Uploader (tee, green F/C/B, fairway point per hole). Now a mapping team "monitoring courses every day". | 37,000-40,000+ | none | the longest tee only, in the 2013 guide | [2013 guide](https://thegrint.com/range/post/how-to-map-a-golf-course-at-thegrint-for-gps-purposes), [features](https://thegrint.com/features) |
| **Shot Scope** | In-house golfers trace satellite imagery: "20 minutes to 2 hours" per course versus about 9 h walking. 48 h updates. | 42,000+ | n/a | Tees added on request. The device snaps to the nearest *mapped* tee (forum). | [blog](https://shotscope.com/blog/inside-the-ropes/expert-insight/golf-course-mapping-how-is-it-done/), [course mapping](https://shotscope.com/us/discover/on-the-course/course-mapping/), [forum](https://forums.golfmonthly.com/threads/shot-scope-accuracy.111368/) |
| **SkyCaddie** (SkyGolf) | Walks courses with survey GPS ("ground-verified"). Argues satellite imagery is not good enough. | 35,000 | "within 1 metre" | walked | [methodology](https://skygolf.com/pages/mapping-methodology), [Golf Monthly](https://www.golfmonthly.com/reviews/gps/skycaddie-pro-5x-gps-review) |
| **Bushnell** | iGolf supplies and maintains the course database. Corrections go to iGolf. | iGolf's | n/a | iGolf tee data | [Bushnell support](https://www.bushnellgolf.com/support/product-gps-ion), [press](https://www.pr.com/press-release/128987) |
| **Garmin** | In-house. Supplier not disclosed; I found no source tying Garmin to iGolf. Users report tee polygons drawn much smaller than the real boxes. | 42,000-43,000 | n/a | n/a | [Garmin](https://www.garmin.com/en-US/garmin-technology/maps-for-smartwatches/golf-courses/), [forum](https://forums.garmin.com/apps-software/mobile-apps-web/f/garmin-golf-ios/441469/tee-shots-location-rough-instead-of-tee-box/2057373) |
| **iGolf / L1 Technologies** (data vendor) | Mapping staff plus its own mapping app, which validates submitted files. Licenses to 60+ brands, including TaylorMade and the USGA. | 40,000+ in 175+ countries; 3D terrain for 20-23k | "most accurate" (own claim) | **Tee names, colours, yardages, slope and rating; tee centre points for up to 5 tees per hole** | [iGolf data](https://igolf.com/solutions/golf-course-data/), [iGolf Connect](https://igolfconnect.com/golf-data), [L1](https://l1technologies.com/igolf), [SDBJ](https://www.sdbj.com/?p=76117) |

What this means for us:

- **Accuracy claims are marketing.** I found no independent controlled test. Users report "about 3 yd"
  front/middle/back agreement with lasers on 18Birdies
  ([MyGolfSpy forum](https://forum.mygolfspy.com/topic/24549-18-birdies-shot-tracking-mini-review/)).
  Sureshot says Google Earth-based maps "can be up to 20-30 yards out"
  ([Golf Business News](https://golfbusinessnews.com/news/corporate/sureshot-unveils-new-gps-measuring-device/)).
  Green F/C/B to about 3 yd is the bar golfers notice.
- **Tee colour is the weakest field industry-wide.** Most apps store one tee point per hole, or a few
  manually placed ones. iGolf stores up to 5 centre points. Golfers fix tees by dragging. We should
  treat tee placement as **"auto-place + one-tap confirm"**, not as something we can guarantee.
- **The human cost they pay** is 20 min to 2 h of tracing per course (Shot Scope). A golfer's
  2-minute review of *only the flagged items* is our equivalent.

## 2. Data sources we could use (details in `auto_course_lookup.json`)

### 2.1 Course and scorecard APIs

| Source | Coverage | Cost / access | Licence | Fields | Fit |
|---|---|---|---|---|---|
| **OpenGolfAPI REST** ([api repo](https://github.com/opengolfapi/api), [docs](https://opengolfapi.org/docs/)) | about 16k US, 32k worldwide | **Free, no key: 1,000/day per IP.** A free key raises the limit. | **ODbL 1.0** (attribute, share-alike) | search (name, state, lat/lon, osm id); `/api/v1/courses/{id}` → `tees[]` (tee_name, tee_color, gender, course_rating, slope, yardage), `holes_data[]` (number, par, handicap_index, yardages{colour}). Geometry (tee coords, green F/C/B, polygons) gated as paid "OpenGolfGeo". | **Use now** as the S1 scorecard fallback and the S0 resolver |
| OpenGolfAPI bulk dump ([data](https://github.com/opengolfapi/data)) | 15,667 US rows | free (GitHub; reachable from our sandbox) | ODbL | id, name, lat/lon, address, osm_id (3,593), par, pars and hcp from OSM (only 22 rows have all 18), total_yardage (568) | Offline resolver and OSM-id join only |
| **GolfCourseAPI** ([site](https://golfcourseapi.com/), [docs](https://api.golfcourseapi.com/docs/api/)) | 30k+ worldwide | Free 35 req/day **with email signup**; Pro $9.99, Enterprise $24.99 | proprietary ToS | tees by gender → per-hole par/yardage/handicap, rating/slope, location lat/lon (v1.1), meters (v1.2) | Good card cross-check. Needs a signup, so not tested here. |
| **GolfAPI.io** ([site](https://golfapi.io/), [Postman](https://documenter.getpostman.com/view/1756312/UVeDsT2b)) | 40k+, 160 countries | key via contact@golfapi.io; price on request; CSV export available | proprietary | clubs, courses, tees (lengths, slope, rating), **coordinates (green, tees, POIs)** | Strongest candidate if we buy tee GPS points |
| **Golfbert** ([site](https://www.golfbert.com/), [node wrapper](https://github.com/dylanjmcdonald/node-golfbert)) | US | key (API, access and secret); pricing unpublished | proprietary | courses, holes, **teeboxes, hole polygons** (green, fairway, hazards), scorecard | Polygons, so it could replace OSM where OSM is empty |
| **Golf Intelligence** ([pricing](https://golfintelligence.com/api-pricing/), [personal-app terms](https://www.golfintelligence.com/personal-golf-app/)) | 40k+ | $49 one-time test credits; $399/mo for 10k credits; $500/yr per facility | **No bulk dump, no model training**, 1-yr on-device cache | polygons: tees, fairways, bunkers, penalty areas, greens, hole outline; scorecards | Data is fine; the licence conflicts with our pipeline |
| **iGolf Connect** ([data](https://igolfconnect.com/golf-data)) | 40k+ | enterprise; per-transaction or unlimited | proprietary | tee names, colours, yardages, rating/slope; **tee centre points ×5 per hole**, green F/C/B, 4 hazard points; full perimeter maps; 3D terrain | The industry answer to "tees per colour" |
| **USGA NCRDB** ([example](https://ncrdb.usga.org/courseTeeInfo?CourseID=7817)) | all rated US courses | free web; **403 to scripts** (our `tees_fetch` run); terms not located | USGA | per tee: name, gender, par, Course Rating, Bogey Rating, Slope, F9/B9 ratings, **total length** | Authority on which sets exist and their totals. Use manually or via a golfer paste. |
| **GHIN API** ([unofficial wrapper](https://github.com/boorad/ghin), [GHIN ToS](https://www.usga.org/content/usga/home-page/Handicap-ghin/ghin-terms-of-service.html)) | US | USGA Golfer Product Access programme approval | USGA agreement | ratings, slope, course details | Only as a licensed partner |
| OSM `golf=*` ([tee wiki](https://wiki.openstreetmap.org/wiki/Tag:golf=tee)) | varies | free | ODbL | `golf=tee` areas; colour as `tee=<colour>` (rarely used); `golf=hole` with ref, par, dist | Already in S1. Tee colours absent at our 3 courses (§6). |
| Club websites, Golfify, Stymie, GolfNow (scraped) | per course | scraped | facts only, site ToS | cards | Already used. Keep the club site as the authority. |

### 2.2 Imagery, elevation, derived layers

| Source | Resolution / date | Licence | Notes |
|---|---|---|---|
| **NAIP** ([Planetary Computer](https://planetarycomputer.microsoft.com/dataset/naip), [AWS](https://registry.opendata.aws/naip/)) | 0.3-0.6 m RGBN; PC holds 2010-2023 (we use IA 2023 at 0.3 m) | public domain | Leaf-on, summer. The Iowa server lists NAIP **2025 at 30 cm** ([ISU](https://ortho.gis.iastate.edu/)). |
| **Iowa county spring orthos 2023-2025** ([ISU map server](https://ortho.gis.iastate.edu/), [Iowa Geodata](https://geodata.iowa.gov/pages/imagery)) | "high resolution" (often 3-6 in; e.g. Scott Co. 2024 at 3 in, [doc](https://www3.scottcountyiowa.gov/board/pub/enclosures/2024/20240130_Committee_of_the_Whole_830AM/08_IT_Orthophotos.pdf)); spring, near leaf-off | public (state/county) | Tee pads, bunker edges, mowing lines. WMS. A second date helps native-grass phenology. |
| **USGS 3DEP lidar** ([QL spec](https://www.usgs.gov/core-science-systems/ngp/ss/lidar-base-specification-collection-requirements), [E. Iowa 2019 validation](https://pubs.usgs.gov/publication/ofr20251017)) | QL2 ≥ 2 pts/m²; flat-area RMSEz < 0.10 m in E. Iowa | public domain | Already used for trees (HAG). **Untapped: tee-pad detection** (levelled raised platforms) and green/bunker relief. |
| **Meta/WRI canopy height v2** ([AWS](https://registry.opendata.aws/dataforgood-fb-forestsv2), [GEE](https://gee-community-catalog.org/projects/meta_trees/)) | 1 m | CC BY 4.0 | Already the lidar-gap fill |
| **Clay v1.5 NAIP embeddings** ([Source Cooperative](https://source.coop/clay/clay-v1-5-naip)) | 256×256 NAIP chips → 1024-d vector | CC-BY | Use the corrected `clay-v1-5-naip-2`. Chip-level only (about 77 m at 0.3 m), so coarse. Good for "is this patch native grass or rough" priors. |
| Esri World Imagery ([item](https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9), [export](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/imagery/wayback-export)) | 0.3 m-class, recent | Esri MLA: display; editing in ArcGIS apps; export ≤ 150k tiles in ArcGIS | Review basemap for the golfer only. OSM tracing allowed ([OSM wiki](https://wiki.openstreetmap.org/wiki/Esri)). |
| Google Map Tiles / 3D tiles ([FAQ](https://mapsplatform.google.com/resources/blog/commonly-asked-questions-about-our-recently-launched-photorealistic-3d-tiles/), [Cesium terms](https://cesium.com/legal/terms-for-google/)) | best available | **No tracing or derivation; no programmatic measurement** | Do not use in the pipeline |
| Mapbox Satellite ([docs](https://docs.mapbox.com/data/tilesets/guides/imagery/)) | mixed | tracing for OSM only; commercial derivation needs a Commercial Satellite licence | Not for us |

## 3. Literature, datasets, open-source projects, models

### 3.1 Golf-specific work

- **Danish Golf Courses Orthophotos.** Aalborg University: 1,123 + 108 RGB orthophotos from 107
  courses, labelled green, fairway, tee, bunker, water and background. Trees were explicitly
  omitted. U-Net reaches mIoU 69.6%. A follow-up "CRAUNet" reports mIoU 94.8%, an abstract-only claim.
  ([AAU portal](https://vbn.aau.dk/en/publications/semantic-segmentation-of-golf-courses-for-course-rating-assistanc/),
  [ResearchGate](https://www.researchgate.net/publication/373475773_Semantic_Segmentation_of_Golf_Courses_for_Course_Rating_Assistance),
  [Kaggle](https://www.kaggle.com/datasets/jacotaco/danish-golf-courses-orthophotos),
  [Dataset Ninja: ODbL](https://datasetninja.com/danish-golf-courses-orthophotos)). Its purpose,
  distances for course rating, is close to ours, but it is RGB, Danish, and spring imagery.
- **ariadgolf/golf-course-segmentation.** NAIP RGBN 0.6 m, 512 px tiles, 790 US courses, OSM labels,
  course-level holdouts (AZ, CO, GA, **IA**, OR). Per-class pixel IoU: green 0.693, tee 0.331,
  fairway 0.636, bunker 0.563, water 0.034. Weights are FP16 safetensors in `segmentation_models_pytorch` format.
  ([HF card](https://huggingface.co/ariadgolf/golf-course-segmentation)). Iowa was held out in
  training, so our courses are honest test data. **Check the licence of the weights** (the labels are ODbL).
- **opengolf-ai/osm-course-mapper** ([GitHub](https://github.com/opengolf-ai/osm-course-mapper)).
  This is the closest open design to what we want. Pipeline: OpenGolfAPI card → user-confirmed
  playing line → NAIP corridor → SAM 2 (`sam2-hiera-large`, on a GPU at Modal) enumerates masks →
  rule-based classifier. Its README states the rules:
  - spectra first: sand bright, water NIR-dark, turf NIR-bright;
  - then position along the line: green at the end, tees at the start;
  - tees are matched by **card yardage back from the green**, and a reversed line is refused;
  - a human confirms each feature.

  Its stated weak classes are fairway and anything that is the same grass. Nothing it produces counts as
  settled until a human says yes.
- **FairwayMapper** ([site](https://www.fairwaymapper.com/), [wiki](https://wiki.openstreetmap.org/wiki/FairwayMapper),
  [forum](https://community.openstreetmap.org/t/fairwaymapper-introducing-golfers-to-mapping/142814)).
  A golfer-friendly OSM editor (v1.0, July 2026). Every course a golfer maps with it improves our
  OSM input for free.
- **Other OSM-based projects.**
  - [hacker-yardage](https://github.com/npilk/hacker-yardage): OSM → yardage books.
  - [golfTiles](https://github.com/HuggeK/golfTiles): OSM golf vector tiles.
  - [golfcaddy PR](https://github.com/spobo1/golfcaddy/pull/1): assigns colours to OSM tee boxes by
    *yardage differences* between sets, longest set to the rearmost box.
  - [woods PR](https://github.com/zeinbenjamin/woods/pull/15): places the tee at card distance along
    the hole line and flags holes where card and line differ by more than 10%.
- **Roboflow Universe sets.**
  - [danish-golf](https://universe.roboflow.com/sportedge/danish-golf): 2,695 images, CC BY 4.0, classes green, water, bunker.
  - [golf-e0biu](https://universe.roboflow.com/a-lzzgm/golf-e0biu): adds fairway and teebox.

  These are small and of unclear provenance. Use them only for augmentation.
- **Arccos + Microsoft.** A U-Net classifying playable vs non-playable (trees) from fewer than 100
  labelled course images, with pre-labelling to bootstrap
  ([ISE blog](https://devblogs.microsoft.com/ise/semantic-segmentation-small-data-using-keras-azure-deep-learning-virtual-machine/)).
  This is evidence that a tiny labelled set plus a U-Net is how industry approached trees.
- **DeepGolf** (IJAEOG 2025) and Sentinel-2 golf CNNs detect *whole courses*, not features inside a
  course. They are not useful to us
  ([DOAJ](https://doaj.org/article/a15a73c830a843d5b82cf7bee33be2a7),
  [IOP](https://iopscience.iop.org/article/10.1088/1755-1315/1633/1/012002)).

### 3.2 General models

- **SAM / SAM 2 via segment-geospatial** ([samgeo](https://samgeo.gishub.org/),
  [text prompts](https://samgeo.gishub.org/examples/sam2_text_prompts/)). SAM is class-agnostic and
  gives good edges. LangSAM (GroundingDINO + SAM) adds text prompts such as "sand bunker" and "pond".
  On a CPU the automatic generator is decoder-bound: a 32×32 point grid means 1,024 decoder passes,
  about 0.9 s on a V100 ([TinySAM](https://arxiv.org/pdf/2312.13789)). That is minutes per 1024 px
  tile on a CPU. We already ran SAM ViT-B on Actions (`sam_masks.yml`, 5 shards, 90 min budget).
  Best use: **refine edges of classes we already detect** (prompt with a box or point from OSM or
  the U-Net). Do not run it everywhere.
- **Mask2Former / SegFormer.** Strong on large multispectral benchmarks
  ([IGARSS 2025](https://citius.gal/static/8c5081f4e5b61a72dbfb82f3f2817f6c/igarss2025_mask2former_postprint_2025120212284780_e275c03c16.pdf)),
  but they need thousands of labels. We have 3 courses. Not worth it before the U-Net baseline.
- **Foundation models.**
  - Clay v1.5 has a NAIP-native, precomputed embeddings archive, so fine-tuning reduces to fitting a
    linear probe ([docs](https://clay-foundation.github.io/model/finetune/finetune-on-embeddings.html)).
  - Prithvi was trained on HLS at 30 m. That is wrong resolution for features inside a course.
  - SatlasPretrain has NAIP-resolution Swin backbones (not re-verified in this spike). It is heavier;
    use it only if Clay probes are not enough.
  - A broad usability evaluation of 89 geospatial foundation models is at
    [arXiv 2608.03804](https://arxiv.org/pdf/2608.03804).
- **Native vs mown grass.** I found no golf-specific study. The building blocks:
  - texture is sensitive to mowing ([WorldView-3 biomass](https://www.researchgate.net/publication/312299523_Estimating_Biomass_of_Native_Grass_Grown_under_Complex_Management_Treatments_Using_WorldView-3_Spectral_Derivatives));
  - seasonal NDVI separates grass types ([PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0181665));
  - turf + rough co-occurrence "texture motif" works for golf detection ([Springer](https://link.springer.com/chapter/10.1007/978-3-319-71589-6_48)).

  So the feature set is NIR/NDVI at two or more dates, a GLCM texture or local variance window, lidar
  vegetation 0.3-1.5 m, and "distance from mown fairway".

### 3.3 What runs on GitHub Actions CPU in under 1 hour per course

Assumptions: a course is about 2 × 2 km, which at 0.6 m is about 3,300² px, or about 50 tiles of
512 px. At 0.3 m that is ×4. Actions runners have 4 vCPU and 16 GB. The timings are my estimates
from model size, not measurements. The first workflow run of each model should log them.

| Model | Params | Est. CPU time per course | Fits < 1 h? | What it adds |
|---|---|---|---|---|
| ariadgolf U-Net R34 (NAIP 0.6 m) | ~24 M | ~1-3 min (50 tiles × ~2 s) | yes | green, tee, fairway, bunker polygons where OSM is missing; tee candidates |
| Same, with 8-way TTA, or at 0.3 m upsampled | | ~10-20 min | yes | smoother edges |
| Linear/LightGBM probe on Clay NAIP embeddings | n/a | seconds (download parquet rows for the bbox) | yes | chip-level native/rough/tree priors |
| Per-course self-supervised pixel classifier (current `vision_any`, sklearn) | | ~1-10 min if precomputed. On-the-fly took 13 min and 3.4 GB in the sandbox. | yes (on Actions) | trees, native, water |
| SAM ViT-B / SAM2-tiny, *prompted* by boxes along hole corridors (about 200 prompts) | 40-90 M | ~5-15 min | yes | crisp edges for bunkers, water, tee pads |
| SAM automatic grid over the whole course at 0.3 m | | hours | no (shard it, or skip) | |
| LangSAM (GroundingDINO-T + SAM) | ~170 M + SAM | ~30-60 s per tile → ~1 h+ | marginal | text-prompted hazards |
| Mask2Former / SegFormer-B2 fine-tune | 25-100 M | training: GPU only | no (inference only) | |

## 4. Automatic tee-box assignment

### 4.1 How the yardage is defined

The USGA measures "horizontally … from the permanent yardage marker for every teeing area … to the
center of the green". On doglegs it measures through pivot points on the line of play
([USGA Handicap Manual §12](https://www.usga.org/custom-search-pages/rules/handicap-manual/rule-14393.html)).
An error of 22 yd over a whole course moves the men's Course Rating by 0.1. Two consequences:

- **The card is a strong geometric constraint.** `place_tee.py` already implements it: the distance
  from the box's middle along the line of play, through the next turning point.
- **Our errors come from three things:**
  - missing candidates: OSM has no box for new back tees (SH 2 at 607, 15 at 215);
  - stale cards: aggregators carry the 7,021-, 7,268- and 7,301-yd Spirit Hollow cards;
  - the reference: the app shows back tees by default.

### 4.2 Methods, ranked by value for our pipeline

1. **Ordered joint assignment per hole.** Rather than choosing each set independently, solve one DP
   per hole:
   - Order the card sets back → front (Gold ≥ Black ≥ White ≥ Rust by yards).
   - Order the candidate boxes by along-line distance to the green.
   - Each set picks a box (sharing allowed) so that the order of sets matches the order of boxes.
   - Cost = Σ max(0, |d(set) − card(set)| − half the box extent) + λ·(walk-back penalty).

   The "difference" trick from the golfcaddy PR falls out of this: the gaps between sets are matched
   even if the green centre is off by 5 yd. It is cheap and deterministic. It fixes cases where two
   sets currently grab the same box when they should not, and the reverse.
2. **Better candidates.**
   - (a) Union of OSM `golf=tee` and imagery-detected tees from the ariadgolf `tee` class (IoU 0.33,
     but recall of the *object* is higher than pixel IoU).
   - (b) A **lidar flat-pad detector** on the 3DEP DTM: tee pads are levelled, slightly raised
     rectangles or ellipses. Keep cells where |slope| < 2%, a local relief step of 0.2-1.5 m to the
     surroundings, and area 80-1,500 m². Keep components near the first leg extended backwards. All
     public-domain data we already fetch; CPU in seconds.
   - (c) The OSM `golf=hole` start node. Many lines are drawn from the back tee of an older card.
3. **Card version handling.**
   - Choose the card by **provenance and recency**: club site > OpenGolfAPI / Golfify > other
     aggregators.
   - Run a **consistency check** on every card: per-hole sum vs stated total.
   - Use the geometry fit only to find **holes where the chosen card has no mapped box**.

   The prototype (§6.3) shows the OSM boxes at Spirit Hollow fit the *old* 7,021-yd card best, so
   "pick the card that fits the map" would choose the wrong card. A card hole with no box within
   25 yd triggers the extra tee detectors and a golfer check.
4. **Green centre.** Use the OSM or U-Net green polygon centroid, not the hole-line end. The QA green
   error is 6 yd median, with outliers to 40-200 yd that are registration failures. This is what makes
   tee-from-card stable.
5. **Tee markers in imagery.** Coloured markers are about 20-30 cm, under one NAIP pixel. They can
   only be seen in 3-6 in county orthos, and even then unreliably, and markers move daily. Not worth it.
6. **OSM `tee=<colour>` tags.** These are correct when present, but almost never present (§6). Read
   them, and use them as "tagged" evidence with confidence 0.95.

### 4.3 Validation

- **Internal.** The residual |measured − card| per hole and set: under 5 yd green, 5-15 yd amber,
  over 15 yd red. Also the sum over holes vs the card total and vs the NCRDB length, if the golfer
  pastes it.
- **Reference fix (Q1).** Label every traced hole with the card set nearest the app's yardage
  (`tees/README.md` already does this by hand). Score tee placement only against the same set.
- **Ground truth that scales.**
  - (a) The golfer's on-course GPS fix when they mark "I'm on the tee". Even 5-10 m phone GPS beats
    a 30-100 yd error.
  - (b) The golfer drags the tee on the review map before the round. 18Birdies does exactly this.
  - (c) Shot-tracking data, if the golfer uses Arccos or 18Birdies exports.
- **Leave-one-course-out** across Spirit Hollow, Mozingo and Veenker. Report the share of holes
  within 10 yd per set.

## 5. Ranked plan

Effort is in engineer-days. Accuracy gains are my estimates for Spirit Hollow and the next 5 courses.
QA should confirm each one with `acceptance.py` / `qa/golden_spirit_hollow.py` before and after.

### Quick wins (this week)

| # | Item | Owner | Effort | Expected gain | Cost |
|---|---|---|---|---|---|
| Q1 | **Fix the tee reference.** Tag each traced hole with its app set. Score tees per set. Report "same club" both ways. | qa + architect | 0.5 d | Tee within 10 yd: 25-50% → about 70% on the *measured* metric. Removes a false blocker. | 0 |
| Q2 | **Ordered joint tee assignment + green centroid + card-version selection** (§4.2 1, 3, 4) | tees | 1-2 d | Length within 5 yd: 12% → about 50-60% (Black). Card versions chosen automatically. | 0, CPU seconds |
| Q3 | **Lidar flat-pad tee candidates** for holes whose card box is missing in OSM (SH 2, 15, 17) | tees + vision_any | 1 d | Fixes the 20-100 yd misses on new back tees. That is 3/18 holes at SH; likely 10-20% of holes elsewhere. | 0 (3DEP DTM already fetched) |
| Q4 | **OpenGolfAPI as S1 scorecard source and S0 resolver.** Read `/api/v1/courses/{id}`. Prefer the club site when both exist. Use the bulk dump for name→OSM id offline. | platform | 0.5-1 d | Mozingo gets real tee sets (today only "App" yardages). Any US course gets a card with no scraping. | 0; ODbL attribution |
| Q5 | **Tree-line convention.** Erode the lidar canopy mask by k yd (fit k on SH LOHO). Treat 1-2 rows of trees as `recovery`, deep woods as `ob`-like. Score with a 5-yd tolerance. | vision_any | 0.5-1 d | Trees IoU 0.23 → about 0.35-0.45 (precision at 5 yd is already 0.48) | 0 |
| Q6 | **Verification UX v1** (§8): per-hole "check these" list in the book plus a review page with the imagery, the tee per set and the hazards to confirm | product | 1-2 d | Golfer-visible errors drop because the worst holes are flagged; the golfer fixes them | 0 |

### Bigger bets (2-6 weeks)

| # | Item | Effort | Expected gain | Cost / risk |
|---|---|---|---|---|
| B1 | **Run the ariadgolf U-Net on NAIP in `vision_any.yml`** (CPU, about 3 min/course). Merge fairway, bunker, green and tee where OSM is empty. Use tee masks as S2 candidates. Optionally fine-tune on our 3 hand maps plus OSM (GPU-free head-only training is feasible). | 3-5 d | Fairway IoU 0.58 → about 0.65. OSM-sparse courses become usable. Tee candidates on about 30-60% of missing boxes. | Weights licence unverified; 0.6 m model on 0.3 m data needs resampling |
| B2 | **Native-grass model v2.** Features: multi-date NAIP (2019, 2021, 2023, 2025) NDVI phenology, texture, lidar 0.3-1.5 m return share, Clay embedding prior, distance from mown turf. Self-supervised seeds from OSM rough/fairway vs `natural=scrub/grassland`. LightGBM. | 1-2 wk | Native IoU 0.09 → about 0.3-0.4. This is the largest single driver of club disagreement on open holes (4, 9, 14, 16). | CPU fine; needs a second NAIP date fetch |
| B3 | **Golfer-in-the-loop corrections** stored per course: tee drag, "this is OB", "this is native". Reuse on re-runs; optionally upload to OSM via FairwayMapper-style flows with explicit consent. | 1-2 wk | The only path to above 90% on tees and OB. Matches what every app does. | Product work; artifact db or repo files |
| B4 | **OB inference.** Course boundary with all rings (P1 fix) ∪ county parcels ∪ OSM `landuse=residential`, roads and fences, as candidate OB. The golfer confirms. | 1 wk | OB IoU 0.2 → about 0.5 | Parcel data licences vary by county |
| B5 | **High-res state orthos** (Iowa spring 2023-25, then other states' programmes) for tee pads, bunker lips and mowing lines. Also SAM-prompted edge refinement. | 1 wk | Edges ±1 yd instead of ±2-3. Helps tee boxes and carries. | WMS throttling; per-state work |
| B6 | **Licensed tee points** (GolfAPI.io / iGolf / Golfbert) if this becomes commercial. Use them as a cross-check, not a replacement. | days + contract | Tee per colour largely solved | $ unknown. Redistribution and ML-use limits (Golf Intelligence forbids both). |

**What gets us to 80% same-club?** Club disagreements at Spirit Hollow fall into three groups:

- trees/native in the 220-340 band: holes 5, 10, 14, 16, 18;
- tee length: 1, 9B, 13, 17;
- the dog-leg line.

Q1+Q2+Q3 address the tee group. Q5+B2 address the hazard group. Rough expectation: Q-items take us
from 56% to about 65-70%, and B1+B2 to about 75-80%. The last few points come from B3, where the
golfer confirms 2-4 flagged items per round. Every number here needs confirming by QA.

## 6. Prototype: free sources tested now

`course_data/research/open_sources.py` has three modes. `fetch` runs on Actions via
`research_fetch.yml`: OpenGolfAPI search, detail, tees and holes for our three courses, OSM taginfo
tee-tag statistics, and Overpass tee tagging per course bbox plus IA/MO statewide counts. `compare`
runs offline and writes `probe.json`. `dump` is the offline resolver test on the ODbL bulk dump.

Run: Actions [38979696509](https://github.com/willbhedges/my_golf_data_science/actions/runs/38979696509),
2026-10-16 23:08 UTC. Raw responses are in `course_data/research/raw/`. Everything below was
anonymous, with about 25 calls in total.

**6.1 OpenGolfAPI vs our hand-checked cards**

| course | resolved? | sets returned | per-hole match vs ours (MAE, holes within 3 yd) | par / stroke index agree |
|---|---|---|---|---|
| Veenker (IA) | yes, 1 candidate | blue (M), gold (M/F), red (M/F), with rating and slope | Blue 2.6 yd, 16/18; Gold 3.1, 16/18; Red 0.9, 17/18. Diffs: Blue 8 (181 vs 174) and 10 (560 vs 520); Gold 2, 6; Red 2. | 18/18 / 18/18 |
| Spirit Hollow (IA) | yes, 1 candidate | gold, black, white (M/F), red, with rating and slope | Rust 0.8 yd, 17/18; Black 5.6, 13/18; White 11.0, 11/18; **Gold 17.3, 8/18** | 18/18 / **6/18** (older index) |
| Mozingo Lake (MO) | **only "Watson 9 Course"**; the main 18 is missing | 9-hole sets | n/a | n/a |

Findings:

- **The free API is good enough to be the default card where no club card exists.** Veenker matches
  our Golfify card to about 1-3 yd on 16-17 of 18 holes.
- **It is internally inconsistent where cards changed.** At Spirit Hollow, the tee *totals* are the
  current card (7550 / 6580 / 6010 / 5053), but the per-hole yardages sum to 7268 / 6659 / 5844 / 5068.
  The per-hole Gold numbers are the stale 7,268 card, and the stroke index is the old one.
  - **Check:** |sum(per-hole) − tee total| > 15 yd → mark the card "mixed versions". Prefer the club
    page. Lower the tee confidence.
  - The same check would have caught Veenker Blue: per-hole sum 6633 vs total 6680.
- **Coverage gaps are real.** Mozingo's main 18 is absent, so S1 needs at least two sources plus
  "paste your scorecard" as the final fallback.
- **The geometry fields exist in the schema but are null:** `tee_coords`, `green.front/center/back`,
  `green_polygon`, `fairway_polygon`, `hazards`, `dogleg` and `plays_like_yards`. The API source says
  these are gated "until accuracy is validated vs GolfViz + paid-tier metering". OpenGolfAPI is not a
  geometry source today.

**6.2 Tee colours in OSM** (taginfo, global, and Overpass)

- Globally, 697,117 `golf=tee` features carry 9,881 `tee=*` tags (**1.4%**). Top values: red 10,010,
  white 8,918, blue 7,058, yellow 5,052, black 3,651, gold 2,598. Combined values such as `blue;white`
  also occur.
- **Iowa:** 6,985 `golf=tee` and 175 with `tee=*` (**2.5%**), 2,651 `golf=hole`, 9 holes with `dist*`,
  and 397 courses.
- **Our courses:** Spirit Hollow has 103 tees, 0 with a colour. Mozingo has 84 tees, 0 with a colour
  and 12 with `ref`. Veenker and the Missouri statewide count hit Overpass "at capacity" or timeouts;
  re-run.
- **Conclusion:** tee colour must come from geometry plus the card. OSM tags only confirm.

**6.3 Which card does the OSM tee geometry represent?** (`open_sources.py cardfit`, Spirit Hollow)

For each card, the gap between each hole's card yardage and the nearest OSM tee box (centroid
along-line distance, `tee_options`):

| card | total | median gap | holes ≤ 10 yd | holes > 25 yd |
|---|---|---|---|---|
| **GolfLink Gold (old)** | 7021 | **6.5** | **16/18** | 0 |
| Stymie Gold (old) | 7301 | 7.0 | 14 | 1 |
| OpenGolfAPI per-hole Gold (old) | 7268 | 7.5 | 12 | 1 |
| club Black (current) | 6589 | 7.5 | 13 | 0 |
| club White (current) | 6040 | 9.0 | 14 | 1 |
| club Gold (current) | 7550 | 8.5 | 10 | 2 |
| club Rust (current) | 5053 | 10.5 | 9 | 4 |

The OSM boxes fit the *old* 7,021 Gold card better than the current one. The mapper traced the
course before the new back tees on 2 and 15 were built, which confirms `tees/README.md`. Two
consequences:

- **Geometry fit cannot pick the current card.** It tells you *which holes of the current card have
  no mapped box*: the gap is over 25 yd on Gold 2 and 15, and on 4 Rust holes. Those are exactly the
  holes to send to the lidar or U-Net tee detector (Q3) and to flag to the golfer.
- **Forward tees (Rust) are the least mapped.** Women and juniors on forward tees will see the most
  "walk-back" placements.

**6.4 Bulk dump as resolver** (`open_sources.py dump`, sandbox)

- 15,667 US rows; 3,593 with `osm_id`.
- All three courses resolve by name and state. Spirit Hollow and Veenker carry the same OSM ids our
  pipeline uses (13353211, 44804299).
- Only 22 rows have all 18 pars, so the dump is not a scorecard source.

**Not tested** (signup or key required, per the constraints): GolfCourseAPI (free tier, needs an
email), GolfAPI.io, Golfbert, iGolf, Golf Intelligence. NCRDB still blocks scripts.

## 7. Design: "type course + tees → verified package in under 15 min"

```
golfer: "Veenker, Ames IA" + "Blue"
  │
  ▼  S0 RESOLVE (≤ 5 s, offline-capable)
  │    OpenGolfAPI dump (ODbL, cached in repo) + OSM course index → candidates (name, town, osm id, holes).
  │    One confident match → continue. Otherwise ask "Which one?" (show 2-3 with town + hole count).
  │
  ▼  S1 FETCH (Actions, ~2-4 min, parallel jobs; cached per course for 90 days)
  │    a. OSM Overpass (golf + landcover + roads), all boundary rings           ~1-2 min
  │    b. Cards: club site (if known) ‖ OpenGolfAPI /api/v1 ‖ Golfify            ~10-30 s
  │       → card-version selection happens after S2 geometry is known
  │    c. NAIP latest (PC STAC; 2025 from USDA/AWS when PC lacks it) + 3DEP DTM/HAG + Meta CHM   ~1-2 min
  │
  ▼  S2 TEES (local, seconds)
  │    candidates = OSM tees ∪ lidar flat pads ∪ U-Net tees ∪ hole-line start
  │    ordered joint assignment per hole for ALL card sets; card-version fit; residuals → confidence
  │
  ▼  S3/S4 HOLES + VISION (Actions, ~3-6 min)
  │    U-Net (fairway/green/bunker/tee) ~3 min; trees (HAG, eroded) ~1 min; native v2 ~2 min;
  │    water (OSM ∪ NIR) ; OB candidates (boundary ∪ parcels ∪ roads)
  │
  ▼  S6 MERGE + CONFIDENCE (local, ~10 s) → package.json with per-hole, per-field confidence and "checks"
  │
  ▼  S7 BOOK (~4 min today; plan.py) + REVIEW PAGE (artifact)
       Book prints at once with "DRAFT - check flagged holes" when any red check is open.
       The golfer confirms on the review page (2 min) → only the affected holes re-plan (~30 s each).
```

Budget: about 1 min queue + 4 min fetch + 6 min vision + 4 min book ≈ **12-15 min cold**, and
**under 5 min warm** (cached S1/S4). Key changes from today:

- **Precompute and cache** the per-course rasters and vision layers on Actions. Today the on-the-fly
  `gapfill_holes` took 13 min and 3.4 GB in the sandbox.
- **Run jobs in parallel**: OSM ‖ imagery ‖ cards.
- **Trigger from a request file**: `requests/package_<slug>.json`, as now.
- **Re-plan only the holes the golfer changed.**

## 8. Confidence and verification UX

Per hole and per field (tee for the chosen set, green, each hazard class in the 200-340 band, OB), compute a
confidence from evidence agreement, not a single score. Show the golfer **only what changes the
decision**:

| Field | Green (auto) | Amber ("glance") | Red ("please check") |
|---|---|---|---|
| Tee for your set | OSM `tee=colour` tag, or card within 5 yd of a mapped box, ordered consistently with the other sets | card within 5-15 yd; box from lidar or U-Net only | > 15 yd, walk-back, or two sets forced onto one box |
| Green | OSM polygon, and U-Net agrees (IoU > 0.6) | one source only | none / line end only |
| Trees / native in landing band | lidar and imagery agree; or the hazard is > 25 yd from both the aim and the 1-sigma dispersion ellipse | one source | the **best club changes** if this hazard is removed or added (sensitivity test) |
| Water / OB | OSM polygon / boundary | inferred (NIR, parcels) | inferred *and* decision-relevant |
| Card | club site and geometry fit < 5 yd median | aggregator only | two cards disagree > 10 yd on this hole |

The **decision-sensitivity test** is the key trick and is cheap. Re-run `tee_strategy` with each
uncertain zone removed or added, and with the tee moved ±15 yd. If the recommended club or aim
changes, the item is red; otherwise it stays amber even when the data is weak. This is how we show
golfers 2-4 checks per round instead of 40.

What the golfer sees:

1. **Review page (artifact).** One card per flagged hole: NAIP or Esri basemap, our tee for their set
   (draggable), the hazard outline in question, and the question in golf terms: "Is the left side
   at 250 trees or open rough?" "Is this where the Blue tee plays from? (card 415, we measure 402)".
   Answers are stored as corrections (B3), and only that hole re-plans.
2. **In the book.** Each hole page gets a small badge: ✓ auto / ◐ checked by you / ⚠ unverified (the
   two things to look at on the tee). The cover lists unverified holes. The aim sheet repeats the
   ⚠ line: "Tee may be 15 yds forward: if the marker is past the cart path, club down."
3. **On course (later).** A one-tap "I'm on the tee" that snaps the tee to the phone GPS fix and
   re-reads the plan for that hole. This is 18Birdies' drag-the-tee, made automatic.

## 9. Licence and attribution checklist

- **OSM** and **OpenGolfAPI**: ODbL 1.0. Credit "© OpenStreetMap contributors" and "Contains data
  from OpenGolfAPI (opengolfapi.org)". A *derivative database* we publish must stay ODbL. The
  rendered PDF book is a "produced work": attribution is enough.
- **NAIP**, **3DEP** and **USGS**: public domain. Meta CHM v2 and Clay embeddings: CC BY 4.0 (credit).
- **Danish dataset**: ODbL (Dataset Ninja) or "other" (Kaggle mirror). Check before training.
  ariadgolf weights: **unverified**.
- Do **not** feed Google, Mapbox or Esri tiles into classifiers. Esri is display-only for the review page.
- Scraped aggregator cards: facts only, low volume, honour 403s (as `tees/fetch_scorecards.py` does).
- NCRDB and GHIN: no automated access without USGA agreement.

## 10. Sources

Apps and vendors:
[18Birdies tees](https://help.18birdies.com/article/588-gps-shows-a-different-set-of-tees-than-what-i-selected) ·
[18Birdies map](https://help.18birdies.com/article/678-how-can-i-show-18birdies-the-map-of-my-home-course) ·
[18Birdies wrong course](https://help.18birdies.com/article/242-my-course-is-wrong) ·
[Golfshot support](https://shotzoom.zendesk.com/hc/en-us/articles/360000958554-How-do-I-correct-or-add-a-course) ·
[Golfshot courses](https://shotzoom.zendesk.com/hc/en-us/articles/360017711754-What-courses-are-mapped-in-Golfshot) ·
[Golfshot Sep 2026](https://golfshot.com/blog/course-update-request-september-2026) ·
[Golfshot Apr 2022](https://golfshot.com/blog/course-update-report-april-2022) ·
[Arccos App Store](https://apps.apple.com/us/app/arccos-golf/id841396631) ·
[Arccos crowd pins](https://au.arccosgolf.com/blogs/community/arccos-golf-premiers-crowd-sourced-hole-locations-siri-shortcuts-and-enhanced-putting-ux-for-arccos-caddie-platform) ·
[Microsoft/Arccos U-Net](https://devblogs.microsoft.com/ise/semantic-segmentation-small-data-using-keras-azure-deep-learning-virtual-machine/) ·
[golf.com apps](https://golf.com/gear/tap-and-shoot-four-apps-that-take-playing-on-your-phone-to-the-next-level/) ·
[Hole19 request](https://help.hole19golf.com/hc/en-us/articles/16515391224348-Request-a-New-Course-or-a-Course-Update) ·
[Hole19 App Store](https://apps.apple.com/nz/app/hole19-golf-shot-gps-tracer/id794462227) ·
[SwingU](https://swingu.com/) ·
[GolfLogix FAQ](https://www.golfgps.com/golfgps/faqs.aspx) ·
[GolfLogix licensing](https://www.golflogix.com/page/map-licensing-inquiries/) ·
[Critical Golf GolfLogix](https://criticalgolf.com/reviews/archived-products/golflogix-review/) ·
[TheGrint mapping guide](https://thegrint.com/range/post/how-to-map-a-golf-course-at-thegrint-for-gps-purposes) ·
[Shot Scope blog](https://shotscope.com/blog/inside-the-ropes/expert-insight/golf-course-mapping-how-is-it-done/) ·
[Shot Scope mapping](https://shotscope.com/us/discover/on-the-course/course-mapping/) ·
[SkyGolf methodology](https://skygolf.com/pages/mapping-methodology) ·
[Bushnell support](https://www.bushnellgolf.com/support/product-gps-ion) ·
[iGolf-Bushnell press](https://www.pr.com/press-release/128987) ·
[Garmin courses](https://www.garmin.com/en-US/garmin-technology/maps-for-smartwatches/golf-courses/) ·
[Garmin forum tee polygons](https://forums.garmin.com/apps-software/mobile-apps-web/f/garmin-golf-ios/441469/tee-shots-location-rough-instead-of-tee-box/2057373) ·
[iGolf data](https://igolf.com/solutions/golf-course-data/) ·
[iGolf Connect](https://igolfconnect.com/golf-data) ·
[L1 iGolf](https://l1technologies.com/igolf) ·
[MyGolfSpy forum](https://forum.mygolfspy.com/topic/24549-18-birdies-shot-tracking-mini-review/) ·
[Sureshot](https://golfbusinessnews.com/news/corporate/sureshot-unveils-new-gps-measuring-device/)

Data APIs:
[OpenGolfAPI api](https://github.com/opengolfapi/api) ·
[OpenGolfAPI data](https://github.com/opengolfapi/data) ·
[OpenGolfAPI docs](https://opengolfapi.org/docs/) ·
[GolfCourseAPI](https://golfcourseapi.com/) ·
[GolfCourseAPI docs](https://api.golfcourseapi.com/docs/api/) ·
[GolfAPI.io](https://golfapi.io/) ·
[GolfAPI Postman](https://documenter.getpostman.com/view/1756312/UVeDsT2b) ·
[Golfbert](https://www.golfbert.com/) ·
[node-golfbert](https://github.com/dylanjmcdonald/node-golfbert) ·
[Golf Intelligence pricing](https://golfintelligence.com/api-pricing/) ·
[Golf Intelligence personal terms](https://www.golfintelligence.com/personal-golf-app/) ·
[NCRDB example](https://ncrdb.usga.org/courseTeeInfo?CourseID=7817) ·
[USGA measurements §12](https://www.usga.org/custom-search-pages/rules/handicap-manual/rule-14393.html) ·
[USGA rating §13](https://www.usga.org/custom-search-pages/rules/handicap-manual/rule-14395.html) ·
[GHIN ToS](https://www.usga.org/content/usga/home-page/Handicap-ghin/ghin-terms-of-service.html) ·
[GHIN wrapper](https://github.com/boorad/ghin) ·
[OSM golf=tee](https://wiki.openstreetmap.org/wiki/Tag:golf=tee) ·
[OSM golf proposal talk](https://wiki.openstreetmap.org/wiki/Talk:Proposed_features/Golf_course)

Imagery and elevation:
[NAIP PC](https://planetarycomputer.microsoft.com/dataset/naip) ·
[NAIP AWS](https://registry.opendata.aws/naip/) ·
[NAIP 2023 Esri](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/imagery/naip-2023-imagery-is-now-available-in-the-naip-timeseries) ·
[Iowa map server](https://ortho.gis.iastate.edu/) ·
[Iowa Geodata imagery](https://geodata.iowa.gov/pages/imagery) ·
[Scott Co. 3-in ortho](https://www3.scottcountyiowa.gov/board/pub/enclosures/2024/20240130_Committee_of_the_Whole_830AM/08_IT_Orthophotos.pdf) ·
[3DEP QL spec](https://www.usgs.gov/core-science-systems/ngp/ss/lidar-base-specification-collection-requirements) ·
[E. Iowa lidar validation](https://pubs.usgs.gov/publication/ofr20251017) ·
[Meta CHM v2](https://registry.opendata.aws/dataforgood-fb-forestsv2) ·
[Clay NAIP](https://source.coop/clay/clay-v1-5-naip) ·
[Clay probes](https://clay-foundation.github.io/model/finetune/finetune-on-embeddings.html) ·
[Esri World Imagery](https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9) ·
[Esri Wayback export](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/imagery/wayback-export) ·
[OSM Esri](https://wiki.openstreetmap.org/wiki/Esri) ·
[Google 3D tiles FAQ](https://mapsplatform.google.com/resources/blog/commonly-asked-questions-about-our-recently-launched-photorealistic-3d-tiles/) ·
[Cesium-Google terms](https://cesium.com/legal/terms-for-google/) ·
[Mapbox imagery](https://docs.mapbox.com/data/tilesets/guides/imagery/)

Research and open source:
[AAU golf segmentation](https://vbn.aau.dk/en/publications/semantic-segmentation-of-golf-courses-for-course-rating-assistanc/) ·
[CRAUNet](https://www.researchgate.net/publication/373475773_Semantic_Segmentation_of_Golf_Courses_for_Course_Rating_Assistance) ·
[Kaggle Danish](https://www.kaggle.com/datasets/jacotaco/danish-golf-courses-orthophotos) ·
[Dataset Ninja Danish](https://datasetninja.com/danish-golf-courses-orthophotos) ·
[ariadgolf model](https://huggingface.co/ariadgolf/golf-course-segmentation) ·
[osm-course-mapper](https://github.com/opengolf-ai/osm-course-mapper) ·
[FairwayMapper](https://www.fairwaymapper.com/) ·
[FairwayMapper forum](https://community.openstreetmap.org/t/fairwaymapper-introducing-golfers-to-mapping/142814) ·
[hacker-yardage](https://github.com/npilk/hacker-yardage) ·
[golfTiles](https://github.com/HuggeK/golfTiles) ·
[golfcaddy PR](https://github.com/spobo1/golfcaddy/pull/1) ·
[woods PR](https://github.com/zeinbenjamin/woods/pull/15) ·
[Roboflow danish-golf](https://universe.roboflow.com/sportedge/danish-golf) ·
[Roboflow golf](https://universe.roboflow.com/a-lzzgm/golf-e0biu) ·
[DeepGolf](https://doaj.org/article/a15a73c830a843d5b82cf7bee33be2a7) ·
[Sentinel-2 golf CNN](https://iopscience.iop.org/article/10.1088/1755-1315/1633/1/012002) ·
[samgeo](https://samgeo.gishub.org/) ·
[samgeo SAM2 text](https://samgeo.gishub.org/examples/sam2_text_prompts/) ·
[TinySAM](https://arxiv.org/pdf/2312.13789) ·
[Mask2Former multispectral](https://citius.gal/static/8c5081f4e5b61a72dbfb82f3f2817f6c/igarss2025_mask2former_postprint_2025120212284780_e275c03c16.pdf) ·
[GFM usability](https://arxiv.org/pdf/2608.03804) ·
[golf texture motif](https://link.springer.com/chapter/10.1007/978-3-319-71589-6_48) ·
[NDVI grass phenology](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0181665) ·
[mowing texture](https://www.researchgate.net/publication/312299523_Estimating_Biomass_of_Native_Grass_Grown_under_Complex_Management_Treatments_Using_WorldView-3_Spectral_Derivatives)
