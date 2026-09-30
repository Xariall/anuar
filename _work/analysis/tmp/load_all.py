import json, glob, unicodedata, collections
NF=lambda x: unicodedata.normalize('NFC',x)
SRC={}  # (path, part) -> obj
files=sorted(glob.glob('s2_*.json'))
skip={'s2_n12.json'}  # partial overwritten copy, correct one is n12_kredit_SPK_Almaty
def load():
    out=[]
    for fn in files:
        if fn in skip: continue
        for obj in json.load(open(fn)):
            obj['_src']=fn; obj['file']=NF(obj['file']); out.append(obj)
    return out
if __name__=='__main__':
    objs=load()
    print(len(objs))
    for o in objs:
        parts=collections.Counter(i.get('part','') for i in o.get('items',[]))
        print(o['_src'], o['file'].split('/')[-1][:50], len(o['items']), dict(parts) if len(parts)>1 or list(parts)!=[''] else '')
