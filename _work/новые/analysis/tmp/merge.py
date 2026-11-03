# Ручное слияние строк одного пункта с разными редакциями -> rows2.json
import json, re
rows = json.load(open("rows.json"))
def find(pred): return [i for i, r in enumerate(rows) if pred(r)]
def txt(r): return next(iter(r["cells"].values()))["text"]
groups = [
  find(lambda r: r["g"] == "1" and any(c["n"] == "1.4" for c in r["cells"].values())),
  find(lambda r: r["g"] == "2.1" and any(c["n"] == "2.1.3" for c in r["cells"].values())),
  find(lambda r: r["g"] == "2.1" and re.search(r"осуществить опрос", txt(r))),
  find(lambda r: r["g"] == "3" and re.search(r"^3\.1", txt(r))),
  find(lambda r: r["g"] == "3" and re.search(r"^3\.2", txt(r))),
  find(lambda r: r["g"] == "8" and re.search(r"^8\.3", txt(r))),
  find(lambda r: r["g"] == "9"),
]
drop = set()
# реквизиты (разд. 9) не сравниваются построчно: отрезать их от п. 8.3 и заголовка 9
for r in rows:
    for c in r["cells"].values():
        L = c["text"].split("\n"); cut = [i for i, l in enumerate(L) if i and re.search(r"Мекенжайы|ФИО|Адрес", l)]
        if cut: c["text"] = "\n".join(L[:cut[0]])
for g in groups:
    assert g, g
    if len(g) == 1: continue
    for i in g[1:]:
        for k, c in rows[i]["cells"].items():
            if rows[g[0]]["g"] == "9":
                rows[g[0]]["cells"].setdefault(k, c); continue
            assert k not in rows[g[0]]["cells"], (k, g)
            rows[g[0]]["cells"][k] = c
        drop.add(i)
rows = [r for i, r in enumerate(rows) if i not in drop]
json.dump(rows, open("rows2.json", "w"), ensure_ascii=False, indent=1)
KEYS = ["Н1","Н2","Н3","Н4","Н5","Н6","Н7"]
def norm(t): return re.sub(r'[\s_«»"“”.,;:()\-–]+', ' ', re.sub(r'^\d+(\.\d+)*\.?\s*', '', t).lower()).strip()
same = 0; diff = []
for i, r in enumerate(rows):
    vals = {norm(c["text"]) for c in r["cells"].values()}
    if len(vals) == 1 and len(r["cells"]) == 7: same += 1
    else: diff.append(i)
print("строк:", len(rows), "одинаковы во всех 7:", same, "различаются/есть не везде:", len(diff))
print(diff)
