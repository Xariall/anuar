import json,sys
P="/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_n43.json"
F="11. Мангистауская область/договора/Договор поручения рус.docx"
def add(rows, key="items"):
    d=json.load(open(P,encoding="utf-8"))
    for r in rows:
        if key=="items":
            part,topic,summary,ref,quote=r
            d[0]["items"].append({"part":part,"topic":topic,"summary":summary,"ref":F+", "+ref,"quote":quote})
        else:
            d[0][key].append(r)
    json.dump(d,open(P,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print(len(d[0]["items"]))
