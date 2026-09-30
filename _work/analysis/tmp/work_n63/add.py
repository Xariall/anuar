import json,sys
P='/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_n63.json'
R='17. Туркестанская область/договара/Договор поставки Ауыл-Аманат.doc'
def load():
    try: return json.load(open(P))
    except Exception: return None
def save(d): json.dump(d,open(P,'w'),ensure_ascii=False,indent=1)
def add(rows, key='items'):
    d=load()
    for r in rows:
        if key=='items':
            t,s,ref,q=r
            d[0]['items'].append({"part":"","topic":t,"summary":s,"ref":R+', '+ref,"quote":q})
        else: d[0][key].append(r)
    save(d)
