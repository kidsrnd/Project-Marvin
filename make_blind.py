"""
make_blind.py v6 — 조건명 비공개 판정지 (교수님 5·6주차 피드백 반영)
  v5 변경: K·L 칸 이름 구체화 (평가 기준 v1.1, 교사 혼동 방지)
  v6 변경: M칸을 [참고] 설계 규칙 확인용으로 변경, N칸에 학습자 수준 명시 (평가 기준 v1.2)
  v4 변경: 오류 칸은 있음/없음/판단 보류/해당 없음 중 하나 (빈칸 = 미판정),
           객관식 전용 3칸(복수 정답·구별 안 되는 오답·본문에 없는 오답)은 단답·서술형에서 자동 '해당 없음',
           '블라인드' 표현 삭제, 연구자용 파일을 교사용과 분리, --check 로 빈칸 경고
  - 조건명·전후 짝·검수기 지적은 모두 숨김 (교사가 먼저 독립 판정)
  - '본문' 탭: 문단 번호 = evidence.py 의 paragraph 번호와 같음 → 근거 위치 기록용
  - '정답이 2개 이상'은 객관식만, '사용 가능 여부' 칸 추가
  - 교사 2명용 파일을 따로 만든다 (같은 순서, 서로 보지 않고 채점)
실행: python make_blind.py outputs/20261005_1336 data/chapter01.txt  [--first30 : B1 수정 전·후 30문항만]
빈칸 검사: python make_blind.py --check outputs/20261005_1336/blind/judge_sheet_v4_1차30_연구자.xlsx
결과: outputs/20261005_1336/blind/  judge_sheet_v4_<태그>_연구자/교사1/교사2.xlsx, judge_key_v4_<태그>.csv
"""
import json, random, csv, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

COLS = [("번호",6),("유형",7),("문제",40),("선지",44),("표시된 정답",30),
        ("정답이 맞나 (O/X/?)",10),
        ("근거 문단 번호 ('본문' 탭)",10),
        ("[치명] 본문 근거 없는 정답",11),("[치명] 정답 선지가 2개 이상 (객관식만)",12),
        ("[중대] 본문만으로 구별 안 되는 오답 (객관식만)",12),("[중대] 문제 문장 안에 답이 있음 (본문 안 읽어도 풀림)",13),("[중대] 본문 표현 그대로 → 그 문장만 찾으면 풀림",13),
        ("[참고] 본문에 없는 내용의 오답 (AI 설계 규칙 확인용, 오류 아님) (객관식만)",14),("[경미] 어휘·길이 문제 (Pupa·중학 수준)",11),
        ("서사 요소",11),("명시/암시",9),
        ("사용 가능 여부",12),("메모",30)]
GREY = PatternFill("solid", fgColor="D9D9D9")

SETS = [("A","A_{}.json"),("B1","B1_{}.json"),("B1R","review/B1R_{}.json"),("B2","B2_{}.json")]

def load(run, sets=SETS):
    pool = []
    for cond, pat in sets:
        for r in (1,2,3):
            for it in json.loads((run/pat.format(r)).read_text(encoding="utf-8"))["items"]:
                pool.append((cond, r, it))
    return pool

def answer_text(it):
    if it["type"] == "mc": return it.get("answer","")
    if "sample_answer" in it: return it["sample_answer"]
    if "rubric" in it: return "채점 핵심: " + it["rubric"].get("key_elements","")
    return it.get("answer","")

