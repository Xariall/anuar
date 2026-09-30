import json,sys
OUT="/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_t1b.json"
P="17. Туркестанская область/договара/Договор залог, ДПМ и договор гарантии.doc"
PART="Гарантия (Приложение №7)"
def add(rows, key="items"):
    d=json.load(open(OUT))
    for r in rows:
        if key=="items":
            t,s,ref,q=r
            d[0]["items"].append({"part":PART,"topic":t,"summary":s,"ref":ref if ref=="—" else P+", "+ref,"quote":q})
        else: d[0][key].append(r)
    json.dump(d,open(OUT,"w"),ensure_ascii=False,indent=1)
