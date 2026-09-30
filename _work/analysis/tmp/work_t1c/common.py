import json,sys
OUT='/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_t1c.json'
R='17. Туркестанская область/договара/Договор залог, ДПМ и договор гарантии.doc'
P='ДПМ: бюджетный кредит'
def add(rows, key='items'):
    d=json.load(open(OUT))
    for r in rows:
        if key=='items':
            t,s,ref,q=r
            d[0]['items'].append({"part":P,"topic":t,"summary":s,"ref":(R+', '+ref) if ref!='—' else '—',"quote":q})
        else:
            d[0][key].append(r)
    json.dump(d,open(OUT,'w'),ensure_ascii=False,indent=1)
