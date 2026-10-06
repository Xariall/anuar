# Лизинг, строго по словам Анура (06.10.2026):
# «оставляешь все пункты, у кого у всех; где варианты есть — оставляешь тот, у кого много;
#  если у всех по одному региону — как чувствует сердце».
# Правила: обычный пункт остаётся только если он есть у всех трёх регионов; в вариантах — вариант большинства
# регионов (если у большинства положения нет — пункт убирается); при равенстве — редакция Костаная
# (самый новый шаблон), затем Туркестана, затем ЗКО. Служебный текст (поля, реквизиты) остаётся.
import json, re
d = json.load(open('l1_reader.json'))
PREF = ['Костанай', 'Туркестан', 'ЗКО']

def var_regions(comment, j):
    for line in comment:
        m = re.match(rf'Вариант {j + 1}(?: \(положения нет\))? — (.*)$', line)
        if m: return [r.strip() for r in m.group(1).split(',') if r.strip() in PREF]
    return []

out, log = [], {'kept_all': 0, 'dropped_partial': 0, 'variant_chosen': [], 'variant_dropped_absent': [], 'tie_by_preference': []}
for c in d['clauses']:
    if c['kind'] == 'heading' or (not c.get('variants') and not c.get('level')):
        if c['kind'] == 'heading' or (c.get('text') or '').strip():
            out.append(c)
        continue
    if c.get('variants'):
        cand = [(j, var_regions(c['comment'], j)) for j in range(len(c['variants']))]
        best = max(len(r) for _, r in cand)
        top = [(j, r) for j, r in cand if len(r) == best]
        if len(top) > 1:
            top.sort(key=lambda x: min(PREF.index(r) for r in x[1]) if x[1] else 9)
            log['tie_by_preference'].append(c['id'] or '(без №)')
        j, regs = top[0]; v = c['variants'][j]
        if not v.get('text'):
            log['variant_dropped_absent'].append(c['id'] or '(без №)'); continue
        others = [', '.join(r) for k, r in cand if k != j and r]
        reason = 'у большинства регионов' if len(top) == 1 else 'у каждой редакции по одному региону — выбрана редакция ' + regs[0]
        out.append({'id': c['id'], 'kind': 'clause', 'text': v['text'], 'level': 'all' if len(regs) == 3 else ('some' if len(regs) == 2 else 'one'),
                    'comment': [f'Выбрана редакция: {", ".join(regs)} ({reason})'] + ([f'Другие редакции были у: {"; ".join(others)}'] if others else [])})
        log['variant_chosen'].append(c['id'] or '(без №)'); continue
    if c['level'] == 'all':
        out.append(c); log['kept_all'] += 1
    else:
        log['dropped_partial'] += 1

# убрать заголовки, после которых до следующего заголовка не осталось пунктов
clean = []
for k, c in enumerate(out):
    if c['kind'] == 'heading':
        nxt = next((x for x in out[k + 1:] if x['kind'] == 'heading' or x.get('level') or x.get('variants') or (x.get('text') or '').strip()), None)
        if nxt is None or nxt['kind'] == 'heading':
            continue
    clean.append(c)
n = 0
for c in clean:  # единый вид заголовков разделов: «N. НАЗВАНИЕ», номера по порядку
    if c['kind'] == 'heading':
        t = re.sub(r'^(Раздел\s+)?\d+\.\s*', '', (c.get('text') or '').strip())
        if t.upper().startswith('ПРИЛОЖЕНИЯ'):
            c['text'] = t.upper(); continue
        n += 1; c['text'] = f'{n}. {t.upper()}'
d['clauses'] = clean
json.dump(d, open('l1_reader_strict.json', 'w'), ensure_ascii=False, indent=1)
json.dump(log, open('l1_strict_log.json', 'w'), ensure_ascii=False, indent=1)
print({k: (v if isinstance(v, int) else len(v)) for k, v in log.items()}, '| пунктов в итоге:', sum(1 for c in clean if c['kind'] != 'heading'))
