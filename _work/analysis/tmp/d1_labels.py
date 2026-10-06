# Замена номеров реестра (№N) на понятные названия источников в комментариях черновика займа.
# Текст пунктов (дословные формулировки договоров) не меняется.
import json, re

# № реестра -> (краткое название, регион, файл)
SRC = {
 2:  ('Акмола', '1. Акмолинская область', 'ДОГ Займа.docx'),
 3:  ('Актобе (кредит ИП)', '2. Актюбинская область', 'Договор  кредита (для ИП).docx'),
 4:  ('Актобе (кредит СПК)', '2. Актюбинская область', 'Договор кредита (для СПК).docx'),
 11: ('Алматы (кредит ИП)', '3. Алматинская область', 'Ф-08.1-П-57-25. Дог.кредита ИП.docx'),
 12: ('Алматы (кредит СПК)', '3. Алматинская область', 'Ф-08.2-П-57-25 . Дог.кредита СПК.docx'),
 15: ('Атырау', '4. Атырауская область', 'Договор займа ауыламанаты.doc'),
 19: ('ВКО', '5. Восточно-Казахстанская область', 'договор займа.docx'),
 22: ('Жамбыл', '6. Жамбылская область', 'ДК ИП.doc'),
 24: ('ЗКО (Прил. 2)', '7. Западно-Казахстанская область', 'Приложения Договора ++25.09.26++.docx — Приложение №2'),
 25: ('Караганда', '8. Карагандинская область', 'ЗАЙМ №2026-СПК-АА-2.docx'),
 30: ('Костанай', '9. Костанайская область', 'Приложение 12_Договор о предоставлении микрокредита.docx'),
 37: ('Кызылорда', '10. Кызылординская область', 'Приложение 2.docx'),
 47: ('Абай', '12. Область Абай', 'договор займа.docx'),
 48: ('Жетісу (заем СПК)', '13. Область Жетісу', 'Договор займа с СПК.docx'),
 49: ('Жетісу (заем)', '13. Область Жетісу', 'Договор займа.docx'),
 53: ('Ұлытау', '14. Область Ұлытау', 'КД Балмұқан Әлімжан Батырбекұлы (КХ Балмұқан).docx'),
 55: ('Павлодар', '15. Павлодарская область', 'Шаблон Договор займа Павлодар.docx'),
 58: ('СКО', '16. Северо-Казахстанская область', 'договор займа (с переводом УСХ).docx'),
 61: ('Туркестан (ДПМ)', '17. Туркестанская область', 'Договор залог, ДПМ и договор гарантии.doc — часть «ДПМ»'),
}
# Как регион уже мог быть подписан рядом с номером (чтобы не дублировать)
ALIAS = r'(?:\s+(?:Акмола|Актобе(?:\s+(?:ИП|СПК))?|Алматы(?:\s+(?:ИП|СПК))?|Атырау|ВКО|Жамбыл|ЗКО(?:,\s*Прил\.\s?2)?|Караганда|Костанай|Кызылорда|Абай|Жетісу(?:\s+СПК)?|Ұлытау|Павлодар|СКО|Туркестан(?:,\s*ДПМ)?))?'
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

d = json.load(open('d1_draft.json'))
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
d['intro'] = [t.replace('№2, 3, 4, 11, 12, 15, 19, 22, 24 (Прил. 2), 25, 30, 37, 47, 48, 49, 53, 55, 58, 61 (ДПМ). Номера — по реестру 01_реестр.xlsx.', 'список источников — в таблице ниже.') for t in d['intro']]
d['intro'] = [t.replace('договорах Атырау (№15) или Туркестана (№61)', 'договорах Атырау или Туркестана') for t in d['intro']]
json.dump(d, open('d1_draft_labeled.json', 'w'), ensure_ascii=False, indent=1)
left = sorted({m for c in d['clauses'] for s in [c.get('text_source') or '', c.get('note') or ''] + [x for v in c.get('variants') or [] for x in v['sources']] + (c.get('present_in') or []) for m in re.findall(r'.{0,25}№\s?\d{1,2}\b', s) if not re.search(r'(вопрос\w*(?:\s+реестра)?|Приложени\w*|этап \d —)\s*(?:\(|:)?\s*№', m)})
print('clauses', len(d['clauses']), '| осталось «№..» в комментариях:', len(left)); print('\n'.join(left[:25]))
