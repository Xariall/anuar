# Проверка: каждая цитата «…» из analysis.json и questions.json есть хотя бы в одном тексте Н1–Н7
import json, re, glob
def n(s): return re.sub(r'[\s_]+', ' ', s.replace('ё','е')).strip().lower()
T = n(" ".join(open(f, encoding="utf-8").read() for f in glob.glob("../../text/Н*.txt")))
src = json.dumps(json.load(open("analysis.json")), ensure_ascii=False) + json.dumps(json.load(open("questions.json")), ensure_ascii=False)
qs = set(re.findall(r'«([^«»]{6,})»', src)); bad = []
for q in sorted(qs):
    parts = [p for p in re.split(r'\s*(?:…|\.\.\.|\[[^\]]*\])\s*', q) if len(p) > 3]
    if not all(n(p) in T for p in parts): bad.append(q)
print("цитат:", len(qs), "не найдено:", len(bad)); [print(" -", b[:150]) for b in bad]
