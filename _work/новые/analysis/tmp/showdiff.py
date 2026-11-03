import json, re, difflib, sys
rows = json.load(open("rows2.json"))
KEYS = ["Н1","Н2","Н3","Н4","Н5","Н6","Н7"]
def norm(t): return re.sub(r'[\s_«»"“”.,;:()\-–]+', ' ', re.sub(r'^\d+(\.\d+)*\.?\s*', '', t).lower()).strip()
for i in map(int, sys.argv[1:]):
    r = rows[i]; groups = {}
    for k in KEYS:
        if k in r["cells"]: groups.setdefault(norm(r["cells"][k]["text"]), []).append(k)
    gl = sorted(groups.items(), key=lambda x: -len(x[1]))
    base = gl[0][0].split()
    print(f"\n##### строка {i}  пп.:", {k: r['cells'][k]['n'] for k in r['cells']}, " нет в:", [k for k in KEYS if k not in r["cells"]])
    print(f"  [{','.join(gl[0][1])}] БАЗА: {gl[0][0][:1500]}")
    for t, ks in gl[1:]:
        sm = difflib.SequenceMatcher(None, base, t.split()); ch = []
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op != "equal": ch.append(f"{op}: «{' '.join(base[a1:a2])[:300]}» → «{' '.join(t.split()[b1:b2])[:300]}»")
        print(f"  [{','.join(ks)}] " + " | ".join(ch))
