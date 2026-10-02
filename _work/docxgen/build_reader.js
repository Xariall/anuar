// Черновик единого договора займа — версия «для чтения»: три цвета, короткие комментарии, сразу текст договора.
// Запуск: node build_reader.js <d1_reader.json> <выход.docx>
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ShadingType, Header,
  CommentRangeStart, CommentRangeEnd, CommentReference,
} = require('docx');

const [, , inPath, outPath] = process.argv;
const data = JSON.parse(fs.readFileSync(inPath, 'utf8'));
const FONT = 'Times New Roman';
const FILL = { all: 'C6EFCE', some: 'FFEB9C', one: 'BDD7EE' };
const runs = (text, opts = {}) => String(text).split(/\r?\n+/).map((t, i) => new TextRun({ text: t, font: FONT, size: 24, ...(i ? { break: 1 } : {}), ...opts }));
const shade = (lv) => (FILL[lv] ? { type: ShadingType.CLEAR, color: 'auto', fill: FILL[lv] } : undefined);

const comments = [];
const addComment = (lines) => {
  const id = comments.length;
  comments.push({ id, author: 'Черновик', initials: 'Ч', date: new Date('2026-10-02T00:00:00Z'),
    children: lines.map((l) => new Paragraph({ children: [new TextRun({ text: l, size: 18 })] })) });
  return id;
};
const num = (c) => (c.id ? [new TextRun({ text: `${c.id}. `, font: FONT, size: 24, bold: true })] : []);

const body = [];
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: runs(data.title, { bold: true, size: 28 }) }));
body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 280 }, children: [
  new TextRun({ text: '  есть у всех регионов  ', font: FONT, size: 18, shading: shade('all') }), new TextRun({ text: '   ', size: 18 }),
  new TextRun({ text: '  у нескольких регионов  ', font: FONT, size: 18, shading: shade('some') }), new TextRun({ text: '   ', size: 18 }),
  new TextRun({ text: '  только у одного региона  ', font: FONT, size: 18, shading: shade('one') }),
] }));

for (const c of data.clauses) {
  if (c.kind === 'heading') {
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: runs(c.text || '', { bold: true, size: 26 }) }));
    continue;
  }
  if (c.variants) {
    const cid = addComment(c.comment);
    body.push(new Paragraph({ spacing: { before: 60 }, children: [new CommentRangeStart(cid), ...num(c),
      new TextRun({ text: 'Варианты (нужно выбрать один):', font: FONT, size: 24, italics: true })] }));
    c.variants.forEach((v, i) => {
      const last = i === c.variants.length - 1;
      body.push(new Paragraph({ indent: { left: 360 }, spacing: { after: 60 }, alignment: AlignmentType.JUSTIFIED, children: [
        new TextRun({ text: `Вариант ${i + 1}: `, font: FONT, size: 24, bold: true }),
        ...runs(v.text || 'положения нет', { shading: shade(v.level), italics: !v.text }),
        ...(last ? [new CommentRangeEnd(cid), new TextRun({ children: [new CommentReference(cid)] })] : []),
      ] }));
    });
    continue;
  }
  if (!c.level) { // служебный текст: поля, реквизиты — без цвета и комментария
    body.push(new Paragraph({ spacing: { after: 80 }, children: [...num(c), ...runs(c.text || '')] }));
    continue;
  }
  const cid = addComment(c.comment);
  body.push(new Paragraph({ spacing: { after: 80 }, alignment: AlignmentType.JUSTIFIED, children: [
    new CommentRangeStart(cid), ...num(c), ...runs(c.text || '', { shading: shade(c.level) }),
    new CommentRangeEnd(cid), new TextRun({ children: [new CommentReference(cid)] }),
  ] }));
}

const doc = new Document({
  creator: 'Черновик', title: data.title,
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  comments: { children: comments },
  sections: [{
    properties: { page: { margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: 'Черновик — для обсуждения', font: FONT, size: 16, color: '808080' })] })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(outPath, b); console.log('ok', outPath, 'comments', comments.length); });
