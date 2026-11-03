// Нулевая версия единого договора с интервьюером (БНС) в DOCX: цвета + примечания с вопросами команде
// Запуск: node build_bns_v0.js <v0.json> <выход.docx>
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ShadingType,
  CommentRangeStart, CommentRangeEnd, CommentReference, Table, TableRow, TableCell, WidthType, BorderStyle,
} = require('docx');

const [, , inPath, outPath] = process.argv;
const data = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const FONT = 'Times New Roman';
const COLORS = {
  yellow: { fill: 'FFEB9C', label: 'Жёлтый' },
  orange: { fill: 'F8CBAD', label: 'Оранжевый' },
  blue:   { fill: 'BDD7EE', label: 'Синий' },
};
const runs = (text, opts = {}) => String(text).split(/\r?\n+/).map((t, i) => new TextRun({ text: t, font: FONT, size: 24, ...(i ? { break: 1 } : {}), ...opts }));
const run = (text, opts = {}) => runs(text, opts)[0];
const shade = (c) => (COLORS[c] ? { type: ShadingType.CLEAR, color: 'auto', fill: COLORS[c].fill } : undefined);

const comments = [];
function addComment(lines) {
  const id = comments.length;
  comments.push({
    id, author: 'Версия 0 (анализ)', initials: 'В0', date: new Date('2026-11-03T00:00:00Z'),
    children: lines.filter(Boolean).map((l) => new Paragraph({ children: [new TextRun({ text: l, size: 18, bold: l.startsWith('❓') })] })),
  });
  return id;
}
const endC = (cid) => [new CommentRangeEnd(cid), new TextRun({ children: [new CommentReference(cid)] })];

function render(c) {
  if (c.kind === 'heading') return [new Paragraph({ heading: HeadingLevel.HEADING_2, alignment: AlignmentType.CENTER, spacing: { before: 240, after: 120 },
    children: runs(c.text, { bold: true, size: 24, color: '000000' }) })];
  if (c.kind === 'subhead') return [new Paragraph({ spacing: { before: 80, after: 60 }, children: [run(`${c.id}. `, { bold: true }), run(c.text, { bold: true })] })];
  const idRun = c.id ? [run(`${c.id}. `, { bold: true })] : [];
  const cid = c.comment && c.comment.filter(Boolean).length ? addComment(c.comment) : null;
  const start = cid !== null ? [new CommentRangeStart(cid)] : [];
  const end = cid !== null ? endC(cid) : [];
  if (c.variants) {
    const out = [new Paragraph({ spacing: { before: 60 }, children: [...start, ...idRun,
      run('[ВАРИАНТЫ — выбор не сделан, см. примечание]', { italics: true, shading: shade(c.color) })] })];
    c.variants.forEach((v, i) => out.push(new Paragraph({ indent: { left: 360 }, spacing: { after: 60 }, alignment: /\n/.test(v.text) ? AlignmentType.LEFT : AlignmentType.JUSTIFIED, children: [
      run(`Вариант ${i + 1} (${v.sources.join(', ')}): `, { bold: true, shading: shade(c.color) }),
      ...runs(v.text, { shading: shade(c.color) }),
      ...(i === c.variants.length - 1 ? end : []),
    ] })));
    return out;
  }
  const tag = c.color === 'blue' ? [run(' [есть не во всех договорах — см. примечание]', { italics: true, size: 20, color: '1F4E79' })]
    : c.color === 'yellow' ? [run(' [есть другие формулировки — см. примечание]', { italics: true, size: 20, color: '7F6000' })] : [];
  return [new Paragraph({ spacing: { after: 80 }, alignment: /\n/.test(c.text || '') ? AlignmentType.LEFT : AlignmentType.JUSTIFIED, children: [
    ...start, ...idRun, ...runs(c.text || '', { shading: shade(c.color) }), ...tag, ...end] })];
}

const border = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
const borders = { top: border, bottom: border, left: border, right: border };
function table(rows, w, headFill) {
  return new Table({ width: { size: w.reduce((a, b) => a + b), type: WidthType.DXA }, columnWidths: w, rows: rows.map((r, ri) => new TableRow({ children: r.map((t, i) => new TableCell({
    width: { size: w[i], type: WidthType.DXA }, borders,
    shading: (ri === 0 && headFill) ? { type: ShadingType.CLEAR, color: 'auto', fill: headFill } : (typeof t === 'object' && t.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: t.fill } : undefined),
    children: [new Paragraph({ children: [run(typeof t === 'object' ? t.text : t, { size: 20, bold: ri === 0 && !!headFill })] })] })) })) });
}

const body = [];
body.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [run('РАБОЧИЙ ЧЕРНОВИК (ВЕРСИЯ 0) — НЕ ЯВЛЯЕТСЯ ДОГОВОРОМ', { bold: true, color: 'C00000' })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [run(data.title, { bold: true, size: 28 })] }));
data.intro.forEach((t) => body.push(new Paragraph({ spacing: { after: 80 }, children: [run(t, { size: 20 })] })));
body.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [run('Цвета в тексте', { bold: true })] }));
body.push(table([
  ['Без выделения', 'Пункт одинаковый во всех 7 договорах.'],
  [{ text: 'Жёлтый', fill: COLORS.yellow.fill }, 'Формулировки немного различаются, смысл одинаков. В тексте — вариант большинства, остальные — в примечании.'],
  [{ text: 'Оранжевый', fill: COLORS.orange.fill }, 'В договорах разные условия (разные значения). Приведены все варианты, выбор не сделан.'],
  [{ text: 'Синий', fill: COLORS.blue.fill }, 'Пункт есть только в части договоров.'],
], [2200, 7160]));
body.push(new Paragraph({ spacing: { before: 200, after: 60 }, children: [run('Исходные договоры', { bold: true })] }));
body.push(table([['Код', 'Файл (_work/новые/исходники/)'], ...data.sources.map((s) => [s.short, s.file])], [2200, 7160], 'E7E6E6'));
body.push(new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, children: [run('ДОГОВОР № __', { bold: true })] }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [run('возмездного оказания услуг', { bold: true })] }));
data.clauses.forEach((c) => render(c).forEach((p) => body.push(p)));

const doc = new Document({
  creator: 'Анализ договоров БНС', title: data.title,
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  comments: { children: comments },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } }, children: body }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(outPath, b); console.log('ok', outPath, 'пунктов', data.clauses.length, 'примечаний', comments.length); });
