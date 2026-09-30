# -*- coding: utf-8 -*-
import json,re
from add import *
t=open("/Users/asanaliesmagambetov/Documents/anuar/_work/text/7. Западно-Казахстанская область __ договора __ Приложения Договора ++25.09.26++.txt",encoding="utf-8").read()
n=lambda s:re.sub(r"\s+"," ",s.replace("​","")).strip()
T=n(t)
d=load()
bad=0
for i,it in enumerate(d[0]["items"]):
    q=it["quote"]
    if q and n(q) not in T:
        bad+=1;print(i,it["topic"],"|",q[:90])
    # refs quotes in «» inside ref
    m=re.findall(r"«([^»]+)»",it["ref"].split(", ",2)[-1]) if False else []
print("bad",bad)
b=0
for i,it in enumerate(d[0]["items"]):
    r=it["ref"]
    for m in re.findall(r"«(.+?)»(?=$|,)",r.split("docx, ",1)[-1]):
        m2=m.rstrip(" ")
        if n(m2) not in T:
            b+=1;print("REF",i,m2[:80])
print("badref",b)
