// Чистовая версия договора: без цветов, комментариев и пометок черновика.
// Нерешённые варианты (если остались) показываются списком «Требует выбора».
// Запуск: node build_clean.js <clean.json> <выход.docx>
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = require('docx');

const [, , inPath, outPath] = process.argv;
const data = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const FONT = 'Times New Roman';
const runs = (text, opts = {}) => String(text).split(/\r?\n+/).map((t, i) => new TextRun({ text: t, font: FONT, size: 24, ...(i ? { break: 1 } : {}), ...opts }));
const num = (c) => (c.id ? [new TextRun({ text: `${c.id}. `, font: FONT, size: 24, bold: true })] : []);

const body = [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 280 }, children: runs(data.title, { bold: true, size: 28 }) })];
for (const c of data.clauses) {
  if (c.kind === 'heading') {
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: runs(c.text || '', { bold: true, size: 26 }) }));
  } else if (c.variants) {
    body.push(new Paragraph({ spacing: { before: 60 }, children: [...num(c), new TextRun({ text: 'Требует выбора одной редакции:', font: FONT, size: 24, italics: true })] }));
    c.variants.forEach((v, i) => body.push(new Paragraph({ indent: { left: 360 }, spacing: { after: 60 }, alignment: AlignmentType.JUSTIFIED,
      children: [new TextRun({ text: `${i + 1}) `, font: FONT, size: 24 }), ...runs(v.text || 'положения нет', { italics: !v.text })] })));
  } else if ((c.text || '').trim()) {
    body.push(new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.JUSTIFIED, children: [...num(c), ...runs(c.text)] }));
  }
}
const doc = new Document({
  creator: 'Ауыл-Аманат', title: data.title,
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } }, children: body }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(outPath, b); console.log('ok', outPath); });
