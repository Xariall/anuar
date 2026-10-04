# Черновик договора финансового лизинга: те же правила, что для займа (К1 — оранжевый для разных значений параметра).
# Договоров три (Костанай, Туркестан, ЗКО), поэтому «общее» — только если положение есть во всех трёх (допуск К2 не применяется).
# К1: разные значения параметра -> оранжевый; К2: отсутствие не более чем в 2 договорах -> зелёный/жёлтый;
# К3: положения только №15/№61 -> синий; D1–D16: ответы о смысловой эквивалентности.
import json, re, sys
PENDING = set(sys.argv[1:])  # номера D, по которым ответ ещё уточняется, например D8 D10 D15

# Ответ заказчика по каждому сомнению: 'same' — один смысл, 'open' — оставить открытым (красный), 'blue' — пояснение/региональное
# Ответы заказчика по сомнениям (заполняются после вопросов): id пункта -> 'same' | 'open' | 'blue'
ANSWERS = json.load(open('l1_answers.json')) if __import__('os').path.exists('l1_answers.json') else {}
DNUM = {}
TENTATIVE = set()

def n_absent(c):
    a = c.get('absent_in') or []
    if any(re.search(r'все|остальн|прочие', x) for x in a): return 99
    return len({m for x in a for m in re.findall(r'№\s?(\d+)', x)})
def weight(v): return sum(len(re.findall(r'№', s)) for s in v['sources'])

clauses = []
for i in range(1, 3):
    clauses += json.load(open(f'l1_part{i}.json'))['clauses']

stats = {}
for c in clauses:
    notes = []
    col = c['color']
    if col == 'doubt':
        d = 'вопрос по п. ' + c['id']; ans = ANSWERS.get(c['id'])
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
                notes.append('Формулировку выбрал заказчик: «…действующих на момент досрочного погашения».' if d == 'D10' else 'Выбрана формулировка большинства договоров.')
    if col == 'red' and c.get('red_kind') == 'param':
        col = 'orange'
    if col in ('red', 'orange'):
        if c.get('text'):
            if not any(v['text'] == c['text'] for v in c.get('variants') or []):
                c.setdefault('variants', []).insert(0, {'text': c['text'], 'sources': [c.get('text_source') or '']})
            c['text'] = None
    if col in ('green', 'yellow', 'blue') and c.get('kind') == 'clause':
        na = n_absent(c)
        if na == 0:
            new = 'yellow' if (c.get('variants') or col == 'yellow') else 'green'
            if new != col: pass
            col = new
        elif col in ('green', 'yellow'):
            notes.append('Положения нет хотя бы в одном из трёх договоров — синий; варианты формулировки сохранены.')
            col = 'blue'
    c['color'] = col
    if notes: c['note'] = ((c.get('note') or '') + ' ' + ' '.join(notes)).strip()
    stats[col] = stats.get(col, 0) + 1


intro = [
  'Статус: рабочий черновик для команды (юрист, аналитик, руководитель). Собран из 3 договоров финансового лизинга программы «Ауыл-Аманат»: Костанай, Туркестан, ЗКО (Приложение №2-1); список источников — в таблице ниже.',
  'Текст пунктов взят дословно из исходных договоров (русский текст). Конкретные данные сделок заменены полями. Условия, которых нет в исходниках, не добавлялись.',
  'Маркировка — по правилам, согласованным для договора займа; так как договоров три, «общим» (зелёный/жёлтый) считается положение, которое есть во всех трёх. Разные значения одного параметра — оранжевые.',
  'В красных и оранжевых пунктах приведены все варианты с источниками; правильный вариант не выбран. Номера вопросов реестра — в файле 02_вопросы_на_решение.xlsx.',
]
out = {'title': 'ЕДИНЫЙ ДОГОВОР ФИНАНСОВОГО ЛИЗИНГА — ЧЕРНОВИК', 'use_orange': True, 'intro': intro, 'clauses': clauses}
json.dump(out, open('l1_draft.json', 'w'), ensure_ascii=False, indent=1)
print(stats, 'pending:', sorted(PENDING))
