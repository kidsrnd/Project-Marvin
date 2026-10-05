"""
run_abc.py — 챕터 하나로 A / B1 / B2 문항을 같은 모델로 REPEATS번씩 만들어 비교한다.

  A  : 기본 생성 (규칙 없음)                       ← 기준선
  B1 : A + 생성 규칙 (선지는 본문 사건만, 어휘 제한, 짝맞추기 금지)
  B2 : B1 + 자기검수(근거·장면 일치·어휘·짝맞추기) + 서술형 채점표

실행:  python run_abc.py data/chapter01.txt
결과:  outputs/<날짜_시각>/  안에
         A_1.json, B1_1.json, B2_1.json, A_2.json, ...   (조건_반복번호)
         compare_1.md, compare_2.md, ...                  (반복별 3조건 나란히)
         eval_sheet.csv                                   (교사 평가·오류 유형 기록용, 빈 칸)
"""
import json, re, sys, datetime, csv
from pathlib import Path
import anthropic
from lemma import lemmatize, lemmatize_compound
from evidence import export as export_public   # 근거 위치 + 공개용 내보내기

MODEL = "claude-sonnet-4-6"           # 세 조건 모두 이 모델로 고정
LEVEL = "Pupa (Korean elementary, about grade 3-4)"
VOCAB_TIER = 2000                     # 허용 어휘 컷: 800 / 2000 / 3000
REPEATS = 3                           # 같은 조건을 몇 번 반복할지 (교수님 피드백: 한 번의 출력에 의존하지 않기)
CONDITIONS = ["A", "B1", "B2"]        # 돌릴 조건. 일부만 돌리려면 예: ["A", "B2"]
ROOT = Path(__file__).parent

# ---------- 파일 ----------
def read(path): return Path(path).read_text(encoding="utf-8")

def load_vocab():
    return {l.strip().lower() for l in read(ROOT / f"vocab/moe_{VOCAB_TIER}.txt").splitlines()
            if l.strip() and not l.startswith("#")}

def tokenize(text): return set(re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower()))

# ---------- 모델 호출 ----------
def call(prompt, tries=3):
    """모델을 부르고 JSON만 뽑아낸다. 앞뒤 설명 문장·코드 울타리는 버리고, 잘리면 다시 시도."""
    client = anthropic.Anthropic()
    last = ""
    for attempt in range(1, tries + 1):
        resp = client.messages.create(model=MODEL, max_tokens=8000,
                                      messages=[{"role": "user", "content": prompt}])
        last = resp.content[0].text
        a, b = last.find("{"), last.rfind("}")          # 첫 { 부터 마지막 } 까지만 JSON으로 취급
        if a >= 0 and b > a:
            try:
                return json.loads(last[a:b + 1])
            except json.JSONDecodeError:
                pass
        print(f"   (JSON 파싱 실패, 재시도 {attempt}/{tries}, stop_reason={resp.stop_reason})")
    Path(ROOT / "outputs" / "last_bad_response.txt").write_text(last, encoding="utf-8")
    raise RuntimeError("모델 출력을 JSON으로 읽지 못했습니다. outputs/last_bad_response.txt 를 확인하세요.")

# ---------- 어휘 초과 검사 (코드가 직접 셈) ----------
EXCEPT = {"mr","mrs","ms","dr","oh","ah","wow","hey","ok","okay"}

def item_text(it):
    opts = [re.sub(r"^[A-D][\.\)]?\s+", "", o) for o in it.get("options", [])]
    return " ".join([it.get("question", "")] + opts)

def vocab_over(items, vocab, chapter_words):
    out = {}
    for it in items:
        over = []
        for w in sorted(tokenize(item_text(it))):
            base = w[:-2] if w.endswith("'s") else w
            if base in EXCEPT or base in chapter_words: continue
            if lemmatize(w, vocab) in vocab: continue
            if lemmatize_compound(w, vocab)[1]: continue
            over.append(w)
        out[it["id"]] = over
    return out

def stem_len(it): return len(it.get("question", "").split())

