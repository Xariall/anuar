import json,re
P='../s2_z2a.json'
d=json.load(open(P)); o=d[0]
o['kk_divergences']=[x for x in o['kk_divergences'] if not (x['ref_kk'].startswith('Приложение №3, п. 6.2') or x['ref_kk'].startswith('Приложение №3-1, п. 2.2.9'))]
for it in o['items']:
    if it['ref'].endswith(', —'): it['ref']='—'
txt=open('/Users/asanaliesmagambetov/Documents/anuar/_work/text/7. Западно-Казахстанская область __ договора __ Приложения Договора ++25.09.26++.txt').read()
n=lambda s:re.sub(r'\s+',' ',s).strip()
T=n(txt)
bad=[]
for i,it in enumerate(o['items']):
    q=it['quote']
    if q and n(q) not in T: bad.append((i,q))
print(len(o['items']),bad)
json.dump(d,open(P,'w'),ensure_ascii=False,indent=1)
