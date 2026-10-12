"""
recount.py — 4주차 결과 다시 세기 (교수님 4주차 피드백 ①⑥)
조건별로 '생성된 문항 수'와 '서로 다른 문항 수'를 나눠 센다.
문제 문장이 거의 같으면(단어 80% 이상 겹침) 같은 문항으로 본다.

실행:  python recount.py outputs/20261005_1336
결과:  같은 폴더에 recount.md
"""
import json, re, sys
from pathlib import Path

def wset(s): return set(re.findall(r"[a-z]+", s.lower()))
def same(a, b):
    A, B = wset(a), wset(b)
    return len(A & B) / max(1, len(A | B)) >= 0.8

def main(run_dir):
    run = Path(run_dir)
    by = {}
    for f in sorted(run.glob("*_[0-9].json")):
        cond, rep = f.stem.rsplit("_", 1)
        for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
            by.setdefault(cond, []).append((int(rep), it))
    md = ["# 4주차 재집계", "",
          "| 조건 | 생성 문항 | 서로 다른 문항 | 객관식 생성 | 객관식 서로 다른 | 객관식 정답 위치(A/B/C/D) |",
          "|---|---|---|---|---|---|"]
    detail = []
    for c in sorted(by):
        items = by[c]
        uniq = []
        for rep, it in items:
            if not any(same(it["question"], u["question"]) for u in uniq): uniq.append(it)
        mc = [it for _, it in items if it["type"] == "mc"]
        mcu = [it for it in uniq if it["type"] == "mc"]
        ans = {k: sum(1 for it in mc if it.get("answer", "")[:1] == k) for k in "ABCD"}
        md.append(f"| {c} | {len(items)} | {len(uniq)} | {len(mc)} | {len(mcu)} | "
                  f"{ans['A']}/{ans['B']}/{ans['C']}/{ans['D']} |")
        detail += ["", f"## {c} — 문항 번호별 3회 비교", ""]
        for qid in range(1, 6):
            qs = [it["question"] for rep, it in items if it["id"] == qid]
            n = len({q for q in qs if not any(same(q, p) for p in qs[:qs.index(q)])})
            detail.append(f"- Q{qid}: 3회 중 서로 다른 문항 {n}개")
    md += ["", "※ '같은 문항' 기준: 문제 문장 단어 80% 이상 겹침 (코드 계산)"] + detail
    (run / "recount.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))

if __name__ == "__main__":
    main(sys.argv[1])
