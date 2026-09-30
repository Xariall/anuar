import json,sys
F="/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_n65.json"
P="17. Туркестанская область/договара/ФИН ЛИЗИНГ Ауыл-Аманат.doc, "
def add(rows, part="Договор финансового лизинга"):
    d=json.load(open(F)); 
    for t,s,r,q in rows:
        d[0]["items"].append({"part":part,"topic":t,"summary":s,"ref":P+r,"quote":q})
    json.dump(d,open(F,"w"),ensure_ascii=False,indent=1)
    print(len(d[0]["items"]))
