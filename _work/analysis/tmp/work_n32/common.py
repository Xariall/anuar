import json,os
OUT="/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_n32.json"
P="9. Костанайская область/договора/Приложение 16 Договор ФЛ  новый шаблон_(лизинг).docx"
def R(x): return P+", "+x
def add(rows):
    d=json.load(open(OUT))
    for t,s,r,q in rows:
        d[0]["items"].append({"part":"","topic":t,"summary":s,"ref":R(r) if r!="—" else "—","quote":q})
    json.dump(d,open(OUT,"w"),ensure_ascii=False,indent=1)
