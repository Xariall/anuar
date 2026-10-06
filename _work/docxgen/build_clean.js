// Чистовая версия договора: без цветов, комментариев и пометок.
// Невыбранные редакции даются в квадратных скобках через «/», как принято в шаблонах:
// первый пункт с вариантами (название договора) — заголовком по центру.
// Нумерация и ссылки — как в файле с отметками Ануара (не перенумеровываются).
// Запуск: node build_clean.js <d1_reader_v4.json> <выход.docx>
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, AlignmentType } = require('docx');

const [, , inPath, outPath] = process.argv;
const data = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const FONT = 'Times New Roman';
const runs = (text, opts = {}) => String(text).split(/\r?\n+/).map((t, i) => new TextRun({ text: t, font: FONT, size: 24, ...(i ? { break: 1 } : {}), ...opts }));
const num = (c) => (c.id ? [new TextRun({ text: `${c.id}. `, font: FONT, size: 24, bold: true })] : []);
const texts = (c) => c.variants.map((v) => v.text).filter((t) => t && t.trim());

const body = [];
let first = true;
for (const c of data.clauses) {
  if (c.kind === 'heading') {
    body.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 240, after: 120 }, children: runs(c.text || '', { bold: true }) }));
  } else if (c.variants) {
    const alts = texts(c);
    if (first && !c.id) { // название договора
      body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: runs(`[${alts.join(' / ')}]`, { bold: true, size: 28 }) }));
    } else {
      alts.forEach((t, i) => body.push(new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.JUSTIFIED,
        children: [...(i === 0 ? num(c) : []), ...runs(`[${t}]${i < alts.length - 1 ? ' /' : ''}`)] })));
    }
  } else if ((c.text || '').trim()) {
    body.push(new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.JUSTIFIED, children: [...num(c), ...runs(c.text)] }));
  }
  first = false;
}
const doc = new Document({
  creator: '', lastModifiedBy: '', title: '', description: '', revision: 1,
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  sections: [{ properties: { page: { margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } }, children: body }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(outPath, b); console.log('ok', outPath); });
