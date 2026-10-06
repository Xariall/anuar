import json, glob, re, os, sys, unicodedata
NF=lambda x: unicodedata.normalize('NFC',x)
TXT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','text')+'/'
def norm(s):
    s=s.replace(' ',' ').replace('«','"').replace('»','"').replace('“','"').replace('”','"').replace('—','-').replace('–','-')
    return re.sub(r'\s+',' ',s).strip().lower()
texts={}
for f in os.listdir(TXT):
    texts[NF(f)]=norm(open(TXT+f,encoding='utf-8',errors='ignore').read())
def find_txt(path):
    # path relative: "<region>/<sub>/<name.ext>"
    path=NF(path); parts=path.split('/'); reg,sub,name=parts[0],parts[1] if len(parts)>2 else '',parts[-1]
    base=os.path.splitext(name)[0]
    cand=[k for k in texts if k.startswith(reg+' __') and k.endswith(' __ '+base+'.txt')]
    return cand
def check(fn):
    d=json.load(open(fn)); out=[]
    for obj in d:
        c=find_txt(obj['file'])
        if not c: out.append((obj['file'],'NO TXT',0,0,0)); continue
        own=texts[c[0]]; tot=bad=foreign=0
        for it in obj.get('items',[]):
            q=it.get('quote','')
            if not q or it.get('summary')=='отсутствует': continue
            tot+=1
            if norm(q) not in own:
                bad+=1
                if any(norm(q) in t for k,t in texts.items() if k!=c[0]): foreign+=1
        out.append((obj['file'][:60],obj.get('reg_no'),tot,bad,foreign))
    return out
if __name__=='__main__':
    for fn in sorted(glob.glob('s2_*.json')):
        for r in check(fn): print(fn,r)
