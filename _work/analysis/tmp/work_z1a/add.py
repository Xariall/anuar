import json,sys
P='/Users/asanaliesmagambetov/Documents/anuar/_work/analysis/tmp/s2_z1a.json'
F='7. Западно-Казахстанская область/договора/Приложения Договора ++25.09.26++.docx'
R='7. Западно-Казахстанская область/договора/Приложения Договора ++25.09.26++.txt'
PART='Приложение №2: договор займа/микрокредита'
def load():
    try: return json.load(open(P,encoding='utf-8'))
    except Exception:
        return [{"file":F,"reg_no":"№24","status":"шаблон (незаполненный, поля ____; приложение к отсутствующему Договору поручения)","items":[],"kk_divergences":[],"internal_contradictions":[],"residuals":[],"notes":""}]
def add(items=None,key='items',rows=None):
    d=load(); o=d[0]
    if key=='items':
        for t,s,r,q in items:
            o['items'].append({"part":PART,"topic":t,"summary":s,"ref":(R+", "+r) if r!='—' else '—',"quote":q})
    elif key=='notes': o['notes']=rows
    else: o[key]+=rows
    json.dump(d,open(P,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
