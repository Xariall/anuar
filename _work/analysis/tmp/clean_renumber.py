# Чистовая версия: перенумерация пунктов подряд с сохранением иерархии (6.2.17 -> 6.2.12 и т. п.).
# Номер в заголовке («6.1. Заемщик имеет право:») тоже перенумеровывается.
# Запуск: python3 clean_renumber.py <вход reader.json> <выход clean.json>
import json, re, sys

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))
HEAD_NUM = re.compile(r'^\s*(\d+(?:\.\d+)*)\.?\s+')

def parts(num):
    # «7.4-1» -> ['7', '4-1'] (отдельный соседний пункт); «6.2.13-Б2» -> ['6','2','13-Б2']
    return [p for p in num.split('.') if p]

new_of = {}      # (новый путь родителя, исходная часть) -> новый номер
counter = {}     # новый путь родителя -> последний номер
def renum(path):
    out = []
    for p in path:
        parent = tuple(out); key = (parent, p)
        if key not in new_of:
            counter[parent] = counter.get(parent, 0) + 1
            new_of[key] = str(counter[parent])
        out.append(new_of[key])
    return '.'.join(out)

for c in d['clauses']:
    if c['kind'] == 'heading':
        m = HEAD_NUM.match(c.get('text') or '')
        if m:
            c['text'] = renum(parts(m.group(1))) + '. ' + c['text'][m.end():]
    elif c.get('id'):
        c['id'] = renum(parts(c['id']))
json.dump(d, open(dst, 'w'), ensure_ascii=False, indent=1)
print('ok', dst, sum(1 for c in d['clauses'] if c.get('id')), 'пунктов с номером')
