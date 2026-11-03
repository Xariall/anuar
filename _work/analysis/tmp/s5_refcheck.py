# Выборочная проверка ссылок 04_структура_*.md: цитата «…» ищется в тексте того договора (№ реестра), на который ссылается
import re, json, random, sys, io
_o=sys.stdout; sys.stdout=io.StringIO()
import verify_quotes as vq
sys.stdout=_o
reg={r['№']:r['путь к файлу'] for r in json.load(open('registry.json'))}
def src_text(n):
    t=vq.find_txt(reg[n]); return vq.texts[t[0]] if t else None
random.seed(20260930)
res=[]
for k in ['займ','залог','гарантия','поручение','дкп','лизинг']:
    t=open(f'../04_структура_{k}.md').read()
    cand=[]
    for m in re.finditer(r'«([^«»\[\]]{50,220})»[^«\n]{0,40}?\(\s*№\s?(\d{1,2})[^)]*\)',t):
        q,n=m.group(1),int(m.group(2))
        if n in reg: cand.append((q,n,m.group(0)[len(q)+2:].strip()[:80]))
    for q,n,ref in random.sample(cand,2):
        st=src_text(n); ok=bool(st) and vq.norm(q) in st
        res.append((k,n,ref,q,ok))
for k,n,ref,q,ok in res: print(f'{k} | №{n} | {ref} | {"найдено дословно" if ok else "НЕ НАЙДЕНО"} | «{q[:120]}»')
json.dump([dict(type=k,n=n,ref=ref,quote=q,ok=ok) for k,n,ref,q,ok in res],open('s5_refcheck.json','w'),ensure_ascii=False,indent=1)