# ---------- 비교표 ----------
def fmt(it):
    s = f"**Q{it['id']} ({it['type']})** {it['question']}  _(stem {stem_len(it)} words)_"
    for o in it.get("options", []): s += f"\n- {o}"
    for k, label in [("answer","정답"),("answer_location","위치"),("sample_answer","예시답")]:
        if k in it: s += f"\n- {label}: {it[k]}"
    if "rubric" in it:
        r = it["rubric"]
        s += f"\n- 핵심요소: {r.get('key_elements','')}\n- 근거위치: {r.get('accepted_evidence_locations','')}"
        s += f"\n- 4점 예: {r.get('example_4pt','')}\n- 2점 예: {r.get('example_2pt','')}\n- 0점 예: {r.get('example_0pt','')}"
    if "target_event" in it: s += f"\n- 장면: {it['target_event']}"
    if "evidence_quote" in it: s += f"\n- 근거: “{it['evidence_quote']}”"
    if "event_match" in it: s += f"\n- 장면 일치(자기보고): {it['event_match']} / 근거 라벨: {it.get('evidence_label','')}"
    if "status" in it:
        s += f"\n- 검수: {it['status']} / 짝맞추기 위험: {it.get('word_matching_risk','')} / 어휘초과(자기보고): {it.get('vocab_over', [])}"
        if it.get("note"): s += f"\n- 메모: {it['note']}"
    return s

def write_compare(path, results, overs, chapter_name, rep):
    md = [f"# 비교 — {chapter_name} · 반복 {rep}",
          f"모델: {MODEL} · {datetime.date.today()} · 어휘 컷: 교육부 누적 {VOCAB_TIER} + 본문단어", "",
          "## 어휘 초과 단어 (코드가 직접 계산)",
          "| 문항 | " + " | ".join(CONDITIONS) + " |", "|---|" + "---|" * len(CONDITIONS)]
    for i in range(1, 6):
        md.append(f"| Q{i} | " + " | ".join(", ".join(overs[c].get(i, [])) or "-" for c in CONDITIONS) + " |")
    for c in CONDITIONS:
        md += ["", f"## {c}", ""] + [fmt(it) + "\n" for it in results[c]["items"]]
    path.write_text("\n".join(md), encoding="utf-8")

def write_eval_sheet(path, chapter_name):
    """교사 평가·오류 유형 기록용 빈 표. 조건·반복·문항마다 한 줄."""
    cols = ["chapter","condition","repeat","item","type",
            "정답정확(1-5)","근거일치(1-5)","오답선지타당(1-5)","정답누설없음(1-5)","어휘적합(1-5)","채점기준명확(1-5, cr만)",
            "오류유형(정답오류/근거불일치/오답선지부적절/정답누설/어휘위반/없음)","메모"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(cols)
        for rep in range(1, REPEATS + 1):
            for c in CONDITIONS:
                for i, t in zip(range(1, 6), ["mc","mc","mc","short","cr"]):
                    w.writerow([chapter_name, c, rep, i, t, "", "", "", "", "", "" if t == "cr" else "n/a", "", ""])

# ---------- 메인 ----------
def main(chapter_path):
    chapter = read(chapter_path)
    chapter_name = Path(chapter_path).stem
    vocab = load_vocab()
    chapter_words = tokenize(chapter)
    vocab_text = "\n".join(sorted(vocab))

    prompts = {}
    for c in CONDITIONS:
        p = read(ROOT / f"prompts/prompt_{c}.md")
        prompts[c] = (p.replace("{{CHAPTER_TEXT}}", chapter)
                       .replace("{{LEVEL}}", LEVEL)
                       .replace("{{VOCAB_LIST}}", vocab_text))

    out = ROOT / "outputs" / datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out.mkdir(parents=True, exist_ok=True)

    for rep in range(1, REPEATS + 1):
        results, overs = {}, {}
        for c in CONDITIONS:
            print(f"[{rep}/{REPEATS}] {c} 생성 중...")
            results[c] = call(prompts[c])
            (out / f"{c}_{rep}.json").write_text(json.dumps(results[c], ensure_ascii=False, indent=2), encoding="utf-8")
            overs[c] = vocab_over(results[c]["items"], vocab, chapter_words)
        write_compare(out / f"compare_{rep}.md", results, overs, chapter_name, rep)

    write_eval_sheet(out / "eval_sheet.csv", chapter_name)
    (out / "run_info.txt").write_text(
        f"model={MODEL}\nlevel={LEVEL}\nvocab_tier={VOCAB_TIER}\nrepeats={REPEATS}\nconditions={CONDITIONS}\nchapter={chapter_path}\n",
        encoding="utf-8")
    print(f"내부용 완료 → {out}")
    export_public(out, chapter_path)                 # outputs_public/ 에 원문 없는 공개용 생성

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "data/chapter01.txt")
