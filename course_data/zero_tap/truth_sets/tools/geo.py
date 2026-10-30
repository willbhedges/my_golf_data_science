import json,math
YD=1/0.9144
KY=110540*YD
def kx(lat): return 111320*math.cos(math.radians(lat))*YD
def ll2xy(ll,o): return ((ll[0]-o[0])*kx(o[1]),(ll[1]-o[1])*KY)
def xy2ll(x,y,o): return [o[0]+x/kx(o[1]), o[1]+y/KY]
def dist(a,b): x,y=ll2xy(b,a); return math.hypot(x,y)
def plen(pts): return sum(dist(a,b) for a,b in zip(pts,pts[1:]))
class Img:
    """photo pixel <-> lon/lat for a 'tee'-kind page image"""
    def __init__(s,m):
        s.m=m; s.o=m['tee_ll']; b=math.radians(m['bearing']); s.u=(math.sin(b),math.cos(b)); s.rv=(math.cos(b),-math.sin(b))
    def ll2px(s,ll):
        x,y=ll2xy(ll,s.o); al=x*s.u[0]+y*s.u[1]; lat=x*s.rv[0]+y*s.rv[1]; m=s.m
        px=m['tee'][0]+(al*m['f'][0]+lat*m['r'][0])*m['ppy']; py=m['tee'][1]+(al*m['f'][1]+lat*m['r'][1])*m['ppy']
        return ((px-m['x0'])*m['s'],(py-m['y0'])*m['s'])
    def px2ll(s,u,v):
        m=s.m; px=u/m['s']+m['x0']; py=v/m['s']+m['y0']; dx=(px-m['tee'][0])/m['ppy']; dy=(py-m['tee'][1])/m['ppy']
        al=dx*m['f'][0]+dy*m['f'][1]; lat=dx*m['r'][0]+dy*m['r'][1]
        x=al*s.u[0]+lat*s.rv[0]; y=al*s.u[1]+lat*s.rv[1]; return xy2ll(x,y,s.o)
