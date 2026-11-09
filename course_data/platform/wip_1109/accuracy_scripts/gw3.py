import sys, json, os, warnings
warnings.filterwarnings("ignore")
CD="/home/user/my_golf_data_science/course_data"
sys.path.insert(0, CD+"/platform")
import rebuild_tees_trees as R, error_budget as E
slug, ref, S = sys.argv[1:4]
pd=CD+"/packages/"+slug; pkg=json.load(open(pd+"/package.json"))
for cw in (0.0, 0.3):
    PP=R._load("rtt_platform_package", os.path.join(R.HERE,"package.py")); lz=PP.load(os.path.join(CD,"tees","localize.py"),"cdp_tee_localize"); lz.PARAMS.update(canopy_w=cw)
    R._load=lambda n,p,_m=PP:_m
    pos=R.tee_positions(pkg,pd,slug,[])
    r=pos[ref]["tees"][S]; print(cw, r.get("method"), r.get("tee_id"), r.get("p_assign"), r.get("dist_yd"), r.get("canopy_blocked_yd"), r.get("alternatives"), r.get("error_yd"))
