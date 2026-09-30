# -*- coding: utf-8 -*-
import json,re
t=open("/Users/asanaliesmagambetov/Documents/anuar/_work/text/7. Западно-Казахстанская область __ договора __ Приложения Договора ++25.09.26++.txt",encoding="utf-8").read()
n=lambda s:re.sub(r"\s+"," ",s).strip()
T=n(t)
d=json.load(open("../s2_z2b.json",encoding="utf-8"))
c=0
for i in d[0]["items"]:
    c+=1
    if i["quote"] and n(i["quote"]) not in T: print("BAD",i["topic"],i["quote"][:80])
print(c)
