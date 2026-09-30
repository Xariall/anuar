import json
OUT="/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_z2b.json"
R="7. Западно-Казахстанская область/договора/Приложения Договора ++25.09.26++.docx"
Z="Приложение №3-1: договор залога (залогодатель ≠ заемщик)"
G="Приложение №4: договор гарантии"
def add(part, rows, key="items"):
    d=json.load(open(OUT,encoding="utf-8"))
    for r in rows:
        if key=="items":
            t,s,ref,q=r
            d[0]["items"].append({"part":part,"topic":t,"summary":s,"ref":(R+", "+ref) if ref!="—" else "—","quote":q})
    json.dump(d,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
def setf(k,v):
    d=json.load(open(OUT,encoding="utf-8")); d[0][k]=v
    json.dump(d,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
