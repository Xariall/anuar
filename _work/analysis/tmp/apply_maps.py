import json, os, collections, sys
from build_matrix import TAX, build
def rebuild(kind):
    m=build(kind); tax=TAX[kind]
    mp=json.load(open(f'map_{kind}.json')) if os.path.exists(f'map_{kind}.json') else {}
    rows=collections.OrderedDict((t,{}) for t in tax); extra=collections.OrderedDict()
    for t,cells in m['rows'].items():
        new=t if t in tax else mp.get(t,t)
        tgt=rows if new in rows else extra
        for col,items in cells.items():
            tgt.setdefault(new,{}).setdefault(col,[]).extend(items)
    rows.update(extra)
    rows=collections.OrderedDict((k,v) for k,v in rows.items() if v)   # drop empty taxonomy rows? keep as absent below
    return dict(kind=kind,columns=m['columns'],rows=rows,tax=tax,mapped=bool(mp))
if __name__=='__main__':
    for k in sys.argv[1:]:
        r=rebuild(k); json.dump(r,open(f'matrix2_{k}.json','w'),ensure_ascii=False,indent=1)
        print(k,len(r['columns']),'cols',len(r['rows']),'rows mapped=',r['mapped'])
