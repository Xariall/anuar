# Сопоставление пунктов Н1–Н7 по смыслу текста внутри подраздела -> rows.json
import json, re, difflib
d = json.load(open("clauses.json"))
ORDER = ["Н1","Н6","Н5","Н2","Н3","Н7","Н4"]
def body(t): return re.sub(r'^\d+(\.\d+)*\.?\s*', '', t)
def norm(t): return re.sub(r'[\s_«»"“”.,;:()\-–]+', ' ', body(t).lower()).strip()
def grp(n):
    if n == "преамбула": return "0"
    p = n.split("."); return ".".join(p[:2]) if len(p) >= 3 else p[0]
rows = []
for k in ORDER:
    used = set()
    for it in d[k]:
        g = grp(it["n"]); best, bs = None, 0
        for ri, r in enumerate(rows):
            if r["g"] != g or ri in used or k in r["cells"]: continue
            ref = next(iter(r["cells"].values()))
            s = difflib.SequenceMatcher(None, norm(ref["text"])[:600], norm(it["text"])[:600]).ratio()
            if s > bs: best, bs = ri, s
        if best is not None and (bs >= 0.5 or it["head"]):
            rows[best]["cells"][k] = it; used.add(best)
        else:
            # вставить после последней строки, занятой этим договором
            pos = max([i for i, r in enumerate(rows) if k in r["cells"]], default=-1) + 1
            rows.insert(pos, {"g": g, "cells": {k: it}}); used = {u + (u >= pos) for u in used} | {pos}
json.dump(rows, open("rows.json", "w"), ensure_ascii=False, indent=1)
KEYS = ["Н1","Н2","Н3","Н4","Н5","Н6","Н7"]
for i, r in enumerate(rows):
    c = r["cells"]; any_ = next(iter(c.values()))
    print("%3d" % i, " ".join("%-6s" % (c[k]["n"] if k in c else "—") for k in KEYS), "|", body(any_["text"]).replace("\n"," ")[:70])
