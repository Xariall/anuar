# Версия черновика «для чтения» (замечания Анура, 02.10.2026):
# три цвета по числу регионов, где есть положение; короткий комментарий; без технических деталей.
# Лизинг: договоров три (Костанай, Туркестан, ЗКО); «у всех» — строго все три региона.
import json, re

REGION = {32: 'Костанай', 65: 'Туркестан', 24: 'ЗКО'}
ORDER = ['Костанай', 'Туркестан', 'ЗКО']
ALL = set(ORDER)
DROP = set()
SKIP_CTX = re.compile(r'(вопрос\w*(?:\s+реестра)?|Приложени\w*|Прил\.|приказ\w*|поручения|этап\s?\d\s?[—–-])\s*(?:\(|:)?\s*$', re.I)

def regions(strings):
    out = set()
    for s in strings or []:
        for m in re.finditer(r'№\s?(\d{1,2})\b', s):
            if int(m.group(1)) in REGION and not SKIP_CTX.search(s[max(0, m.start()-40):m.start()]):
                out.add(REGION[int(m.group(1))])
    return out
def level(rs):
    if not (ALL - rs): return 'all'  # договоров три: «у всех» — строго все три региона
    if len(rs) == 1: return 'one'
    return 'some'
def names(rs): return ', '.join(r for r in ORDER if r in rs)
def describe(rs):
    lv = level(rs); miss = ALL - rs
    if lv == 'all': return 'Есть у всех регионов' + (f', кроме: {names(miss)}' if miss else '')
    if lv == 'one': return f'Есть только у: {names(rs)}'
    return f'Есть у {len(rs)} из 3 регионов: {names(rs)}'

d = json.load(open('l1_draft.json'))
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
json.dump({'title': 'Единый договор финансового лизинга', 'clauses': out}, open('l1_reader.json', 'w'), ensure_ascii=False, indent=1)
