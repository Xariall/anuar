# Версия черновика «для чтения» (замечания Анура, 02.10.2026):
# три цвета по числу регионов, где есть положение; короткий комментарий; без технических деталей.
# «У всех» — если положения нет не более чем у 2 регионов (правило К2). Регионы, а не договоры: всего 16.
import json, re

REGION = {2:'Акмола', 3:'Актобе', 4:'Актобе', 11:'Алматы', 12:'Алматы', 15:'Атырау', 19:'ВКО', 22:'Жамбыл',
          24:'ЗКО', 25:'Караганда', 30:'Костанай', 37:'Кызылорда', 47:'Абай', 48:'Жетісу', 49:'Жетісу',
          53:'Ұлытау', 55:'Павлодар', 58:'СКО', 61:'Туркестан'}
ORDER = ['Акмола','Актобе','Алматы','Атырау','ВКО','Жамбыл','ЗКО','Караганда','Костанай','Кызылорда','Абай','Жетісу','Ұлытау','Павлодар','СКО','Туркестан']
ALL = set(ORDER)
DROP = {'2.12', '2.6.3'}  # повторы: 2.12 = 6.1.2 (перенос платежа), 2.6.3 = 6.9.3.11 (гарантия Председателя СПК)
SKIP_CTX = re.compile(r'(вопрос\w*(?:\s+реестра)?|Приложени\w*|Прил\.|приказ\w*|поручения|этап\s?\d\s?[—–-])\s*(?:\(|:)?\s*$', re.I)

def regions(strings):
    out = set()
    for s in strings or []:
        for m in re.finditer(r'№\s?(\d{1,2})\b', s):
            if int(m.group(1)) in REGION and not SKIP_CTX.search(s[max(0, m.start()-40):m.start()]):
                out.add(REGION[int(m.group(1))])
    return out
def level(rs):
    if len(ALL - rs) <= 2: return 'all'
    if len(rs) == 1: return 'one'
    return 'some'
def names(rs): return ', '.join(r for r in ORDER if r in rs)
def describe(rs):
    lv = level(rs); miss = ALL - rs
    if lv == 'all': return 'Есть у всех регионов' + (f', кроме: {names(miss)}' if miss else '')
    if lv == 'one': return f'Есть только у: {names(rs)}'
    return f'Есть у {len(rs)} из 16 регионов: {names(rs)}'

d = json.load(open('d1_draft.json'))
out = []
for c in d['clauses']:
    if c['id'] in DROP: continue
    r = {'id': c['id'] if re.match(r'^\d', c['id'] or '') else '', 'kind': c['kind'], 'text': c.get('text')}
    if c['kind'] == 'heading' or c['color'] == 'none':
        r['level'] = None; out.append(r); continue
    if c['color'] in ('red', 'orange'):
        r['text'] = None; r['variants'] = []; lines = ['Регионы пишут по-разному — нужно выбрать один вариант.']
        for i, v in enumerate(c.get('variants') or [], 1):
            rs = regions(v['sources'])
            if not v.get('text'):
                r['variants'].append({'text': None, 'level': None}); lines.append(f'Вариант {i} (положения нет) — {names(rs) or "остальные регионы"}'); continue
            r['variants'].append({'text': v['text'], 'level': level(rs) if rs else 'one'})
            lines.append(f'Вариант {i} — {names(rs)}')
        r['comment'] = lines; out.append(r); continue
    if any(re.search(r'все|остальн|прочие', x) for x in c.get('present_in') or []):
        rs = ALL - regions(c.get('absent_in'))
    else:
        rs = regions((c.get('present_in') or []) + [c.get('text_source') or ''])
    r['level'] = level(rs); r['comment'] = [describe(rs)]
    out.append(r)

from collections import Counter
print(Counter(x.get('level') for x in out if x['kind'] != 'heading' and x.get('text') is not None),
      '| вариантных пунктов:', sum(1 for x in out if x.get('variants')))
json.dump({'title': 'Единый договор займа (кредита)', 'clauses': out}, open('d1_reader.json', 'w'), ensure_ascii=False, indent=1)