GUIDE = [
 "■ 채점 순서",
 "1. '본문' 탭에서 챕터를 먼저 한 번 읽습니다. 문단마다 번호가 있습니다.",
 "2. 문제마다 표시된 정답이 맞는지 O / X / ? 를 고르고, 그 근거가 되는 문단 번호를 적습니다 (예: 4, 또는 4,15).",
 "3. 오류 칸(빨강·노랑·초록 머리) 하나하나에 '있음 / 없음 / 판단 보류' 중 하나를 고릅니다.",
 "   빈칸으로 두면 '아직 안 봄'으로 처리됩니다. 오류가 없으면 반드시 '없음'을 고르세요.",
 "   회색 칸은 이미 '해당 없음'이 들어가 있습니다 (객관식 전용 기준). 건드리지 않습니다.",
 "   확신이 서지 않으면 '판단 보류'를 고르고 메모에 이유를 한 줄 적습니다.",
 "4. 마지막으로 '사용 가능 여부'를 고릅니다.",
 "",
 "■ 오류 기준 (고정)",
 "[치명] 본문 근거 없는 정답: 정답이 본문의 대사·행동·서술로 뒷받침되지 않음.",
 "      감정을 묻는 문제라도, 그 장면의 대사·행동으로 그 감정을 설명할 수 있으면 '있음'이 아닙니다.",
 "      다른 감정도 똑같이 가능하면 '있음'입니다.",
 "[치명] 정답 선지가 2개 이상: 객관식에서 다른 선지도 정답으로 인정됨. (객관식만)",
 "      서술형에서 여러 표현이 맞는 것은 오류가 아닙니다.",
 "[중대] 본문만으로 구별 안 되는 오답: 본문을 읽어도 그 오답이 틀렸다고 확인할 수 없음. (객관식만)",
 "[중대] 문제 문장 안에 답이 있음: 본문을 읽지 않고 문제 문장만 읽어도 답을 고를 수 있음.",
 "[중대] 본문 표현 그대로 → 그 문장만 찾으면 풀림: 문제(또는 정답 선지)에 본문 표현이 그대로 있어서,",
 "      그 표현을 본문에서 찾아 바로 옆 문장만 보면 이해 없이 답이 나옴. 본문 단어를 쓴 것 자체는 오류가 아님.",
 "[참고] 본문에 없는 내용의 오답: 오답 선지 내용이 본문에서 일어난 적도, 언급된 적도 없음. (객관식만)",
 "      수능 내용일치 문제처럼 '본문에 없는 내용'으로 오답을 만드는 것은 정상적인 출제 방법이며 문항 오류가 아닙니다.",
 "      이 칸은 AI에게 준 설계 규칙(오답도 본문 사건으로 만들 것)을 지켰는지 확인하는 기록용입니다.",
 "      '사용 가능 여부'에는 영향을 주지 않습니다.",
 "[경미] 어휘·길이: Pupa 레벨(국내 중학 수준, 교육부 기본 어휘 2,000단어)에 어려운 단어가 있거나, 문제가 너무 김.",
 "",
 "■ 서사 요소 / 명시·암시 (오류와 별도로 기록)",
 "서사 요소: 이 문제가 무엇을 묻는지 하나 고릅니다 (인물·배경·사건·감정·인과·결말·예측).",
 "명시 = 답이 본문에 그대로 있음 / 암시 = 읽고 추론해야 함.",
 "'감정'이나 '암시'를 골랐다고 해서 오류는 아닙니다. 오류 여부는 위 칸에서 따로 판단합니다.",
 "",
 "■ 사용 가능 여부 (고정)",
 "그대로 사용: 치명 0, 중대 0 (경미·참고는 있어도 됨)",
 "고치면 사용: 치명 0, 중대 1개 이상",
 "사용 불가: 치명 1개 이상",
 "",
 "■ 주의",
 "어느 조건이 만든 문제인지, 수정 전인지 후인지는 숨겨 두었습니다. 추측하지 말고 문제만 보세요.",
 "비슷한 문제가 여러 번 나와도 각각 따로 채점합니다.",
 "다른 선생님과 상의하지 말고 혼자 채점합니다. 다 끝난 뒤에 맞춰 봅니다.",
 "judge_key 파일은 채점이 끝날 때까지 열지 마세요.",
]

