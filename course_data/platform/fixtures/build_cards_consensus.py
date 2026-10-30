"""Rebuild fixtures/cards_consensus.json from the reviewed library courses (needs course_data/library + research/web)."""
import json, os, sys, glob
WT = __import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, WT + '/course_data/platform')
import scorecard as s, card_consensus as cc
LIB = WT + '/course_data/library'
WEB = WT + '/course_data/research/web'
AS = {'finkbine': 'rv02_cards/07', 'harvester': 'rv02_cards/08', 'gustin': 'rv11_cards/02', 'adams_pointe': 'rv11_cards/16',
      'la_nickell': 'rv14_cards/02', 'tpc_deere_run': 'rv04_deere_weaver/02'}
extra = sys.argv[1:]  # more research dirs for allsquare pages
courses = ['finkbine', 'harvester', 'gustin', 'creekmoor', 'buffalo_ridge', 'la_nickell', 'old_kinderhook', 'st_andrews_op',
           'tpc_deere_run', 'weaver_ridge', 'eagle_bend', 'falcon_ridge', 'painted_hills', 'lake_shawnee']
def slim(card):
    c = s.normalise(card)
    keep = {}
    for n, t in c['tee_sets'].items():
        keep[n] = {k: t.get(k) for k in ('colour', 'aliases', 'yards', 'total', 'total_stated', 'rating', 'slope') if t.get(k) is not None}
    return dict(schema='scorecard/1', source=c.get('source'), par=c.get('par'), tee_sets=keep,
                **({'card_date': c['card_date']} if c.get('card_date') else {}))
out = {}
for c in courses:
    sw = json.load(open(f'{LIB}/{c}/raw/scorecard_web.json'))
    cards = [dict(kind=x['source'], url=x['url'], card=slim(x['card'])) for x in sw['cards']]
    for f, kind in (('card_review.json', 'review'), ('card_golfify.json', 'golfify_review'), ('card_fix.json', 'review_fix')):
        if os.path.exists(f'{LIB}/{c}/{f}'):
            cards.append(dict(kind=kind, url=f'course_data/library/{c}/{f}', card=slim(json.load(open(f'{LIB}/{c}/{f}')))))
    if c in AS and os.path.exists(f'{WEB}/{AS[c]}.html'):
        card, info = s.parse_allsquare(open(f'{WEB}/{AS[c]}.html').read())
        if card:
            cards.append(dict(kind='allsquare', url=f'course_data/research/web/{AS[c]}.html', card=slim(card)))
    pkg = json.load(open(f'{LIB}/{c}/package.json'))
    out[c] = dict(course=pkg['request']['course'], cards=cards, ground=cc.ground_from_package(pkg))
json.dump(out, open(WT + '/course_data/platform/fixtures/cards_consensus.json', 'w'), separators=(',', ':'))
print(os.path.getsize(WT + '/course_data/platform/fixtures/cards_consensus.json'))
