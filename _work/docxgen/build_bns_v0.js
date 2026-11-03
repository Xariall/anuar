// Версия 0 единого договора с интервьюером (БНС) в DOCX: таблица «каз | рус», как в исходниках Н1/Н6/Н7
// Запуск: node build_bns_v0.js <v0.json> <выход.docx>
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, ShadingType, Table, TableRow, TableCell, WidthType, BorderStyle,
  CommentRangeStart, CommentRangeEnd, CommentReference, TableLayoutType,
} = require('docx');

const [, , inPath, outPath] = process.argv;
const data = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const FONT = 'Times New Roman';
const SIZE = 20;                                    // 10 пт (в исходниках 9,5 пт)
const W = [5495, 5528];                             // ширины колонок из исходника Н1
const FILL = { yellow: 'FFEB9C', orange: 'F8CBAD', blue: 'BDD7EE' };
const shade = (c) => (FILL[c] ? { type: ShadingType.CLEAR, color: 'auto', fill: FILL[c] } : undefined);
const runs = (text, o = {}) => String(text).split(/\r?\n/).map((t, i) => { const r = new TextRun({ text: t, font: FONT, size: SIZE, ...(i ? { break: 1 } : {}), ...o }); if (i) r.__brk = true; return r; });

const comments = [];
function addComment(lines) {
  const id = comments.length;
  comments.push({ id, author: 'Версия 0', initials: 'В0', date: new Date('2026-11-03T00:00:00Z'),
    children: lines.map((l) => new Paragraph({ children: [new TextRun({ text: l, size: 18 })] })) });
  return id;
}
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: none, bottom: none, left: none, right: none };
const P = (children, o = {}) => new Paragraph({ alignment: children.some((r) => r instanceof TextRun && r.__brk) ? AlignmentType.LEFT : AlignmentType.JUSTIFIED, spacing: { after: 40 }, children, ...o });
const cell = (paras, i, fill) => new TableCell({ width: { size: W[i], type: WidthType.DXA }, borders: noBorders,
  margins: { left: 80, right: 80 }, shading: fill ? { type: ShadingType.CLEAR, color: 'auto', fill } : undefined, children: paras });
const row = (l, r, fill) => new TableRow({ cantSplit: false, children: [cell(l, 0, fill), cell(r, 1, fill)] });

function clauseRows(c) {
  if (c.kind === 'heading') {
    const h = (t) => [P(runs(t, { bold: true }), { alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 } })];
    return [row(h(c.kz), h(c.ru))];
  }
  if (c.kind === 'subhead') return [row([P(runs(c.kz, { bold: true }))], [P(runs(c.ru, { bold: true }))])];
  if (c.kind === 'requisites') return data.requisites.map(([l, r]) => row([P(runs(l), { alignment: AlignmentType.LEFT })], [P(runs(r), { alignment: AlignmentType.LEFT })]));
  const id = c.id ? `${c.id}. ` : '';
  const cid = c.comment ? addComment(c.comment) : null;
  const mark = (inner) => (cid === null ? inner : [new CommentRangeStart(cid), ...inner, new CommentRangeEnd(cid), new TextRun({ children: [new CommentReference(cid)] })]);
  if (c.variants) {
    const out = [row([P([new TextRun({ text: id, bold: true, font: FONT, size: SIZE }), ...runs('[нұсқалар — таңдау жасалмаған]', { italics: true })])],
                     [P(mark([new TextRun({ text: id, bold: true, font: FONT, size: SIZE }), ...runs('[ВАРИАНТЫ — выбор не сделан]', { italics: true })]))])];
    c.variants.forEach((v, i) => out.push(row(
      [P([...runs(`${i + 1}-нұсқа (${v.forms}): `, { bold: true }), ...runs(v.kz)])],
      [P([...runs(`Вариант ${i + 1} (${v.forms}): `, { bold: true }), ...runs(v.ru)])], FILL[c.color])));
    return out;
  }
  const b = (t) => [new TextRun({ text: id, bold: true, font: FONT, size: SIZE }), ...runs(t)];
  return [row([P(b(c.kz))], [P(mark(b(c.ru)))], FILL[c.color])];
}

const head = [];
head.push(new Paragraph({ alignment: AlignmentType.CENTER, children: runs('РАБОЧИЙ ЧЕРНОВИК (ВЕРСИЯ 0) — НЕ ЯВЛЯЕТСЯ ДОГОВОРОМ', { bold: true, color: 'C00000' }) }));
data.intro.forEach((t) => head.push(new Paragraph({ spacing: { after: 40 }, children: runs(t, { size: 18 }) })));
head.push(new Paragraph({ spacing: { after: 160 }, children: [
  ...runs('Цвета: ', { size: 18, bold: true }), ...runs('без цвета — одинаково во всех 7;  ', { size: 18 }),
  ...runs(' жёлтый ', { size: 18, shading: shade('yellow') }), ...runs(' — формулировки чуть разные, взята редакция большинства;  ', { size: 18 }),
  ...runs(' оранжевый ', { size: 18, shading: shade('orange') }), ...runs(' — разные условия, все варианты;  ', { size: 18 }),
  ...runs(' синий ', { size: 18, shading: shade('blue') }), ...runs(' — пункт есть не во всех договорах.', { size: 18 }) ] }));

const rows = [row([P(runs('Өтеулі қызметтер көрсету туралы\nШАРТ № __', { bold: true }), { alignment: AlignmentType.CENTER })],
                  [P(runs('ДОГОВОР № __\nвозмездного оказания услуг', { bold: true }), { alignment: AlignmentType.CENTER })])];
data.clauses.forEach((c) => clauseRows(c).forEach((r) => rows.push(r)));
const table = new Table({ width: { size: W[0] + W[1], type: WidthType.DXA }, columnWidths: W, layout: TableLayoutType.FIXED, borders: { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none }, rows });

const doc = new Document({
  creator: 'Анализ договоров БНС', title: 'Договор с интервьюером — версия 0',
  styles: { default: { document: { run: { font: FONT, size: SIZE } } } },
  comments: { children: comments },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 964, right: 907, bottom: 850, left: 907 } } }, children: [...head, table] }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(outPath, b); console.log('ok', outPath, 'строк таблицы', rows.length, 'примечаний', comments.length); });
