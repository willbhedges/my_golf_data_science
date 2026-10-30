import json,math,sys
from geo import *
def meas(tee,line,green):
    # tee -> first corner ahead of the tee (skip line start) -> ... -> green centre
    dg=dist(tee,green); pts=[p for p in (line[1:-1] if len(line)>2 else []) if dist(p,green)<dg]
    return plen([tee]+pts+[green])
def on_line_at(card,line,green):
    """point at `card` yds back from the green along the hole line (extended behind its start)"""
    pts=[green]+[p for p in reversed(line[1:-1])]+[line[0]]
    acc=0
    for a,b in zip(pts,pts[1:]):
        d=dist(a,b)
        if acc+d>=card: t=(card-acc)/d; return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]
        acc+=d
    a,b=pts[-2],pts[-1]; d=dist(a,b); t=(card-acc+d)/d
    return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]
def centroid(poly):
    return [sum(p[0] for p in poly[:-1])/(len(poly)-1), sum(p[1] for p in poly[:-1])/(len(poly)-1)]
