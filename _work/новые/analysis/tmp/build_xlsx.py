# Сборка 02_сравнение_договор_интервьюера.xlsx и 02_вопросы_на_решение.xlsx
import json, os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(open("rows2.json")); A = json.load(open("analysis.json")); Q = json.load(open("questions.json"))
KEYS = ["Н1","Н2","Н3","Н4","Н5","Н6","Н7"]
NAMES = {"Н1":"Н1 Н-020","Н2":"Н2 Т-001","Н3":"Н3 Т-004","Н4":"Н4 D002–D008","Н5":"Н5 УДН","Н6":"Н6 Н-050","Н7":"Н7 Н-060"}
# разделить строку 11: п. 2.1.4 Н4 — другое обязательство
items = []
for i, r in enumerate(rows):
    if i == 11:
        c = dict(r["cells"]); h4 = c.pop("Н4")
        items += [("11", c), ("11b", {"Н4": h4})]
    else: items.append((str(i), r["cells"]))
A["2"]["q"] = sorted(set(A["2"].get("q", []) + [13])); A["5"]["q"] = sorted(set(A["5"].get("q", []) + [13]))
FILL = {"одинаково":"E2EFDA","редакция":"FFF2CC","параметр":"FCE4D6","не во всех":"DDEBF7","противоречие":"F8CBAD","служебное":"F2F2F2"}
thin = Side(style="thin", color="BFBFBF")
def style(ws, widths):
    for c in ws[1]: c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="D9D9D9")
    for col, w in widths.items(): ws.column_dimensions[col].width = w
    for row in ws.iter_rows():
        for c in row: c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
    ws.freeze_panes = "C2"
wb = Workbook(); ws = wb.active; ws.title = "Сравнение"
ws.append(["№ строки","Условие"] + [NAMES[k] for k in KEYS] + ["Есть в","Нет в","Статус","Различия","Противоречия","Дефекты источника / примечание","Вопрос №"])
for n, (key, cells) in enumerate(items, 1):
    a = A[key]
    vals = [f"п. {cells[k]['n']}\n{cells[k]['text']}" if k in cells else "отсутствует" for k in KEYS]
    if a["status"] == "одинаково" and len(cells) == 7:   # одинаковый текст: полностью в Н1, в остальных — ссылка
        vals = [vals[0]] + [f"п. {cells[k]['n']}: совпадает с Н1" for k in KEYS[1:]]
    ws.append([n, a["label"]] + vals + [", ".join(k for k in KEYS if k in cells), ", ".join(k for k in KEYS if k not in cells) or "—",
               a["status"], a.get("diff", ""), a.get("contr", "") or ("нет" if a["status"] not in ("служебное", "одинаково") else ""), a.get("note", ""),
               ", ".join(map(str, a.get("q", [])))])
    ws.cell(row=ws.max_row, column=12).fill = PatternFill("solid", fgColor=FILL[a["status"]])
style(ws, {"A":7,"B":30,**{c:42 for c in "CDEFGHI"},"J":16,"K":12,"L":13,"M":60,"N":14,"O":55,"P":9})
# лист источников
s = wb.create_sheet("Источники")
s.append(["Код","Файл","Текстовая копия"])
for k in KEYS:
    fn = [f for f in os.listdir("../../исходники") if f.startswith(k + " ")][0]
    s.append([k, "_work/новые/исходники/" + fn, "_work/новые/text/" + fn[:-5] + ".txt"])
s.append([]); s.append(["Легенда статусов"])
for st, col in FILL.items():
    s.append([st]); s.cell(row=s.max_row, column=1).fill = PatternFill("solid", fgColor=col)
s.append([]); s.append(["Основа сравнения — русский текст. Казахская версия сверена по числовым параметрам в каждом пункте (kz_check.json): расхождение найдено только в п. 3.1 Н2 (год)."])
for col, w in {"A":14,"B":70,"C":70}.items(): s.column_dimensions[col].width = w
wb.save("../02_сравнение_договор_интервьюера.xlsx")
# реестр вопросов
qb = Workbook(); q = qb.active; q.title = "Вопросы"
q.append(["№","Тема","Пункты","Варианты и источники","Вопрос","Кто решает","Решение команды","Комментарий"])
for x in Q: q.append([x["n"], x["тема"], x["пункты"], x["варианты"], x["вопрос"], x["кто"], x.get("решение", ""), ""])
style(q, {"A":5,"B":26,"C":22,"D":70,"E":55,"F":18,"G":35,"H":30})
q.freeze_panes = "B2"
qb.save("../02_вопросы_на_решение.xlsx")
from collections import Counter
print(len(items), Counter(A[k]["status"] for k, _ in items))
