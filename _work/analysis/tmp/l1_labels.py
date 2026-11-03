# Замена номеров реестра (№N) на понятные названия источников в комментариях черновика займа.
# Текст пунктов (дословные формулировки договоров) не меняется.
import json, re

# № реестра -> (краткое название, регион, файл)
SRC = {
 32: ('Костанай', '9. Костанайская область', 'Приложение 16 Договор ФЛ  новый шаблон_(лизинг).docx'),
 65: ('Туркестан', '17. Туркестанская область', 'договара/ФИН ЛИЗИНГ Ауыл-Аманат.doc'),
 24: ('ЗКО (Прил. 2-1)', '7. Западно-Казахстанская область', 'Приложения Договора ++25.09.26++.docx — Приложение №2-1'),
}
# Как регион уже мог быть подписан рядом с номером (чтобы не дублировать)
ALIAS = r'(?:\s+(?:Костанай|Туркестан|ЗКО(?:,\s*Прил\.\s?2-1)?))?'
# Контекст, где «№» — не номер договора по реестру (вопрос реестра, приложение, приказ и т. п.)
SKIP = re.compile(r'(вопрос\w*|реестр\w*|Приложени\w*|Прил\.|приказ\w*|постановлени\w*|поручения|протокол\w*|решени\w*)[^;()]{0,12}$', re.I)

def relabel(s):
    if not s: return s
    out, pos, prev_skip, prev_end = [], 0, False, -100
    for m in re.finditer(r'№\s?(\d{1,2})\b' + ALIAS, s):
        before = s[max(0, m.start() - 40):m.start()]
        in_list = re.fullmatch(r'\s*(?:,|и|/|–|-)\s*', s[prev_end:m.start()] or 'x') is not None
        if in_list: skip = prev_skip
        else: skip = bool(re.search(r'(вопрос\w*(?:\s+реестра)?|Приложени\w*|Прил\.|приказ\w*|постановлени\w*|поручения|протокол\w*|решени\w*|этап\s?\d\s?[—–-]|реестра)\s*(?:\(|:)?\s*$', before, re.I))
        n = int(m.group(1)); prev_skip, prev_end = skip, m.end()
        if skip or n not in SRC: continue
        out.append(s[pos:m.start()]); out.append(SRC[n][0]); pos = m.end()
    out.append(s[pos:])
    r = ''.join(out)
    return re.sub(r'([\w)])\s\(((?:п|пп|разд|ст)\.[^()]*)\)', r'\1, \2', r)

def nums(lst):
    return {int(x) for s in (lst or []) for x in re.findall(r'№\s?(\d{1,2})\b', s) if int(x) in SRC}

d = json.load(open('l1_draft.json'))
for c in d['clauses']:
    pres, absn = nums(c.get('present_in')), nums(c.get('absent_in'))
    allabs = any(re.search(r'все|остальн|прочие', x) for x in (c.get('absent_in') or []))
    if c.get('kind') == 'heading' or c.get('color') == 'none': pass
    elif absn and not allabs and len(absn) <= len(pres):
        c['presence_summary'] = 'Есть во всех договорах, кроме: ' + ', '.join(SRC[n][0] for n in sorted(absn))
    elif not absn and not allabs and pres:
        c['presence_summary'] = 'Есть во всех договорах, где регулируется этот вопрос'
    elif pres:
        c['presence_summary'] = 'Есть только в: ' + ', '.join(SRC[n][0] for n in sorted(pres))
    for k in ('text_source', 'note'):
        c[k] = relabel(c.get(k))
    for k in ('present_in', 'absent_in'):
        c[k] = [relabel(x) for x in (c.get(k) or [])]
    for v in c.get('variants') or []:
        v['sources'] = [relabel(x) for x in v['sources']]
d['sources'] = [{'short': SRC[n][0], 'region': SRC[n][1], 'file': SRC[n][2]} for n in sorted(SRC, key=lambda n: (int(SRC[n][1].split('.')[0]), n))]
json.dump(d, open('l1_draft_labeled.json', 'w'), ensure_ascii=False, indent=1)
left = sorted({m for c in d['clauses'] for s in [c.get('text_source') or '', c.get('note') or ''] + [x for v in c.get('variants') or [] for x in v['sources']] + (c.get('present_in') or []) for m in re.findall(r'.{0,25}№\s?\d{1,2}\b', s) if not re.search(r'(вопрос\w*(?:\s+реестра)?|Приложени\w*|этап \d —)\s*(?:\(|:)?\s*№', m)})
print('clauses', len(d['clauses']), '| осталось «№..» в комментариях:', len(left)); print('\n'.join(left[:25]))
