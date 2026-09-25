# Marvin 프로토타입 — A/B 비교 최소 버전

챕터 텍스트 하나를 넣으면 같은 모델로
- **A**: 검수 없이 만든 문항 5개
- **B**: 생성 → 근거 대조 → 어휘 검사 → 짝맞추기 검사 → 서술형 채점표까지 붙인 문항 5개

를 만들어 `outputs/compare.md` 한 장에 나란히 보여줍니다.

## 폴더

```
Project-Marvin/
├─ run_ab.py            ← 실행 파일
├─ prompts/prompt_A.md  ← 검수 없는 프롬프트 (비교군)
├─ prompts/prompt_B.md  ← 검수 있는 프롬프트 (실험군)
├─ lemma.py             ← 변화형(was, children…)을 대표형으로 되돌리는 도구
├─ profile.py           ← 원서 텍스트의 어휘 프로필 (교육부 3층 어디에 속하는지 집계)
├─ data/chapter01.txt   ← 원서 텍스트 (GitHub에 올리지 말 것)
├─ vocab/
│   ├─ moe_800.txt      ← 교육부 초등 권장 800 (2022 개정 고시 별표 3, *표)
│   ├─ moe_2000.txt     ← + 중·고 공통 1,200 = 누적 2,000 (**표)
│   ├─ moe_3000.txt     ← + 고등 선택 1,000 = 전체 3,000
│   └─ moe_tier.json    ← 단어별 등급 (1/2/3)
└─ outputs/             ← 결과 (A.json, B.json, compare.md)
```

## 실행 5단계

1. 터미널에서 이 폴더로 이동
   `cd Project-Marvin`
2. 패키지 설치 (한 번만)
   `pip install anthropic`
3. API 키 설정 (한 번만, 터미널 창마다)
   - Mac/Linux: `export ANTHROPIC_API_KEY=sk-ant-...`
   - Windows PowerShell: `$env:ANTHROPIC_API_KEY="sk-ant-..."`
4. 실행
   `python run_ab.py data/chapter01.txt`
5. `outputs/compare.md` 열어서 A와 B 비교

## 꼭 지킬 것

- A와 B는 **같은 모델, 같은 날, 같은 텍스트**로 돌린다. `run_ab.py` 맨 위 `MODEL` 한 줄이 그 약속.
- 허용 어휘 컷은 `run_ab.py` 맨 위 `VOCAB_TIER` 한 줄로 정한다 (800 / 2000 / 3000). Marvin은 2000, Hatchet은 3000.
- 어휘 검사는 교육부 지침대로 굴절형·36개 파생 접사·합성어를 대표형으로 환원해 비교하고, 고유명사·호칭·감탄사는 예외 처리한다.
- 원서 자체의 어휘 프로필: `python profile.py data/chapter01.txt`
- `data/` 폴더는 GitHub에 올리지 않는다 (`.gitignore`에 `data/` 한 줄).
- 프롬프트를 고치면 A·B **둘 다 다시** 돌린다. 한쪽만 다시 돌리면 비교가 깨진다.

## 어휘 목록 출처

교육부(2022). 영어과 교육과정. 교육부 고시 제2022-33호 [별책 14] 별표 3 기본 어휘 목록 (3,000어).
초등 권장 800 / 중·고 공통과목 권장 1,200 / 고등 선택과목 권장 1,000.

## 다음 단계 (4주차 이후)

- 프롬프트 B 자기검수에 "질문의 시점 = 근거 문장의 시점" 항목 추가
- 단답형 길이 제한, 문제 문장 길이 제한(레벨별)
- 챕터 2 추가 → 짧은 챕터는 1~2장을 한 단위로
- 교사 평가지(5기준 × 5점 척도) 만들기
- 웹 입력 화면 (Antigravity)
