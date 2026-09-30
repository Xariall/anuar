import json,sys
P='/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_z2a.json'
R='7. Западно-Казахстанская область/договора/Приложения Договора ++25.09.26++.docx'
def add(part, rows, key='items'):
    d=json.load(open(P)); 
    for r in rows:
        if key=='items':
            topic,summ,ref,q=r
            d[0]['items'].append({"part":part,"topic":topic,"summary":summ,"ref":R+", "+ref,"quote":q})
        else:
            d[0][key].append(r)
    json.dump(d,open(P,'w'),ensure_ascii=False,indent=1)
