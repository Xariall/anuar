# Казахский текст по пунктам для Н1–Н7 -> kz_clauses.json {док: {номер: текст}}
# Н1, Н6, Н7 — таблица «каз | рус» (берём левую ячейку); Н2–Н5 — казахский блок до строки «ДОГОВОР №»
import zipfile, re, json, os, glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SRC = "../../исходники/"
NUM = re.compile(r'^(?:(\d+\.\d+(?:\.\d+)*)(?:\.\s*|\s+)|(\d)\.\s*)(?=\S)')
def paras(xml):
    out = []
    for p in re.findall(r'<w:p[ >].*?</w:p>', xml, re.S):
        t = "".join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))
        t = t.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        if t.strip(): out.append(t.strip())
    return out
def split(lines):
    d, cur, pre = {}, None, []
    for l in lines:
        # Н2–Н5: заголовки разд. 1, 2 и п. 2.4 без номера (или «.2.4.») — присвоить номер, чтобы не прилипали к предыдущему пункту
        h = {"Шарттың мәні": "1", "Тараптардың құқықтары мен міндеттері": "2"}.get(l.strip())
        if h: l = f"{h}. {l.strip()}"
        if l.startswith(".2.4."): l = l[1:]
        m = NUM.match(l)
        if m and not re.match(r'^\d{3,}', l):
            cur = (m.group(1) or m.group(2)).rstrip("."); d.setdefault(cur, ""); d[cur] += ("\n" if d[cur] else "") + l
        elif cur: d[cur] += "\n" + l
        else: pre.append(l)
    d["преамбула"] = "\n".join(pre)
    return d
res = {}
for f in sorted(glob.glob(SRC + "Н[1-7]*.docx")):
    k = os.path.basename(f)[:2]; x = zipfile.ZipFile(f).read("word/document.xml").decode()
    if k in ("Н1", "Н6", "Н7"):
        kz = []
        for r in re.findall(r'<w:tr[ >].*?</w:tr>', x, re.S):
            cells = re.findall(r'<w:tc>.*?</w:tc>', r, re.S)
            if len(cells) == 2: kz += paras(cells[0])
    else:
        allp = paras(x); i = [j for j, l in enumerate(allp) if re.match(r'^ДОГОВОР\s*№', l)][0]; kz = allp[:i]
    res[k] = split(kz)
json.dump(res, open("kz_clauses.json", "w"), ensure_ascii=False, indent=1)
ru = json.load(open("clauses.json"))
for k in sorted(res):
    rn = [c["n"] for c in ru[k]]; kn = list(res[k])
    print(k, "нет в каз:", [n for n in rn if n not in res[k]], "| лишние в каз:", [n for n in kn if n not in rn])
