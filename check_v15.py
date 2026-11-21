"""
check_v15.py — 판정 기준 v1.5 집계용 검사기 (make_blind.py --check 의 v1.5 판)
  배포한 판정지(구글 시트)는 고치지 않는다. 이 파일은 회수한 판정지를 집계하기 전에 검사만 한다.
  v1.5 사용 가능 여부 규칙 (배포본 Q열 수식과 같은 순서):
    1) H~L 에 빈칸이 있으면 계산하지 않음 (미판정)
    2) H·I(치명) 중 '있음'      → 사용 불가   (다른 칸에 보류가 있어도 사용 불가)
    3) H~L 중 '판단 보류'       → 미확정
    4) J·K·L(중대) 중 '있음'    → 고치면 사용
    5) 그 외                    → 그대로 사용
  '해당 없음'(단답·서술형의 I·J·M)은 빈칸도 '있음'도 아니다.
실행: python check_v15.py <구글 시트에서 내려받은 판정지.xlsx>
자체 점검(다섯 사례): python check_v15.py --selftest
"""
import sys

FATAL, MAJOR = "HI", "JKL"

def usable(row):
    """row: {'H':..,'I':..,'J':..,'K':..,'L':..} → v1.5 규칙의 사용 가능 여부"""
    v = [row.get(c) for c in FATAL + MAJOR]
    if any(x in (None, "") for x in v): return ""
    if any(row[c] == "있음" for c in FATAL): return "사용 불가"
    if any(x == "판단 보류" for x in v): return "미확정"
    if any(row[c] == "있음" for c in MAJOR): return "고치면 사용"
    return "그대로 사용"

def check(path):
    from openpyxl import load_workbook
    ws = load_workbook(path, data_only=True)["판정"]   # data_only: Q열 수식이 아니라 계산된 값을 읽는다
    need = "FHIJKLMN"; empty = []; hold = []; clash = []
    for r in range(2, ws.max_row + 1):
        n = ws[f"A{r}"].value
        if n is None: continue
        miss = [c for c in need if ws[f"{c}{r}"].value in (None, "")]
        if miss: empty.append((n, miss))
        h = [c for c in "HIJKLMN" if ws[f"{c}{r}"].value == "판단 보류"]
        if h: hold.append((n, h))
        want = usable({c: ws[f"{c}{r}"].value for c in "HIJKL"})
        got = ws[f"Q{r}"].value or ""
        if want != got: clash.append((n, got, want))
    for n, m in empty: print(f"[미판정] {n}번: {' '.join(m)} 칸이 비어 있음")
    for n, m in hold:  print(f"[보류] {n}번: {' '.join(m)}")
    for n, g, w in clash: print(f"[불일치] {n}번: 판정지 Q='{g}', v1.5 규칙='{w}' (판정값은 고치지 말고 원인을 확인)")
    print(f"판단 보류 {sum(len(m) for _, m in hold)}칸 ({len(hold)}문항)")
    ok = not empty and not clash
    print("빈칸·불일치 없음 — 집계 가능" if ok else "→ 빈칸 또는 불일치가 있어 집계하지 않습니다.")
    return ok

def old_check_v14(row, q):
    """make_blind.py v7 --check 의 모순 규칙: 치명·중대에 보류가 있는데 Q가 미확정이 아니면 모순"""
    h = any(row.get(c) == "판단 보류" for c in "HIJKL")
    return "모순 경고" if h and q not in (None, "", "미확정") else "통과"

CASES = [
 ("① 치명 있음 + 다른 칸 보류", dict(H="있음", I="없음", J="판단 보류", K="없음", L="없음"), "사용 불가"),
 ("② 치명 없음 + 중대 보류",   dict(H="없음", I="없음", J="없음", K="판단 보류", L="없음"), "미확정"),
 ("③ 전부 없음",               dict(H="없음", I="없음", J="없음", K="없음", L="없음"), "그대로 사용"),
 ("④ 빈칸",                    dict(H="없음", I="없음", J="", K="없음", L="없음"), ""),
 ("⑤ 객관식 아님 (I·J 해당 없음)", dict(H="없음", I="해당 없음", J="해당 없음", K="없음", L="있음"), "고치면 사용"),
 ("(추가) 치명 보류, 치명 있음 없음", dict(H="판단 보류", I="없음", J="없음", K="있음", L="없음"), "미확정"),
 ("(추가) 중대 있음만",         dict(H="없음", I="없음", J="있음", K="없음", L="없음"), "고치면 사용"),
]

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        bad = 0
        for name, row, exp in CASES:
            got = usable(row); bad += got != exp
            print(f"{name} | 예상 '{exp or '(계산 안 함)'}' | v1.5 검사기 '{got or '(계산 안 함)'}' | {'일치' if got == exp else '불일치'} | 기존 --check(v1.4): {old_check_v14(row, got)}")
        print("다섯 사례 모두 일치" if not bad else f"{bad}건 불일치")
    else:
        check(sys.argv[1])
