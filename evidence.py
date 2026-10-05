"""
evidence.py — 근거 문장을 본문에서 찾아 위치(문단 번호·글자 위치)를 붙이고,
              공개용(원문 없이 evidence_id·위치·라벨만) 버전을 만든다.

내부용: outputs/<실행폴더>/  (원문 근거 문장 포함 — GitHub에 올리지 않음)
공개용: outputs_public/<실행폴더>/  (evidence_id + 판본/장/문단/글자위치 + 라벨 — GitHub에 올림)

단독 실행:  python evidence.py outputs/20261005_2130 data/chapter01.txt
(run_abc.py 가 끝날 때 자동으로도 호출된다)
"""
import json, re, sys, shutil
from pathlib import Path

ROOT = Path(__file__).parent

def paragraphs(text):
    """본문을 문단 리스트로 (줄 하나 = 문단 하나, 빈 줄 제외). 각 문단의 (시작, 끝) 글자 위치. 0번은 첫 줄(제목)."""
    out, pos = [], 0
    for line in text.split("\n"):
        start = pos; pos += len(line) + 1
        if line.strip(): out.append((start, start + len(line)))
    return out

def norm(s): return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def locate(quote, text, paras):
    """근거 문장을 본문에서 찾는다. 정확히 없으면 따옴표·공백 차이를 무시하고 다시 찾는다."""
    if not quote: return None
    # 1) 그대로
    i = text.find(quote)
    # 2) '...'로 이어붙인 인용은 첫 조각만
    if i < 0 and "..." in quote:
        i = text.find(quote.split("...")[0].strip())
    # 3) 정규화 비교 (따옴표 종류, 공백 차이)
    if i < 0:
        nq = norm(quote)
        for p, (a, b) in enumerate(paras):
            if nq and nq[:40] in norm(text[a:b]):
                return {"paragraph": p, "start": a, "end": b, "match": "fuzzy"}
        return {"paragraph": None, "start": None, "end": None, "match": "not_found"}
    p = next((k for k, (a, b) in enumerate(paras) if a <= i < b), None)
    return {"paragraph": p, "start": i, "end": i + len(quote), "match": "exact"}

def attach_locations(items, text, meta, chapter_id):
    """각 문항의 근거에 evidence_id와 위치를 붙인다 (내부용 JSON에 그대로 추가)."""
    paras = paragraphs(text)
    for it in items:
        k = 0
        if "evidence_quote" in it:
            k += 1
            loc = locate(it["evidence_quote"], text, paras)
            it["evidence"] = {"evidence_id": f"{meta['book_id']}-{chapter_id}-q{it['id']}-e{k}",
                              "label": it.get("evidence_label", "support"), **loc}
        if isinstance(it.get("distractor_evidence"), dict):
            it["distractor_evidence_loc"] = {}
            for opt, d in it["distractor_evidence"].items():
                k += 1
                q = d.get("quote", d) if isinstance(d, dict) else d
                loc = locate(q, text, paras)
                it["distractor_evidence_loc"][opt] = {"evidence_id": f"{meta['book_id']}-{chapter_id}-q{it['id']}-e{k}",
                                                      "label": d.get("label", "contradict") if isinstance(d, dict) else "contradict", **loc}
    return items

PRIVATE_KEYS = {"evidence_quote", "distractor_evidence", "rubric", "sample_answer", "answer"}

def public_view(items):
    """원문이 들어갈 수 있는 칸을 모두 빼고, evidence_id·위치·라벨만 남긴다."""
    pub = []
    for it in items:
        p = {k: v for k, v in it.items() if k not in PRIVATE_KEYS and k != "distractor_evidence_loc"}
        if "evidence" in it: p["evidence"] = it["evidence"]
        if "distractor_evidence_loc" in it: p["distractor_evidence"] = it["distractor_evidence_loc"]
        # 채점표는 점수 기준 구조만 남기고 예시 답(원문 인용 가능성)은 제외
        if "rubric" in it:
            p["rubric_fields"] = sorted(it["rubric"].keys())
        pub.append(p)
    return pub

def export(run_dir, chapter_path):
    run_dir, chapter_path = Path(run_dir), Path(chapter_path)
    text = chapter_path.read_text(encoding="utf-8")
    meta = json.load(open(ROOT / "data/book_meta.json", encoding="utf-8"))
    chapter_id = chapter_path.stem
    pub_dir = ROOT / "outputs_public" / run_dir.name
    pub_dir.mkdir(parents=True, exist_ok=True)

    n = 0
    for f in sorted(run_dir.glob("*.json")):
        data = json.load(open(f, encoding="utf-8"))
        if "items" not in data: continue
        data["items"] = attach_locations(data["items"], text, meta, chapter_id)
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")   # 내부용에 위치 추가
        pub = {"book": {k: meta[k] for k in ("book_id","title","author","isbn","edition")},
               "chapter": chapter_id, "condition": f.stem.split("_")[0], "repeat": f.stem.split("_")[1],
               "items": public_view(data["items"])}
        (pub_dir / f.name).write_text(json.dumps(pub, ensure_ascii=False, indent=2), encoding="utf-8")
        n += 1
    for extra in ("eval_sheet.csv", "run_info.txt"):
        if (run_dir / extra).exists(): shutil.copy(run_dir / extra, pub_dir / extra)
    print(f"공개용 {n}개 파일 → {pub_dir}  (원문 문장 없음)")

if __name__ == "__main__":
    export(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ROOT / "data/chapter01.txt")
