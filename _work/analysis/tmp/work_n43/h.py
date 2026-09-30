import json,sys
OUT="/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_n43.json"
F="11. Мангистауская область/договора/Договор поручения рус.docx"
def init():
    json.dump([{"file":F,"reg_no":"43","status":"","items":[],"kk_divergences":[],"internal_contradictions":[],"residuals":[],"notes":""}],open(OUT,"w"),ensure_ascii=False,indent=1)
def add(rows,key="items"):
    d=json.load(open(OUT)); 
    for r in rows:
        if key=="items":
            d[0][key].append({"part":r[0],"topic":r[1],"summary":r[2],"ref":F.split("/",2)[0]+"/"+F.split("/",2)[1]+"/"+F.split("/")[-1]+", "+r[3],"quote":r[4]})
        else: d[0][key].append(r)
    json.dump(d,open(OUT,"w"),ensure_ascii=False,indent=1)
def setf(k,v):
    d=json.load(open(OUT)); d[0][k]=v; json.dump(d,open(OUT,"w"),ensure_ascii=False,indent=1)
