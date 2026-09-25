"""
run_ab.py — 챕터 하나로 A(검수 없음) / B(생성+자기검수) 문항을 만들어 나란히 비교한다.

실행:  python run_ab.py data/chapter01.txt
결과:  outputs/A.json, outputs/B.json, outputs/compare.md
"""
import json, re, sys, datetime
from pathlib import Path
import anthropic                      # pip install anthropic
from lemma import lemmatize, lemmatize_compound   # 변화형(was, children…)을 대표형으로 되돌림

MODEL = "claude-sonnet-4-6"           # A·B 둘 다 이 모델로 고정 (바꾸면 두 조건 다 바뀜)
LEVEL = "Pupa (Korean elementary, about grade 3-4)"
VOCAB_TIER = 2000                     # 허용 어휘 컷: 800(초등) / 2000(중고 공통까지) / 3000(전체)
ROOT = Path(__file__).parent

# ---------- 1. 파일 읽기 ----------
def read(path):                       # 파일 내용을 문자열로 읽는다
    return Path(path).read_text(encoding="utf-8")

def load_vocab():                     # 교육부 기본 어휘, VOCAB_TIER 컷까지
    words = set()
    for line in read(ROOT / f"vocab/moe_{VOCAB_TIER}.txt").splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            words.add(line)
    return words

def tokenize(text):                   # 문장을 소문자 단어 집합으로 바꾼다
    return set(re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower()))

# ---------- 2. 모델 호출 ----------
def call(prompt):                     # 프롬프트를 보내고 JSON을 돌려받는다
    client = anthropic.Anthropic()    # API 키는 환경변수 ANTHROPIC_API_KEY 에서 읽음
    resp = client.messages.create(
        model=MODEL, max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()  # ```json 울타리 제거
    return json.loads(text)

# ---------- 3. 어휘 초과 검사 (모델 자기보고와 별개로, 코드가 직접 센다) ----------
def item_text(item):                  # 문항에서 학생이 읽는 부분만 모은다 (질문 + 선지, 선지 앞 A/B/C/D 글자는 제거)
    opts = [re.sub(r"^[A-D][\.\)]?\s+", "", o) for o in item.get("options", [])]
    return " ".join([item.get("question", "")] + opts)

EXCEPT = {"mr","mrs","ms","dr","oh","ah","wow","hey","ok","okay"}   # 교육부 예외(호칭·감탄사)

def vocab_over(items, allowed, chapter_words):
    """허용 어휘(교육부 컷 + 본문 단어)에 없는 단어를 문항별로 찾는다. 변화형·접두사·합성어는 대표형으로 환원해 비교."""
    result = {}
    for it in items:
        over = []
        for w in sorted(tokenize(item_text(it))):
            base = w[:-2] if w.endswith("'s") else w        # marvin's → marvin
            if base in EXCEPT or base in chapter_words: continue
            if lemmatize(w, allowed) in allowed: continue
            c, kind = lemmatize_compound(w, allowed)
            if kind: continue
            over.append(w)
        result[it["id"]] = over
    return result

# ---------- 4. 비교표 만들기 ----------
def fmt_item(it):
    s = f"**Q{it['id']} ({it['type']})** {it['question']}"
    for o in it.get("options", []):
        s += f"\n- {o}"
    if "answer" in it:
        s += f"\n- 정답: {it['answer']}"
    if "sample_answer" in it:
        s += f"\n- 예시답: {it['sample_answer']}"
    if "rubric" in it:
        r = it["rubric"]
        s += f"\n- 핵심요소: {r.get('key_elements','')}\n- 근거위치: {r.get('accepted_evidence_locations','')}"
        s += f"\n- 4점 예: {r.get('example_4pt','')}\n- 2점 예: {r.get('example_2pt','')}\n- 0점 예: {r.get('example_0pt','')}"
    if "evidence_quote" in it:
        s += f"\n- 근거: “{it['evidence_quote']}”"
    if "status" in it:
        s += f"\n- 검수: {it['status']} / 짝맞추기 위험: {it.get('word_matching_risk','')} / 어휘초과(자기보고): {it.get('vocab_over', [])}"
        if it.get("note"):
            s += f"\n- 메모: {it['note']}"
    return s

def main(chapter_path):
    chapter = read(chapter_path)
    vocab = load_vocab()
    chapter_words = tokenize(chapter)            # 본문에 나온 단어는 레벨과 무관하게 허용
    allowed = vocab
    vocab_text = "\n".join(sorted(vocab)) if vocab else "(list not provided — use chapter words only)"

    pa = read(ROOT / "prompts/prompt_A.md").replace("{{CHAPTER_TEXT}}", chapter)
    pb = (read(ROOT / "prompts/prompt_B.md")
          .replace("{{CHAPTER_TEXT}}", chapter)
          .replace("{{LEVEL}}", LEVEL)
          .replace("{{VOCAB_LIST}}", vocab_text))

    print("A 생성 중..."); A = call(pa)
    print("B 생성 중..."); B = call(pb)

    out = ROOT / "outputs"; out.mkdir(exist_ok=True)
    (out / "A.json").write_text(json.dumps(A, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "B.json").write_text(json.dumps(B, ensure_ascii=False, indent=2), encoding="utf-8")

    overA = vocab_over(A["items"], allowed, chapter_words)
    overB = vocab_over(B["items"], allowed, chapter_words)

    md = [f"# A/B 비교 — {Path(chapter_path).name}",
          f"모델: {MODEL} · 생성일: {datetime.date.today()} · 허용어휘: 교육부 누적 {VOCAB_TIER} ({len(vocab)}개) + 본문단어",
          "", "## 어휘 초과 단어 (코드가 직접 계산)",
          "| 문항 | A | B |", "|---|---|---|"]
    for i in range(1, 6):
        md.append(f"| Q{i} | {', '.join(overA.get(i, [])) or '-'} | {', '.join(overB.get(i, [])) or '-'} |")
    md += ["", "## A — 검수 없음", ""] + [fmt_item(it) + "\n" for it in A["items"]]
    md += ["", "## B — 생성 + 자기검수", ""] + [fmt_item(it) + "\n" for it in B["items"]]
    (out / "compare.md").write_text("\n".join(md), encoding="utf-8")
    print("완료 → outputs/compare.md")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "data/chapter01.txt")
