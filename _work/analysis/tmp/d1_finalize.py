# Применение решений заказчика (30.09.2026) к классификации пунктов черновика займа
# К1: разные значения параметра -> оранжевый; К2: отсутствие не более чем в 2 договорах -> зелёный/жёлтый;
# К3: положения только №15/№61 -> синий; D1–D16: ответы о смысловой эквивалентности.
import json, re, sys
PENDING = set(sys.argv[1:])  # номера D, по которым ответ ещё уточняется, например D8 D10 D15

# Ответ заказчика по каждому сомнению: 'same' — один смысл, 'open' — оставить открытым (красный), 'blue' — пояснение/региональное
ANSWERS = {'1.7':'same','2.12':'same','4.10':'same','6.2.2.2':'same','6.2.7':'same','6.6.6':'same',
           '6.6.12':'open','6.7.10':'open','6.8.6':'same','6.9.1.2':'blue','7.3':'same','7.5.6':'same',
           '7.5.11':'same','9.2':'same','11.1':'same','11.3':'same','11.4':'same'}
DNUM = {'1.7':'D1','2.12':'D2','4.10':'D3','6.2.2.2':'D4','6.2.7':'D5','6.6.6':'D6','6.6.12':'D7','6.7.10':'D7',
        '6.8.6':'D8','6.9.1.2':'D9','7.3':'D10','7.5.6':'D11','7.5.11':'D12','9.2':'D13','11.1':'D14','11.3':'D15','11.4':'D16'}
TENTATIVE = {'D15','D16'}  # заказчик ответил неуверенно («Да?», «мне кажется»)

def n_absent(c):
    a = c.get('absent_in') or []
    if any(re.search(r'все|остальн|прочие', x) for x in a): return 99
    return len({m for x in a for m in re.findall(r'№\s?(\d+)', x)})
def weight(v): return sum(len(re.findall(r'№', s)) for s in v['sources'])

clauses = []
for i in range(1, 5):
    clauses += json.load(open(f'd1_part{i}.json'))['clauses']

stats = {}
for c in clauses:
    notes = []
    col = c['color']
    if col == 'doubt':
        d = DNUM.get(c['id']); ans = ANSWERS.get(c['id'])
        if d in PENDING or ans is None:
            col = 'red'; c['red_kind'] = 'conflict'
            notes.append(f'Смысловая эквивалентность уточняется у заказчика ({d}); до ответа — без выбора.')
        elif ans == 'open':
            col = 'red'; c['red_kind'] = 'conflict'
            notes.append(f'{d}: заказчик оставил вопрос открытым; выбор не сделан.')
        elif ans == 'blue':
            col = 'blue'; notes.append(f'{d}: заказчик подтвердил, что это пояснение к обязанности подтвердить целевое использование, а не иной способ.')
        else:
            col = 'yellow'
            notes.append(f'{d}: смысловая эквивалентность подтверждена заказчиком' + (' (ответ предварительный — стоит перепроверить юристу)' if d in TENTATIVE else '') + '.')
            if not c.get('text'):
                vs = sorted(c['variants'], key=weight, reverse=True); best = vs[0]
                c['text'] = best['text']; c['text_source'] = '; '.join(best['sources'])
                c['variants'] = [v for v in c['variants'] if v is not best]
                notes.append('Выбрана формулировка большинства договоров.')
    if col == 'red' and c.get('red_kind') == 'param':
        col = 'orange'
    if col in ('red', 'orange'):
        if c.get('text'):
            if not any(v['text'] == c['text'] for v in c.get('variants') or []):
                c.setdefault('variants', []).insert(0, {'text': c['text'], 'sources': [c.get('text_source') or '']})
            c['text'] = None
    if col in ('green', 'yellow', 'blue') and c.get('kind') == 'clause':
        na = n_absent(c)
        if na <= 2:
            new = 'yellow' if (c.get('variants') or col == 'yellow') else 'green'
            if new != col: notes.append(f'К2: нет только в {na} договор(ах) — отнесено к категории «{ "жёлтый" if new=="yellow" else "зелёный"}».')
            col = new
        elif col in ('green', 'yellow'):
            notes.append(f'К2: положения нет в {na if na < 99 else "многих"} договорах — отнесено к синему; варианты формулировки сохранены.')
            col = 'blue'
    c['color'] = col
    if notes: c['note'] = ((c.get('note') or '') + ' ' + ' '.join(notes)).strip()
    stats[col] = stats.get(col, 0) + 1

# Заголовки: единая нумерация разделов черновика (служебный текст, без цвета)
HFIX = {'ФОРС-МАЖОРНЫЕ ОБСТОЯТЕЛЬСТВА':'8. ФОРС-МАЖОРНЫЕ ОБСТОЯТЕЛЬСТВА','ПЕРЕУСТУПКА ПРАВ ТРЕБОВАНИЙ ПО ДОГОВОРУ':'9. ПЕРЕУСТУПКА ПРАВ ТРЕБОВАНИЙ ПО ДОГОВОРУ',
        'РАЗНОГЛАСИЯ И СПОРЫ СТОРОН':'10. РАЗНОГЛАСИЯ И СПОРЫ СТОРОН','ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ':'11. ДОПОЛНИТЕЛЬНЫЕ УСЛОВИЯ',
        'АНТИКОРРУПЦИОННАЯ ОГОВОРКА':'12. АНТИКОРРУПЦИОННАЯ ОГОВОРКА','АДРЕСА И РЕКВИЗИТЫ СТОРОН':'13. АДРЕСА И РЕКВИЗИТЫ СТОРОН',
        '6.8. Партнер имеет право:':'Партнер имеет право:'}
kept = []
for c in clauses:
    if c.get('kind') == 'heading':
        t = (c.get('text') or c.get('section') or '').strip()
        if t.startswith('применяемые в настоящем Договоре') and kept and kept[-1].get('kind') == 'heading':
            kept[-1]['text'] = (kept[-1].get('text') or '').rstrip(':') + ' ' + t; continue
        c['text'] = HFIX.get(t, t)
    kept.append(c)
clauses = kept

intro = [
  'Статус: рабочий черновик для команды (юрист, аналитик, руководитель). Собран из 19 договоров займа (кредита, микрокредита, бюджетного кредита) 16 регионов программы «Ауыл-Аманат»: №2, 3, 4, 11, 12, 15, 19, 22, 24 (Прил. 2), 25, 30, 37, 47, 48, 49, 53, 55, 58, 61 (ДПМ). Номера — по реестру 01_реестр.xlsx.',
  'Текст пунктов взят дословно из исходных договоров (русский текст). Конкретные данные сделок заменены полями [данные заемщика], [сумма], [дата]. Условия, которых нет в исходниках, не добавлялись.',
  'Правила маркировки согласованы с заказчиком 30.09.2026: положение, которого нет не более чем в двух договорах, считается общим (зелёный/жёлтый), в комментарии указано, где его нет; положения, которые есть только в договорах Атырау (№15) или Туркестана (№61), — синие; разные значения одного параметра — оранжевые.',
  'В красных и оранжевых пунктах приведены все варианты с источниками; правильный вариант не выбран. Номера вопросов реестра — в файле 02_вопросы_на_решение.xlsx.',
]
out = {'title': 'ЕДИНЫЙ ДОГОВОР ЗАЙМА (КРЕДИТА) — ЧЕРНОВИК', 'use_orange': True, 'intro': intro, 'clauses': clauses}
json.dump(out, open('d1_draft.json', 'w'), ensure_ascii=False, indent=1)
print(stats, 'pending:', sorted(PENDING))
