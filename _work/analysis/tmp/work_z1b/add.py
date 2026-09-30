import json,sys
OUT="/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_z1b.json"
PFX="7. Западно-Казахстанская область/договора/Приложения Договора ++25.09.26++.docx, "
L="Приложение №2-1: договор финансового лизинга"
def load():
    return json.load(open(OUT,encoding="utf-8"))
def save(d):
    json.dump(d,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
def add(rows,part=L):
    d=load()
    for r in rows:
        topic,summ,ref,q=r[:4]
        p=r[4] if len(r)>4 else part
        d[0]["items"].append({"part":p,"topic":topic,"summary":summ,"ref":(PFX+ref) if ref!="—" else "—","quote":q})
    save(d)
