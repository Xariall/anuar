# Разбивка русского текста Н1–Н7 на пункты -> clauses.json
import glob, re, json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
T = "../../text/"
KZ = set("әғқңөұүһіӘҒҚҢӨҰҮҺІ")
NUM = re.compile(r'^(\d+(?:\.\d+)*)\.?\s?(?=[А-Яа-я(«])')
HEAD = re.compile(r'^(\d)\.\s*[А-Я]')
out = {}
for f in sorted(glob.glob(T + "Н[1-7]*.txt")):
    key = os.path.basename(f)[:2]
    lines = [l.strip() for l in open(f, encoding="utf-8")]
    st = [i for i, l in enumerate(lines) if re.match(r"^ДОГОВОР\s*№", l)]
    assert len(st) == 1, (f, st)
    lines = lines[st[0]:]
    KW = re.compile(r"Шарт|\bосы\b|\bжәне\b|бойынша|Тапсырыс|Орындаушы|ережел|мерзім|жылғы|қолы|Т\.А\.Ж", re.I)
    rus = [l for l in lines if l and not any(c in KZ for c in l.replace("теңге", "")) and not KW.search(l) and re.search("[а-яА-Я]", l) or re.match(r"^9\.\s", l)]
    items, cur = [], None
    for l in rus:
        if l == "Оплата оказанных услуг": l = "3. " + l  # Н5: заголовок без номера
        m = NUM.match(l)
        if m and (HEAD.match(l) and len(l) < 80 or '.' in m.group(1) or HEAD.match(l)):
            cur = {"n": m.group(1), "text": l, "head": bool(HEAD.match(l) and len(l) < 80)}
            items.append(cur)
        elif cur is None:
            cur = {"n": "преамбула", "text": l, "head": False}; items.append(cur)
        else:
            cur["text"] += "\n" + l
    out[key] = items
json.dump(out, open("clauses.json", "w"), ensure_ascii=False, indent=1)
for k, v in out.items():
    print(k, len(v), [i["n"] for i in v][:60])
