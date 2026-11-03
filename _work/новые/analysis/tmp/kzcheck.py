# Сверка чисел в одноимённых пунктах казахской и русской версий -> kz_check.json
import glob, re, json, os
KZ = set("әғқңөұүһіӘҒҚҢӨҰҮҺІ")
NUM = re.compile(r'^(\d+(?:\.\d+)+)\.?\s?')
def split(lines):
    out, cur = {}, None
    for l in lines:
        m = NUM.match(l)
        if m: cur = m.group(1); out.setdefault(cur, "")
        if cur: out[cur] += " " + l
    return out
def nums(t):
    t = NUM.sub('', t.strip())
    return sorted(re.findall(r'(?<![\d.])\d+(?:[.,]\d+)?(?![\d.])', re.sub(r'\b\d+(\.\d+)+\b', '', t)))
res = {}
for f in sorted(glob.glob("../../text/Н[1-7]*.txt")):
    k = os.path.basename(f)[:2]
    L = [l.strip() for l in open(f, encoding="utf-8") if l.strip()]
    kz = split([l for l in L if any(c in KZ for c in l.replace("теңге", ""))])
    ru = split([l for l in L if not any(c in KZ for c in l.replace("теңге", ""))])
    for n in sorted(set(kz) | set(ru), key=lambda x: [int(p) for p in x.split(".")]):
        a, b = nums(kz.get(n, "")), nums(ru.get(n, ""))
        if n not in kz or n not in ru: res.setdefault(k, []).append({"п": n, "нет_в": "каз" if n not in kz else "рус"})
        elif a != b: res.setdefault(k, []).append({"п": n, "каз": a, "рус": b})
json.dump(res, open("kz_check.json", "w"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, v)
