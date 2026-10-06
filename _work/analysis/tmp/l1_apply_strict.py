# Лизинг, строго по словам Анура (06.10.2026):
# «оставляешь все пункты, у кого у всех; где варианты есть — оставляешь тот, у кого много;
#  если у всех по одному региону — как чувствует сердце».
# Правила: обычный пункт остаётся только если он есть у всех трёх регионов; в вариантах — вариант большинства
# регионов (если у большинства положения нет — пункт убирается); при равенстве — редакция Костаная
# (самый новый шаблон), затем Туркестана, затем ЗКО. Служебный текст (поля, реквизиты) остаётся.
# Запуск с аргументом «anuar» дополнительно применяет отметки Ануара из файла «…лизинга v3.docx» (06.10.2026)
# и пишет l1_reader_anuar.json; без аргумента — прежняя версия 2 (l1_reader_strict.json).
import json, re, sys
ANUAR = len(sys.argv) > 1 and sys.argv[1] == 'anuar'
d = json.load(open('l1_reader.json'))
# Ответы Ануара на комментарии черновика: преамбула — две редакции (вариант 2 — без партнёра,
# вариант 3 — с партнёром-ТОО, отмечен зелёным); 1.1.1 — «исключить»; 1.1 и 1.2 — «оставить».
KEEP_VARIANTS = {'Вариант 1 — Костанай|Вариант 2 — ЗКО|Вариант 3 — Туркестан': [1, 2]} if ANUAR else {}
EXCLUDE = {'1.1.1'} if ANUAR else set()
KEEP = {'1.1', '1.2'} if ANUAR else set()
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
    if c.get('id') in EXCLUDE:
        log.setdefault('anuar', []).append('исключён ' + c['id']); continue
    if c.get('id') in KEEP:
        out.append(c); log.setdefault('anuar', []).append('оставлен ' + c['id']); continue
    key = '|'.join(l for l in c.get('comment', []) if l.startswith('Вариант'))
    if c.get('variants') and not c.get('id') and key in KEEP_VARIANTS:
        out.append(dict(c, variants=[c['variants'][j] for j in KEEP_VARIANTS[key]]))
        log.setdefault('anuar', []).append('преамбула: две редакции'); continue
    if c.get('variants'):
        cand = [(j, var_regions(c['comment'], j)) for j in range(len(c['variants']))]
        best = max(len(r) for _, r in cand)
        top = [(j, r) for j, r in cand if len(r) == best]
        if len(top) > 1:
            top.sort(key=lambda x: min(PREF.index(r) for r in x[1]) if x[1] else 9)
            log['tie_by_preference'].append(c['id'] or '(без №)')
        j, regs = top[0]; v = c['variants'][j]
        if not v.get('text') or v['text'].strip() == '[не предусмотрено]':  # пометка «у региона пункта нет»
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
for k, c in enumerate(clean):  # единый вид заголовков разделов: «N. НАЗВАНИЕ», N — исходный номер раздела (по его пунктам)
    if c['kind'] == 'heading':
        t = re.sub(r'^(Раздел\s+)?\d+\.\s*', '', (c.get('text') or '').strip())
        if t.upper().startswith('ПРИЛОЖЕНИЯ'):
            c['text'] = t.upper(); continue
        first = next((x.get('id') for x in clean[k + 1:] if x.get('id')), None)
        c['text'] = f'{first.split(".")[0]}. {t.upper()}'
d['clauses'] = clean
suffix = 'anuar' if ANUAR else 'strict'
json.dump(d, open(f'l1_reader_{suffix}.json', 'w'), ensure_ascii=False, indent=1)
json.dump(log, open(f'l1_{suffix}_log.json', 'w'), ensure_ascii=False, indent=1)
print({k: (v if isinstance(v, int) else len(v)) for k, v in log.items()}, '| пунктов в итоге:', sum(1 for c in clean if c['kind'] != 'heading'))
