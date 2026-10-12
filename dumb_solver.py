"""
dumb_solver.py — '바보 풀이기' (교수님 4주차 피드백 ⑤)
정답을 보지 않고, 문제+선지 단어가 본문의 한 문장과 얼마나 겹치는지만 보고 답을 고른다.
이 풀이기가 맞히면 = 이해 없이 단어 찾기로 풀릴 수 있는 문항 '후보'.
(최종 판정은 교사. 이 결과는 보조 지표)

실행:  python dumb_solver.py outputs/20261005_1336 data/chapter01.txt
결과:  같은 폴더에 dumb_solver.csv, dumb_solver_summary.txt
"""
import json, re, sys, csv
from pathlib import Path

STOP = set("""a an the and or but if of to in on at for with by from is are was were be been being
do does did have has had he she it they we you i his her its their our your him them me my
that this these those what which who whom why how when where not no so as up out""".split())

def words(s):
    return [w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP]

def sentences(text):
    return [s for s in re.split(r"(?<=[.!?\"”])\s+", text) if s.strip()]

def score(q, opt, sents):
    """문제+선지 단어 중 본문 한 문장에 들어 있는 비율의 최댓값"""
    qa = set(words(q)) | set(words(opt))
    if not qa: return 0.0
    return max(len(qa & set(words(s))) / len(qa) for s in sents)

def strip_letter(o):
    return re.sub(r"^[A-D][\.\)]?\s+", "", o)

def main(run_dir, chapter_path):
    run = Path(run_dir)
    sents = sentences(Path(chapter_path).read_text(encoding="utf-8"))
    rows, summary = [], {}
    for f in sorted(run.glob("*_[0-9].json")):
        cond, rep = f.stem.rsplit("_", 1)
        for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
            if it.get("type") != "mc" or "answer" not in it: continue
            opts = it["options"]
            sc = [score(it["question"], strip_letter(o), sents) for o in opts]
            best = max(sc)
            picks = [i for i, s in enumerate(sc) if s == best]
            pick = "ABCD"[picks[0]] if len(picks) == 1 else "동점"
            correct = it["answer"].strip()[:1]
            hit = pick == correct
            rows.append([cond, rep, it["id"], pick, correct, "맞힘" if hit else "못맞힘",
                         " / ".join(f"{'ABCD'[i]}={s:.2f}" for i, s in enumerate(sc))])
            s = summary.setdefault(cond, [0, 0]); s[0] += hit; s[1] += 1
    with open(run / "dumb_solver.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["condition", "repeat", "item", "풀이기_선택", "정답", "결과", "선지별 겹침점수"])
        w.writerows(rows)
    lines = ["바보 풀이기 결과 (객관식만, 정답을 보지 않고 본문 겹침만으로 선택)", ""]
    for c in sorted(summary):
        h, n = summary[c]
        lines.append(f"{c}: {h}/{n} 맞힘  (우연 기대값 {n/4:.2f})")
    (run / "dumb_solver_summary.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
