import json, sys, os
from apply_maps import rebuild
CH=int(os.environ.get('CH','12'))
for kind in sys.argv[1:]:
    m=rebuild(kind); json.dump(m,open(f'matrix2_{kind}.json','w'),ensure_ascii=False,indent=1)
    rows=list(m['rows'].items()); cols=[c['label'] for c in m['columns']]
    n=0
    for i in range(0,len(rows),CH):
        chunk=rows[i:i+CH]; n+=1
        json.dump(dict(kind=kind,columns=cols,total_columns=len(cols),rows=[dict(row=t,cells={c:cells.get(c,'—') for c in cols}) for t,cells in chunk]),
                  open(f'chunk_{kind}_{n}.json','w'),ensure_ascii=False,indent=1)
    print(kind,len(rows),'rows',n,'chunks')
