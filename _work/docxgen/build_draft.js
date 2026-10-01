// Сборка черновика единого договора займа (кредита) в DOCX из d1_part*.json
// Запуск: node build_draft.js <вход.json> <выход.docx>
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ShadingType,
  CommentRangeStart, CommentRangeEnd, CommentReference, Table, TableRow, TableCell,
  WidthType, BorderStyle,
} = require('docx');

const [, , inPath, outPath] = process.argv;
const data = JSON.parse(fs.readFileSync(inPath, 'utf8'));

const COLORS = {
  green:  { fill: 'C6EFCE', label: 'Зелёный',  mark: 'З' },
  yellow: { fill: 'FFEB9C', label: 'Жёлтый',   mark: 'Ж' },
  blue:   { fill: 'BDD7EE', label: 'Синий',    mark: 'С' },
  orange: { fill: 'F8CBAD', label: 'Оранжевый', mark: 'О' },
  red:    { fill: 'FF9E9E', label: 'Красный',  mark: 'К' },
  none:   null,
};
const FONT = 'Times New Roman';
// Текст с переводами строк -> несколько TextRun с разрывом строки (\n в TextRun Word не отображает)
const runs = (text, opts = {}) => String(text).split(/\r?\n+/).map((t, i) => new TextRun({ text: t, font: FONT, size: 24, ...(i ? { break: 1 } : {}), ...opts }));
const run = (text, opts = {}) => runs(text, opts)[0];
const shade = (color) => (COLORS[color] ? { type: ShadingType.CLEAR, color: 'auto', fill: COLORS[color].fill } : undefined);

const comments = [];
function addComment(lines) {
  const id = comments.length;
  comments.push({
    id, author: 'Черновик (анализ)', initials: 'АН', date: new Date('2026-09-30T00:00:00Z'),
    children: lines.filter(Boolean).map((l) => new Paragraph({ children: [new TextRun({ text: l, size: 18 })] })),
  });
  return id;
}

function commentLines(c) {
  const L = [];
  const cat = COLORS[c.color] ? COLORS[c.color].label : 'Без выделения';
  L.push(`Пункт ${c.id} — ${cat}${c.red_kind ? ` (${c.red_kind === 'param' ? 'разные значения параметра' : 'противоречие'})` : ''}${c.block ? `; блок ${c.block}` : ''}`);
  if (c.text_source) L.push(`Текст взят: ${c.text_source}`);
  if (c.presence_summary) L.push(c.presence_summary);
  if (c.present_in && c.present_in.length) L.push(`Где в исходниках (регион, пункт): ${c.present_in.join('; ')}`);
  if (!c.presence_summary && c.absent_in && c.absent_in.length) L.push(`Нет в: ${c.absent_in.join(', ')}`);
  if (c.color === 'yellow' && c.variants && c.variants.length) {
    L.push('Региональные варианты формулировки (смысл тот же):');
    c.variants.forEach((v, i) => L.push(`  ${i + 1}) «${v.text}» — ${v.sources.join('; ')}`));
  }
  if (c.register_q && c.register_q.length) L.push(`Решение: вопрос(ы) реестра № ${c.register_q.join(', ')} (02_вопросы_на_решение.xlsx)`);
  if (c.note) L.push(`Примечание: ${c.note}`);
  return L;
}

function clauseParagraphs(c) {
  const out = [];
  const idRun = c.id && c.kind === 'clause' ? [run(`${c.id}. `, { bold: true })] : [];
  if (c.kind === 'heading') {
    out.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 },
      children: runs(c.text || c.section, { bold: true, size: 26 }) }));
    return out;
  }
  const cid = addComment(commentLines(c));
  if ((c.color === 'red' || c.color === 'orange') && (!c.text) && c.variants && c.variants.length) {
    out.push(new Paragraph({ spacing: { before: 60 }, children: [
      new CommentRangeStart(cid), ...idRun,
      run(`[ВАРИАНТЫ — выбор не сделан${c.register_q && c.register_q.length ? `; вопрос реестра № ${c.register_q.join(', ')}` : ''}]`, { italics: true, shading: shade(c.color) }),
    ] }));
    c.variants.forEach((v, i) => {
      const last = i === c.variants.length - 1;
      out.push(new Paragraph({ indent: { left: 360 }, spacing: { after: 60 }, children: [
        run(`Вариант ${i + 1} (${v.sources.join('; ')}): `, { bold: true, shading: shade(c.color) }),
        ...runs(v.text || '[положение отсутствует]', { shading: shade(c.color), italics: !v.text }),
        ...(last ? [new CommentRangeEnd(cid), new TextRun({ children: [new CommentReference(cid)] })] : []),
      ] }));
    });
    return out;
  }
  out.push(new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.JUSTIFIED, children: [
    new CommentRangeStart(cid), ...idRun,
    ...runs(c.text || '', { shading: shade(c.color) }),
    ...(c.color === 'yellow' && c.variants && c.variants.length ? [run(' [есть региональные варианты формулировки — см. комментарий]', { italics: true, size: 20, color: '7F6000' })] : []),
    new CommentRangeEnd(cid), new TextRun({ children: [new CommentReference(cid)] }),
  ] }));
  return out;
}

