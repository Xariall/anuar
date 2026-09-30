import json,sys
P='/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_n65.json'
F="17. Туркестанская область/договара/ФИН ЛИЗИНГ Ауыл-Аманат.doc"
def load():
    return json.load(open(P,encoding='utf-8'))
def save(d):
    json.dump(d,open(P,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
def items(lst):
    d=load()
    for t,s,r,q in lst:
        d[0]['items'].append({"part":"Договор финансового лизинга","topic":t,"summary":s,"ref":F.rsplit('/',1)[0]+'/'+F.rsplit('/',1)[1].replace('.doc','.doc')+", "+r if False else "17. Туркестанская область/договара/ФИН ЛИЗИНГ Ауыл-Аманат.doc, "+r,"quote":q})
    save(d)
def field(k,v):
    d=load(); d[0][k].extend(v) if isinstance(d[0][k],list) else d[0].__setitem__(k,v); save(d)