def build(pool, chapter, path):
    wb = Workbook(); ws = wb.active; ws.title = "판정"
    f11 = Font(name="맑은 고딕", size=11); fb = Font(name="맑은 고딕", size=11, bold=True)
    for c,(h,w) in enumerate(COLS,1):
        cell = ws.cell(1,c,h); cell.font=fb; cell.alignment=Alignment(wrap_text=True,vertical="center")
        cell.fill = PatternFill("solid", fgColor="FDE2E2" if "치명" in h else "FFF2CC" if "중대" in h else "E2EFDA" if "경미" in h else "DDEBF7")
        ws.column_dimensions[cell.column_letter].width = w
    ws.row_dimensions[1].height = 75
    dvs = {"oxq": DataValidation(type="list", formula1='"O,X,?"', allow_blank=True),
           "yn":  DataValidation(type="list", formula1='"있음,없음,판단 보류"', allow_blank=True),
           "nar": DataValidation(type="list", formula1='"인물,배경,사건,감정,인과,결말,예측"', allow_blank=True),
           "ei":  DataValidation(type="list", formula1='"명시,암시"', allow_blank=True),
           "use": DataValidation(type="list", formula1='"그대로 사용,고치면 사용,사용 불가"', allow_blank=True)}
    for dv in dvs.values(): ws.add_data_validation(dv)
    for n,(cond,r,it) in enumerate(pool,1):
        row = n+1
        vals = [n, {"mc":"객관식","short":"단답","cr":"서술형"}[it["type"]], it["question"],
                "\n".join(it.get("options",[])), answer_text(it)]
        for c in range(1, len(COLS)+1):
            cell = ws.cell(row, c, vals[c-1] if c <= len(vals) else None)
            cell.font=f11; cell.alignment=Alignment(wrap_text=True,vertical="top")
        dvs["oxq"].add(f"F{row}"); dvs["nar"].add(f"O{row}"); dvs["ei"].add(f"P{row}"); dvs["use"].add(f"Q{row}")
        for col in "HKLN": dvs["yn"].add(f"{col}{row}")
        for col in MC_ONLY:
            if it["type"] == "mc": dvs["yn"].add(f"{col}{row}")
            else: ws[f"{col}{row}"].value = "해당 없음"; ws[f"{col}{row}"].fill = GREY
    ws.freeze_panes = "A2"
    b = wb.create_sheet("본문")
    b.column_dimensions["A"].width = 8; b.column_dimensions["B"].width = 110
    b.cell(1,1,"문단").font=fb; b.cell(1,2,"본문").font=fb
    k = 0
    for line in chapter.split("\n"):
        if not line.strip(): continue
        b.cell(k+2,1,k).font=f11
        c = b.cell(k+2,2,line + ("   (제목)" if k < 2 else "")); c.font=f11; c.alignment=Alignment(wrap_text=True,vertical="top")
        k += 1
    g = wb.create_sheet("채점 방법")
    g.column_dimensions["A"].width = 110
    for i,line in enumerate(GUIDE,1):
        g.cell(i,1,line).font = fb if line.startswith("■") else f11
    wb.move_sheet("채점 방법", offset=-2)
    wb.active = 1
    wb.save(path)

def main(run_dir, chapter_path):
    run = Path(run_dir); out = run/"blind"; out.mkdir(exist_ok=True)
    chapter = Path(chapter_path).read_text(encoding="utf-8")
    tag = "v6_1차30" if FIRST30 else "v6"
    pool = load(run, SETS[1:3] if FIRST30 else SETS); random.Random(20261019 if FIRST30 else 20261016).shuffle(pool)
    for t in ("연구자","교사1","교사2","교사3"):   # 연구자 판정과 외부 교사 판정은 파일을 나눠 따로 저장
        build(pool, chapter, out/f"judge_sheet_{tag}_{t}.xlsx")
    with open(out/f"judge_key_{tag}.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(["번호","조건","반복","원래문항번호","유형"])
        w.writerows([[n,c,r,it["id"],it["type"]] for n,(c,r,it) in enumerate(pool,1)])
    print(f"{len(pool)}문항 → {out}")

def check(path):
    """빈칸(미판정) 경고: 정답 O/X/?, 오류 7칸, 사용 가능 여부 중 비어 있는 칸을 모두 출력"""
    from openpyxl import load_workbook
    ws = load_workbook(path)["판정"]; need = "FHIJKLMNQ"; empty = []
    for row in range(2, ws.max_row+1):
        if ws[f"A{row}"].value is None: continue
        miss = [ws[f"{c}1"].value for c in need if ws[f"{c}{row}"].value in (None, "")]
        if miss: empty.append((ws[f"A{row}"].value, miss))
    for n, m in empty: print(f"[경고] {n}번 미판정: " + " / ".join(m))
    print("빈칸 없음 — 집계 가능" if not empty else f"→ {len(empty)}문항에 빈칸이 있어 집계하지 않습니다.")
    return not empty

MC_ONLY = "IJM"   # 객관식 전용: 복수 정답(I), 구별 안 되는 오답(J), 본문에 없는 내용의 오답(M, 참고)

if "--check" in sys.argv:
    sys.argv.remove("--check"); check(sys.argv[1]); sys.exit()

FIRST30 = "--first30" in sys.argv
if FIRST30: sys.argv.remove("--first30")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else Path(__file__).parent/"data/chapter01.txt")
