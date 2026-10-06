# Чистовая версия: перенумерация пунктов подряд с сохранением иерархии (6.2.17 -> 6.2.12, 7.4-1 -> 7.5 и т. п.).
# Номер в заголовке («6.1. Заемщик имеет право:») тоже перенумеровывается.
# Ссылки в тексте («пунктом 4.3», «подпунктах 6.2.1., 6.2.2.») переводятся на новые номера;
# ссылки на номера, которых в документе нет, не меняются и выводятся списком.
# Запуск: python3 clean_renumber.py <вход reader.json> <выход clean.json>
import json, re, sys

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src))
HEAD_NUM = re.compile(r'^\s*(\d+(?:\.\d+)*)\.?\s+')
REF = re.compile(r'(?:пункт\w*|подпункт\w*|пп?\.)\s*((?:\d+(?:\.\d+)+\.?(?:\s*(?:,|и|-|–|—)\s*)?)+)')
NUM = re.compile(r'\d+(?:\.\d+)+')

def parts(num):
    return [p for p in num.strip().rstrip('.').split('.') if p]

new_of, counter, old2new = {}, {}, {}
def renum(path):
    out = []
    for p in path:
        parent = tuple(out); key = (parent, p)
        if key not in new_of:
            counter[parent] = counter.get(parent, 0) + 1
            new_of[key] = str(counter[parent])
        out.append(new_of[key])
    old2new['.'.join(path)] = '.'.join(out)
    return '.'.join(out)

for c in d['clauses']:
    if c['kind'] == 'heading':
        m = HEAD_NUM.match(c.get('text') or '')
        if m:
            c['text'] = renum(parts(m.group(1))) + '. ' + c['text'][m.end():]
    elif c.get('id'):
        c['id'] = renum(parts(c['id']))

unresolved, changed = [], []
def fix_refs(text, where):
    def one_ref(m):
        def one_num(n):
            old = n.group(0)
            if old in old2new:
                if old2new[old] != old: changed.append((where, old, old2new[old]))
                return old2new[old]
            unresolved.append((where, old)); return old
        return m.group(0)[:m.start(1) - m.start(0)] + NUM.sub(one_num, m.group(1))
    return REF.sub(one_ref, text)

for c in d['clauses']:
    if c.get('text'): c['text'] = fix_refs(c['text'], c.get('id'))
    for v in c.get('variants', []):
        if v.get('text'): v['text'] = fix_refs(v['text'], c.get('id'))

json.dump(d, open(dst, 'w'), ensure_ascii=False, indent=1)
print('ok', dst, sum(1 for c in d['clauses'] if c.get('id')), 'пунктов с номером')
print('ссылки изменены:', changed)
print('ссылки на отсутствующие пункты (не тронуты):', unresolved)
