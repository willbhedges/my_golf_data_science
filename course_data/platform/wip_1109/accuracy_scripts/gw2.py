import sys, json, os, warnings
warnings.filterwarnings("ignore")
CD="/home/user/my_golf_data_science/course_data"
sys.path.insert(0, CD+"/platform")
import rebuild_tees_trees as R
slug=sys.argv[1]
pd=CD+"/packages/"+slug
pkg=json.load(open(pd+"/package.json"))
pos=R.tee_positions(pkg,pd,slug,[])
for ref in sys.argv[2:]:
    for s,r in pos[ref]["tees"].items():
        print(ref,s,r.get("method"),r.get("tee_id"),r.get("p_assign"),r.get("dist_yd"),r.get("borrowed"),r.get("alternatives"), round(r["lat"],6), round(r["lon"],6))
