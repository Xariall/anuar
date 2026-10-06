# Применение отметок Анура (файл «…v3.docx», 06.10.2026) к версии черновика займа для чтения.
# Зелёный — оставить; красный — удалить; без отметки — оставить пока.
# В пунктах с вариантами: оставить отмеченный зелёным вариант, остальные убрать; без отметок — все варианты остаются.
# Примечания Анура: «исключить» — 6.2.15, 6.2.16, 6.2.17.2, 6.2.20.1; «Оставляй целиком» — блок 6.11.
import json, re
from collections import defaultdict

d = json.load(open('d1_reader.json'))
marks = defaultdict(dict)
for i, j, m in json.load(open('an_marks.json')):
    marks[i][j] = m
EXCLUDE_BY_COMMENT = {'6.2.15', '6.2.16', '6.2.17.2', '6.2.20.1'}
KEEP_BLOCK = '6.11'

def regions_of(comment, j):
    for line in comment:
        m = re.match(rf'Вариант {j + 1}(?: \(положения нет\))? — (.*)$', line)
        if m: return m.group(1)
    return ''

out, log = [], {'kept_variant': [], 'deleted': [], 'unmarked_variants': [], 'excluded_by_comment': []}
for i, c in enumerate(d['clauses']):
    mk = marks.get(i, {})
    cid = c.get('id') or ''
    if c['kind'] != 'heading' and not c.get('variants') and not (c.get('text') or '').strip():
        continue  # служебные отсылки без текста — в версии для чтения не нужны
    in_block = cid == KEEP_BLOCK or cid.startswith(KEEP_BLOCK + '.')
    if cid in EXCLUDE_BY_COMMENT:
        log['excluded_by_comment'].append(cid); continue
    if c.get('variants'):
        vm = [mk.get(j, 'none') for j in range(len(c['variants']))]
        if all(m == 'red' for m in vm):
            log['deleted'].append(cid or c['variants'][0]['text'][:40]); continue
        if 'green' in vm:
            j = vm.index('green'); v = c['variants'][j]
            others = [regions_of(c['comment'], k) for k in range(len(c['variants'])) if k != j and vm[k] != 'red']
            out.append({'id': cid, 'kind': 'clause', 'text': v['text'], 'level': v['level'] or 'one',
                        'comment': [f'Выбрана редакция: {regions_of(c["comment"], j)}'] +
                                   ([f'Другие редакции были у: {"; ".join(o for o in others if o)}'] if others else [])})
            log['kept_variant'].append(cid or v['text'][:40]); continue
        log['unmarked_variants'].append(cid or c['variants'][0]['text'][:40])
        out.append(c); continue
    m = mk.get('head' if c['kind'] == 'heading' else None, 'none')
    if m == 'red' and not in_block:
        log['deleted'].append(cid or (c.get('text') or '')[:40]); continue
    out.append(c)

d['clauses'] = out
json.dump(d, open('d1_reader_v4.json', 'w'), ensure_ascii=False, indent=1)
json.dump(log, open('d1_anuar_log.json', 'w'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in log.items()}, '| пунктов в итоге:', sum(1 for c in out if c['kind'] != 'heading'))
