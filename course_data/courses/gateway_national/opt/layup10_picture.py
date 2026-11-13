import sys, os, json, numpy as np
ROOT='/home/user/my_golf_data_science/'
sys.path.insert(0, ROOT+'course_data/courses/gateway_national/opt'); sys.path.insert(0, ROOT+'course_data/courses')
import layup10 as LU
P5=LU.P5
import rasterio, pyproj
from scipy.ndimage import map_coordinates
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
which=sys.argv[1]
Wd=P5.World(which); M=Wd.M
sys.path.insert(0, ROOT+'course_data/imagery'); import render as RD
h=10; hd=Wd.course.HOLES[h]; R=M.Raster(hd); bearing=float(Wd.course.BEARINGS[h])
wx=Wd.wx(h,P5.DAYS['sat']); P=M.central(temp_f=wx['temp']); S=R.strokes(P,hd['length']); z=M.draws_z(3000,77); rel=(wx['frm']-bearing)%360
fr=RD.Frame.from_json(Wd.course.FRAMES[h]); tee,fwd,right,ppy=M.frame(hd)
src=rasterio.open(ROOT+'course_data/packages/gateway_national/imagery/naip_rgb.tif'); img=src.read(); T=pyproj.Transformer.from_crs(4326,src.crs,always_xy=True)
a0,a1,x0,x1=90,315,-70,75; st=0.3
xs=np.arange(x0,x1,st); als=np.arange(a0,a1,st); XX,AA=np.meshgrid(xs,als)
px=tee+(AA.ravel()[:,None]*fwd+XX.ravel()[:,None]*right)*ppy
ll=np.asarray(fr.px_to_ll(px)); E,N=T.transform(ll[:,0],ll[:,1]); rr,cc=rasterio.transform.rowcol(src.transform,E,N,op=float)
rgb=np.stack([map_coordinates(b.astype(float),[np.array(rr),np.array(cc)],order=1).reshape(XX.shape) for b in img[:3]],-1)
lo,hi=np.percentile(rgb,[1,99]); rgb=np.clip((rgb-lo)/(hi-lo),0,1)
COL={'water':'#3af','native':'orange','sand':'yellow','recovery':'#0a0','ob':'r','fairway':'lime','first_cut':'#9f9'}
clubs=['8-iron','Mid iron','Long iron','4-wood','2-wood']
fig,axs=plt.subplots(1,len(clubs)+1,figsize=(4.2*(len(clubs)+1),7.2))
gp=np.asarray(hd['green_poly'])
for i,ax in enumerate(axs):
    ax.imshow(rgb,extent=[x0,x1,a0,a1],origin='lower')
    if i==0:
        for name,poly in hd['zones']:
            if len(poly)<3: continue
            p=(np.asarray(poly,float)-tee)/ppy; q=np.c_[p@right,p@fwd]; q=np.r_[q,q[:1]]; ax.plot(q[:,0],q[:,1],color=COL.get(name,'w'),lw=0.8)
        g=np.r_[gp,gp[:1]]; ax.plot(g[:,1],g[:,0],color='cyan',lw=1)
        for c,(lo_,hi_) in (('wood',LU.WINDOW['wood']),('iron',LU.WINDOW['iron'])):
            ax.axvline(lo_,color='w',ls=':' if c=='iron' else '--',lw=0.8); ax.axvline(hi_,color='w',ls='--',lw=0.8)
        ax.set_title('map zones; lay-up window (finishing line)\nirons 5 L..45 R (dotted), woods 5 R..45 R',fontsize=8)
    else:
        c=clubs[i-1]; o=LU.lay_solve(Wd,hd,R,S,P,z,c,wx['mph'],rel,True)
        col=np.where(np.isin(o['lie'],[M.CODE['water'],M.CODE['native'],M.CODE['ob']]),'r',np.where(o['lie']==M.CODE['sand'],'yellow',np.where(np.isin(o['lie'],[M.CODE['fairway'],M.CODE['first_cut']]),'w','#f90')))
        ax.scatter(o['l'],o['a'],s=1.2,c=col,alpha=.6,lw=0)
        ax.plot([0,o['aim']*1.0],[0,o['total']],color='#ffc928',lw=0.8); ax.plot(o['aim'],o['total'],'+',color='#ffc928',ms=10)
        ax.set_title('%s lay-up: aim %+.1f, %.0f total, %.2f strokes\nwhite fairway, orange rough, yellow sand, red lost'%(c,o['aim'],o['total'],o['ev']),fontsize=8)
    ax.axvline(0,color='m',lw=0.3); ax.set_xlim(x0,x1); ax.set_ylim(a0,a1); ax.set_yticks(np.arange(a0,a1,10)); ax.set_xticks(np.arange(-70,75,10)); ax.grid(color='w',lw=0.2,alpha=.5); ax.tick_params(labelsize=6)
fig.suptitle('Hole 10 from the %s tee, Saturday: each club at its best lay-up aim (3,000 swings)'%LU.SET_OF[which],fontsize=10)
fig.tight_layout(); fn='h10_layup_%s.jpg'%LU.SET_OF[which]; fig.savefig(fn,dpi=72); print(fn)
