"""원서 텍스트의 어휘 프로필: 교육부 3층 어디에 속하는지 집계"""
import re, sys, json
from collections import Counter
from lemma import lemmatize, lemmatize_compound
tier = json.load(open("moe_tier.json", encoding="utf-8"))
allv = set(tier)
EXCEPT = {"mr","mrs","ms","dr","oh","ah","wow","ouch","hey","d","c","ok"}  # 호칭·감탄사 등 교육부 예외
raw = open(sys.argv[1], encoding="utf-8").read()
# 제목·저자·챕터 제목 줄(첫 빈 줄 이전)은 분석에서 제외
text = raw.split("\n\n", 1)[1] if "\n\n" in raw else raw
tokens = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)
counts = Counter(t.lower() for t in tokens)
mid_caps = set()
for m in re.finditer(r"[A-Za-z]+(?:'[A-Za-z]+)?", text):
    t = m.group()
    if t[0].isupper():
        before = text[:m.start()].rstrip()
        if before and before[-1] not in '.!?"\n' and not before.endswith("Chapter 1"):
            mid_caps.add(t.lower())
propers = {w for w in mid_caps if lemmatize(w, allv) not in allv}
result = {1:[],2:[],3:[],"out":[],"except":[]}
for w, n in counts.items():
    if w in EXCEPT: result["except"].append(w); continue
    lem = lemmatize(w, allv)
    if lem in allv: result[tier[lem]].append((w,lem,n))
    elif w in propers: result["except"].append(w)
    else:
        c, kind = lemmatize_compound(w, allv)
        if kind == "prefix": result[tier[c]].append((w, c, n))
        elif kind == "compound": result[max(tier[c[0]], tier[c[1]])].append((w, "+".join(c), n))
        else: result["out"].append((w,n))
tot = sum(len(v) for k,v in result.items() if k!="except")
print(f"총 토큰 {len(tokens)} / 고유 단어 {len(counts)} / 예외(고유명사·호칭) {len(result['except'])}")
print(f"초등 800 안: {len(result[1])} ({len(result[1])/tot:.0%})")
print(f"중고 공통(누적 2,000) 추가: {len(result[2])} ({len(result[2])/tot:.0%})")
print(f"고등 선택(누적 3,000) 추가: {len(result[3])} ({len(result[3])/tot:.0%})")
print(f"목록 밖: {len(result['out'])} ({len(result['out'])/tot:.0%})")
print("\n[중고 공통 단어]", ", ".join(sorted(f"{w}" for w,l,n in result[2])))
print("[고등 선택 단어]", ", ".join(sorted(f"{w}" for w,l,n in result[3])))
print("[목록 밖]", ", ".join(sorted(f"{w}({n})" for w,n in result["out"])))
print("[예외 처리]", ", ".join(sorted(result["except"])))
