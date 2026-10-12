"""
review.py — 고정된 B1 문항을 '별도 호출'로 검수·수정한다 (교수님 4주차 피드백 ③)

  - 4주차에 이미 만든 B1 문항(B1_1~3.json)은 그대로 두고, 새 호출로 검수만 시킨다.
  - 생성과 같은 모델(run_abc.py의 MODEL), 서술형 채점표는 넣지 않음 → 조건을 맞춤.
  - 같은 question_id에 [수정 전 → 검수 지적 → 수정 후]를 연결해 review_link.csv로 저장.

실행:  python review.py outputs/20261005_1336 data/chapter01.txt
결과:  outputs/20261005_1336/review/  안에
         B1R_1.json, B1R_2.json, B1R_3.json   (수정 후 문항 — 블라인드 평가에 넣을 것)
         review_raw_1.json ...                (검수기가 낸 원본 답)
         review_link.csv                      (수정 전 / 지적 / 결정 / 수정 후)
비용:  호출 3번 (B1 3회분)
"""
import json, sys, csv
from pathlib import Path
from run_abc import call, read, load_vocab, MODEL, LEVEL, ROOT

def main(run_dir, chapter_path):
    run = Path(run_dir)
    chapter = read(chapter_path)
    vocab_text = "\n".join(sorted(load_vocab()))
    template = read(ROOT / "prompts/prompt_review.md")
    out = run / "review"; out.mkdir(exist_ok=True)

    rows = []
    for rep in (1, 2, 3):
        src = json.loads(read(run / f"B1_{rep}.json"))
        items = src["items"]
        prompt = (template.replace("{{LEVEL}}", LEVEL).replace("{{VOCAB_LIST}}", vocab_text)
                  .replace("{{ITEMS_JSON}}", json.dumps(items, ensure_ascii=False, indent=1))
                  .replace("{{CHAPTER_TEXT}}", chapter))
        print(f"[{rep}/3] B1_{rep} 검수 중...")
        res = call(prompt)
        (out / f"review_raw_{rep}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

        rev = {r["id"]: r for r in res.get("reviews", [])}
        new_items = []
        for it in items:
            r = rev.get(it["id"], {})
            after = r.get("revised_item") if r.get("decision") == "revise" and r.get("revised_item") else it
            new_items.append(after)
            probs = r.get("problems", [])
            rows.append([rep, it["id"], it["type"],
                         json.dumps(it, ensure_ascii=False),
                         "; ".join(f"{p.get('check')}: {p.get('reason')}" for p in probs),
                         ", ".join(k for k, v in r.get("checks", {}).items() if v == "unsure"),
                         r.get("decision", "(응답 없음)"),
                         json.dumps(after, ensure_ascii=False) if after is not it else "(변경 없음)"])
        (out / f"B1R_{rep}.json").write_text(json.dumps({"items": new_items}, ensure_ascii=False, indent=2), encoding="utf-8")

    with open(out / "review_link.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["repeat", "question_id", "type", "수정 전", "검수 지적", "검수기가 '불확실'로 표시", "결정", "수정 후"])
        w.writerows(rows)
    (out / "review_info.txt").write_text(f"model={MODEL}\nsource={run}/B1_*.json\nrubric=none\n", encoding="utf-8")
    n_rev = sum(1 for r in rows if r[6] == "revise")
    print(f"완료 → {out}   (15문항 중 수정 {n_rev}개)")
    print("이 폴더를 그대로 두고 Claude에게 '검수 끝났어'라고 알려 주세요.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "outputs/20261005_1336",
         sys.argv[2] if len(sys.argv) > 2 else ROOT / "data/chapter01.txt")
