# Версия 0 единого договора с интервьюером: двуязычная (каз | рус), короткие вопросы -> v0.json
# Вход: rows2.json (русские пункты Н1–Н7, сопоставленные), kz_clauses.json (казахские пункты), analysis.json
# Казахский текст пункта берётся из того же договора и того же пункта, что и русский.
import json, re, os, zipfile
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(open("rows2.json")); A = json.load(open("analysis.json")); KZ = json.load(open("kz_clauses.json"))
KEYS = ["Н1", "Н2", "Н3", "Н4", "Н5", "Н6", "Н7"]
FORM = {"Н1": "Н-020", "Н2": "Т-001", "Н3": "Т-004", "Н4": "D002–D008", "Н5": "УДН", "Н6": "Н-050", "Н7": "Н-060"}

# Решённые вопросы: 1 (форма — из справочника), 12 (раскладка «каз | рус» как в исходниках; реквизиты обеих сторон — по Н1)
Q = {
 2: "❓ 2. Название акта: «Акт выполненных работ (оказанных услуг)» (5 договоров) или «Акт оказанных услуг» (Т-001, Т-004)?",
 3: "❓ 3. Объём: какой вариант для какой формы? «График работы интервьюера» (D-формы) — это приложение к договору?",
 4: "❓ 4. Что выдаётся и возвращается: один перечень для всех с оговоркой «если это предусмотрено статистическим наблюдением» или свой для каждой формы? Для Н-060: выдаётся ли список анкет (вернуть его надо)?",
 5: "❓ 5. Пункт есть не во всех договорах. Включить для всех с оговоркой «если это предусмотрено статистическим наблюдением» или только для форм, где он был?",
 6: "❓ 6. Только D-формы: интервьюер оформляет договоры с членами домохозяйств. Оставить? (нужен юрист)",
 7: "❓ 7. Срок предупреждения об отказе: 3 дня (Н-020, Н-050, Н-060), 30 дней (Т-001, Т-004, D-формы) или 5 дней (УДН)?",
 8: "❓ 8. В исходниках ссылки на пункты сбиты — здесь поставлены верные номера [в скобках]. Согласны? Пункт есть везде, кроме УДН — включаем для всех?",
 9: "❓ 9. Правило о невозврате имущества повторено дважды (как в 4 договорах). Убрать повтор (как в Т-001, Т-004)? И «подмена респондента» или «подмена домашнего хозяйства»?",
 10: "❓ 10. Какая формула оплаты для какой формы? В Т-001 уже вписаны 26 МРП на 2026 г. и нормы 47/50 — оставить или сделать пустые поля?",
 11: "❓ 11. Срок действия: пустое поле или «до 1 ноября» (как в УДН)?",
 13: "❓ 13. Н-060 (посетители): вариант этого договора или отдельный шаблон? В Н-060 п. 1.1 — «по опросу и сбору…» без «домашних хозяйств», объём и оплата — в анкетах.",
}
QROW = {"2": [13], "4": [2], "5": [3], "10": [4], "11": [5], "11b": [5], "12": [5], "25": [6], "26": [4], "27": [7],
        "28": [8], "30": [8], "34": [4], "40": [9], "43": [10], "63": [11]}

def strip_n(t): return re.sub(r'^\.?\d+(\.\d+)*\.?\s*', '', t.strip())
def norm(t): return re.sub(r'[\s_«»"“”.,;:()\-–]+', ' ', strip_n(t).lower()).strip()
def kz_of(doc, n):
    t = KZ[doc].get(n) or KZ["Н1"].get(n, "")
    t = re.sub(r'\n\.\d+(\.\d+)*\..*$', '', t, flags=re.S)        # Н2/Н3: к 2.3.4 приклеен заголовок «.2.4.»
    return strip_n(t)
def forms(ks): return ", ".join(FORM[k] for k in ks)

items = []
for i, r in enumerate(rows):
    if i == 11:
        c = dict(r["cells"]); h4 = c.pop("Н4"); items += [("11", c), ("11b", {"Н4": h4})]
    else: items.append((str(i), r["cells"]))

num, sec, sub, subsub = {}, 0, 0, 0                                 # сквозная нумерация черновика
for key, cells in items:
    n = next(iter(cells.values()))["n"]
    if key == "0": num[key] = None; continue
    if A[key]["status"] == "служебное" and n.count(".") == 0: sec = int(n); sub = 0; num[key] = str(sec); continue
    p = n.split(".")
    if len(p) == 2: sub = int(p[1]); subsub = 0; num[key] = f"{sec}.{sub}"
    else: subsub += 1; num[key] = f"{sec}.{sub}.{subsub}"
NOTICE, RAST = num["27"], num["28"]
def fix_refs(t, targets):
    it = iter(targets)
    return re.sub(r'2\.1\.\d+', lambda m: f"[{next(it, NOTICE)}]", t)

