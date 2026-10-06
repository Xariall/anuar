# Указатель для 05_итог.md: по разделам 04_структура_<тип>.md — источники (№ реестра) и метки
import re, json
from build_matrix import DEF
KINDS=[('займ','Договор займа'),('залог','Договор залога'),('гарантия','Договор гарантии'),('поручение','Договор поручения'),('дкп','ДКП предмета лизинга'),('лизинг','Договор финансового лизинга')]
SKIP=('Вариативные блоки','Нерешённые','Проверка','Условные')
out={}
for k,name in KINDS:
    t=open(f'../04_структура_{k}.md').read()
    own={int(re.match(r'№(\d+)',c['label']).group(1)) for c in DEF[k]}|({36} if k=='поручение' else set())
    secs=re.split(r'(?m)^(?=## )',t)[1:]
    rows=[]
    for s in secs:
        h=s.split('\n',1)[0][3:].strip()
        if h.startswith(SKIP): continue
        s_c=re.sub(r'(вопрос\w*|реестр\w*)[^.;()\]\n]{0,40}?№\s?\d+(\s*(?:[–\-,]|и)\s*№?\s?\d+)*','',s)
        s_c=re.sub(r'№\s?\d+(\s*(?:[–\-,]|и)\s*№?\s?\d+)*\s+(?:реестра|этап)','',s_c)
        s_c=re.sub(r'(?i)(приложени\w*|приказ\w*|постановлени\w*|закон\w*|поручения|соглашени\w*|решени\w*|протокол\w*|ДКП|шарт\w*)\s*№\s?[\d\-–/.]+','',s_c)
        s_c=re.sub(r'№\s?0\d[\d\-–/]*','',s_c)
        nums=sorted({int(n) for n in re.findall(r'№\s?(\d{1,2})\b',s_c) if int(n) in own}, key=int)
        rows.append(dict(section=h,sources=nums,variants=s.count('[ВАРИАНТ'),regional=s.count('[РЕГИОНАЛЬНОЕ'),defects=s.count('[ДЕФЕКТ ИСТОЧНИКА')))
    tot=dict(variants=t.count('[ВАРИАНТ'),regional=t.count('[РЕГИОНАЛЬНОЕ'),defects=t.count('[ДЕФЕКТ ИСТОЧНИКА'),questions=sorted({int(x) for x in re.findall(r'вопрос\w*\s+№\s?(\d{1,3})',t)}))
    out[k]=dict(name=name,rows=rows,total=tot)
    print(name,len(rows),'разделов',tot['variants'],tot['regional'],tot['defects'],'вопросы:',len(tot['questions']))
json.dump(out,open('s5_index.json','w'),ensure_ascii=False,indent=1)
