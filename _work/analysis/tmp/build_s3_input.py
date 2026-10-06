# Подготовка входа для этапа 3: по каждой строке — где условие есть/нет, различия, противоречия
import json, glob
from apply_maps import rebuild
KINDS=['займ','залог','гарантия','поручение','дкп','лизинг']
def load_an(k):
    a={}
    for f in sorted(glob.glob(f'analysis_{k}_*.json')): a.update(json.load(open(f)))
    return a
def absent(items):
    return all(i['summary'].strip().lower().startswith('отсутств') for i in items)
if __name__=='__main__':
    for k in KINDS:
        m=rebuild(k); an=load_an(k); labels=[c['label'] for c in m['columns']]
        rows=[]
        for t,cells in m['rows'].items():
            has=[l for l in labels if l in cells and not absent(cells[l])]
            rows.append(dict(row=t,present_in=has,absent_in=[l for l in labels if l not in has],
                             различия=an.get(t,{}).get('различия',''),противоречия=an.get(t,{}).get('противоречия','')))
        json.dump(dict(kind=k,columns=m['columns'],rows=rows),open(f's3_input_{k}.json','w'),ensure_ascii=False,indent=1)
        print(k,len(rows))