function legend() {
  const rows = [
    ['green', 'Положение есть во всех договорах, к которым применимо, и совпадает (практически дословно).'],
    ['yellow', 'Формулировки различаются, смысл одинаков. Для черновика выбрана одна формулировка, варианты — в комментарии.'],
    ['blue', 'Положение есть только в части регионов; может быть включено в единый договор.'],
    ...(data.use_orange ? [['orange', 'Одно положение, но разные значения параметра (срок, ставка, размер штрафа). Приведены все значения, выбор не сделан.']] : []),
    ['red', 'Положения существенно отличаются по смыслу или противоречат друг другу. Приведены все варианты, выбор не сделан.'],
    ['none', 'Без выделения — заголовки, поля для заполнения, реквизиты.'],
  ];
  const w = [2200, 7160];
  const border = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: w, rows: rows.map(([c, t]) => new TableRow({ children: [
    new TableCell({ width: { size: w[0], type: WidthType.DXA }, borders, shading: COLORS[c] ? { type: ShadingType.CLEAR, color: 'auto', fill: COLORS[c].fill } : undefined,
      children: [new Paragraph({ children: [run(COLORS[c] ? COLORS[c].label : 'Без выделения', { bold: true, size: 20 })] })] }),
    new TableCell({ width: { size: w[1], type: WidthType.DXA }, borders, children: [new Paragraph({ children: [run(t, { size: 20 })] })] }),
  ] })) });
}

function sourcesTable() {
  const w = [2400, 2900, 4060];
  const border = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
  const borders = { top: border, bottom: border, left: border, right: border };
  const cell = (t, i, bold) => new TableCell({ width: { size: w[i], type: WidthType.DXA }, borders,
    shading: bold ? { type: ShadingType.CLEAR, color: 'auto', fill: 'E7E6E6' } : undefined,
    children: [new Paragraph({ children: [run(t, { size: 18, bold })] })] });
  const rows = [new TableRow({ tableHeader: true, children: ['Краткое название (в комментариях)', 'Папка региона', 'Файл'].map((t, i) => cell(t, i, true)) })];
  (data.sources || []).forEach((s) => rows.push(new TableRow({ children: [cell(s.short, 0), cell(s.region, 1), cell(s.file, 2)] })));
  return new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: w, rows });
}

const body = [];
body.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [run('РАБОЧИЙ ЧЕРНОВИК — НЕ ЯВЛЯЕТСЯ ДОГОВОРОМ', { bold: true, color: 'C00000' })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [run(data.title || 'Единый договор займа (кредита)', { bold: true, size: 28 })] }));
(data.intro || []).forEach((t) => body.push(new Paragraph({ spacing: { after: 80 }, children: [run(t, { size: 20 })] })));
body.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [run('Цветовая маркировка', { bold: true })] }));
body.push(legend());
body.push(new Paragraph({ spacing: { before: 200, after: 60 }, children: [run('Исходные договоры', { bold: true })] }));
body.push(sourcesTable());
body.push(new Paragraph({ spacing: { after: 240 }, children: [run('Источник каждого пункта — в комментарии к нему: краткое название договора из этой таблицы и номер пункта в исходном файле.', { size: 20, italics: true })] }));
data.clauses.forEach((c) => clauseParagraphs(c).forEach((p) => body.push(p)));

const doc = new Document({
  creator: 'Анализ договоров Ауыл-Аманат', title: data.title || 'Черновик договора займа',
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  comments: { children: comments },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } }, children: body }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(outPath, b); console.log('ok', outPath, 'clauses', data.clauses.length, 'comments', comments.length); });