COLOR = {"одинаково": "none", "служебное": "none", "редакция": "yellow", "параметр": "orange", "не во всех": "blue"}
seen = set()
def comment(key, extra=None):
    L = list(extra or [])
    for q in QROW.get(key, []):
        L.append(Q[q] if q not in seen else f"См. вопрос {q}."); seen.add(q)
    return L or None

out = []
for key, cells in items:
    a = A[key]; st = a["status"]; ks = [k for k in KEYS if k in cells]; nid = num[key]
    groups = {}
    for k in ks: groups.setdefault(norm(cells[k]["text"]), []).append(k)
    gl = sorted(groups.values(), key=lambda g: -len(g))
    d0 = gl[0][0]; n0 = cells[d0]["n"]
    if key == "0":
        ru = strip_n(cells["Н1"]["text"]).split("\n", 2)[2]
        kz = KZ["Н1"]["преамбула"].split("\n", 2)[2]
        out.append({"kind": "clause", "id": None, "color": "none", "kz": kz, "ru": ru}); continue
    if key == "64":
        out.append({"kind": "heading", "kz": "9. Тараптардың мекенжайлары мен банктік деректемелері", "ru": "9. Адреса и банковские реквизиты Сторон"})
        out.append({"kind": "requisites"}); continue
    if st == "служебное":
        kind = "heading" if n0.count(".") == 0 else "subhead"
        out.append({"kind": kind, "kz": f"{nid}. " + kz_of(d0, n0).rstrip(":") + (":" if kind == "subhead" else ""),
                    "ru": f"{nid}. " + strip_n(cells[d0]["text"]).rstrip(":") + (":" if kind == "subhead" else "")}); continue
    c = {"kind": "clause", "id": nid, "color": COLOR[st]}
    if key == "2":                                                   # решение по вопросу 1: форма из справочника
        F_RU, F_KZ = "[ФОРМА — из справочника форм]", "[НЫСАН — нысандар анықтамалығынан]"
        c["ru"] = re.sub(r"\s+в объеме", " в объеме", strip_n(cells["Н2"]["text"]).replace("Т-001 (месячная) «Анкета выборочного обследования занятости населения»", F_RU))
        c["kz"] = re.sub(r"\s+іріктемелі", " іріктемелі", kz_of("Н2", "1.1").replace("«Халықтың жұмыспен қамтылуын іріктемелі зерттеу сауалнамасы» Т-001 (айлық)", F_KZ))
        assert F_RU in c["ru"] and F_KZ in c["kz"]; c["color"] = "none"
    elif COLOR[st] == "orange":
        c["variants"] = [{"forms": forms(g), "ru": strip_n(cells[g[0]]["text"]), "kz": kz_of(g[0], cells[g[0]]["n"])} for g in gl]
    else:
        c["ru"] = strip_n(cells[d0]["text"]); c["kz"] = kz_of(d0, n0)
    if key == "28": c["ru"] = fix_refs(c["ru"], [NOTICE]); c["kz"] = fix_refs(c["kz"], [NOTICE])
    if key == "30": c["ru"] = fix_refs(c["ru"], [NOTICE, RAST]); c["kz"] = fix_refs(c["kz"], [NOTICE, RAST])
    extra = [f"Есть только в: {forms(ks)}."] if COLOR[st] == "blue" else []
    c["comment"] = comment(key, extra)
    out.append(c)

# реквизиты — дословно из Н1 (двуязычная таблица: Заказчик | Исполнитель)
x = zipfile.ZipFile("../../исходники/Н1 Договор Н-020 (цифровые технологии).docx").read("word/document.xml").decode()
trs = re.findall(r'<w:tr[ >].*?</w:tr>', x, re.S); st_i = [i for i, r in enumerate(trs) if "Адреса и банковские" in r][0]
def ptexts(cx): return ["".join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)) for p in re.findall(r'<w:p[ >].*?</w:p>', cx, re.S)]
req = []
for r in trs[st_i + 1:]:
    cl = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
    l, rr = ("\n".join(t for t in ptexts(cl[0]) if t.strip()), "\n".join(t for t in ptexts(cl[1]) if t.strip()))
    if l or rr: req.append([l.replace("&quot;", '"'), rr.replace("&quot;", '"')])

intro = ["Рабочий черновик (версия 0) единого договора с интервьюером, собран из 7 шаблонов БНС. Текст — дословно из исходников; казахский текст каждого пункта — из того же договора, что и русский.",
         "Вопросы команде — в примечаниях (❓). Решено: форма подставляется из справочника; раскладка «каз | рус», как в исходниках."]
json.dump({"intro": intro, "clauses": out, "requisites": req}, open("v0.json", "w"), ensure_ascii=False, indent=1)
print("строк:", len(out), "вопросов:", sorted(seen), "реквизиты:", len(req))
