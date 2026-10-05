# Marvin 프로토타입 — A / B1 / B2 비교

챕터 텍스트 하나를 넣으면 같은 모델로 세 조건을 REPEATS번씩 만들어 나란히 보여줍니다.

| 조건 | 내용 | 뭘 보나 |
|---|---|---|
| **A** | 기본 생성 (규칙 없음) | 기준선 |
| **B1** | A + 생성 규칙 (선지는 본문 사건만, 어휘 제한, 짝맞추기 금지, 정답 누설 금지, 문장 길이 제한) | 규칙만으로 얼마나 나아지나 |
| **B2** | B1 + 자기검수 (근거 인용·**장면 일치**·오답 근거·어휘·짝맞추기) + 서술형 채점표 | 자기검수가 추가로 얼마나 기여하나 |

조건을 하나씩 더해가며 비교하는 방식(ablation)이라 "무엇 때문에 좋아졌는지"를 분리할 수 있습니다.

## 폴더

```
Project-Marvin/
├─ run_abc.py           ← 실행 파일 (A/B1/B2 × 반복)
├─ run_ab.py            ← 3주차 A/B 버전 (기록용)
├─ prompts/prompt_A.md  ← 기본 생성
├─ prompts/prompt_B1.md ← 생성 규칙만
├─ prompts/prompt_B2.md ← 규칙 + 자기검수(장면 일치 포함) + 채점표
├─ prompts/prompt_B.md  ← 3주차 버전 (기록용)
├─ lemma.py             ← 변화형(was, children…)을 대표형으로 되돌리는 도구
├─ profile.py           ← 원서 텍스트의 어휘 프로필 (교육부 3층 어디에 속하는지 집계)
├─ data/chapter01.txt   ← 원서 텍스트 (GitHub에 올리지 말 것)
├─ vocab/
│   ├─ moe_800.txt      ← 교육부 초등 권장 800 (2022 개정 고시 별표 3, *표)
│   ├─ moe_2000.txt     ← + 중·고 공통 1,200 = 누적 2,000 (**표)
│   ├─ moe_3000.txt     ← + 고등 선택 1,000 = 전체 3,000
│   └─ moe_tier.json    ← 단어별 등급 (1/2/3)
├─ evidence.py          ← 근거 문장 위치 찾기 + 공개용 내보내기
├─ data/book_meta.json  ← 책 판본 정보 (ISBN·edition — 직접 채우기)
├─ outputs/<날짜_시각>/  ← 내부용: 원문 근거 문장 포함 (GitHub에 올리지 않음)
└─ outputs_public/<날짜_시각>/ ← 공개용: evidence_id + 판본/장/문단/글자위치 + 라벨만 (GitHub에 올림)
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
   `python run_abc.py data/chapter01.txt`
5. `outputs/<날짜_시각>/compare_1.md` … 열어서 세 조건 비교, `eval_sheet.csv`에 평가 기록

## 꼭 지킬 것

- 세 조건은 **같은 모델, 같은 날, 같은 텍스트**로 돌린다. `run_abc.py` 맨 위 `MODEL`·`REPEATS`·`CONDITIONS` 세 줄이 실험 설정.
- 허용 어휘 컷은 `run_abc.py` 맨 위 `VOCAB_TIER` 한 줄로 정한다 (800 / 2000 / 3000). Marvin은 2000(Pupa 레벨 = 초등 고학년~중1 학습자, 교육과정상 중학교 총 학습 어휘 1,500 이내 → 초등 800 + 중·고 공통 1,200 누적), Hatchet은 3000.
- 어휘 검사는 교육부 지침대로 굴절형·36개 파생 접사·합성어를 대표형으로 환원해 비교하고, 고유명사·호칭·감탄사는 예외 처리한다.
- 원서 자체의 어휘 프로필: `python profile.py data/chapter01.txt`
- `data/` 폴더는 GitHub에 올리지 않는다 (`.gitignore`에 `data/` 한 줄).
- 프롬프트를 고치면 **세 조건 모두** 다시 돌린다. 일부만 다시 돌리면 비교가 깨진다.

## 근거(evidence) 이중 구조

| | 내부용 `outputs/` | 공개용 `outputs_public/` |
|---|---|---|
| 근거 문장 원문 | 있음 | 없음 |
| evidence_id | 있음 | 있음 (`book_id-chapter-qN-eK`) |
| 위치 | 문단 번호 + 글자 위치(start/end) | 동일 |
| 라벨 | support / contradict / insufficient | 동일 |
| 채점표 예시 답 | 있음 | 필드명만 |

교사 평가·gold evidence 대조는 내부용으로, 논문·저장소에는 공개용만. 판본은 `data/book_meta.json`에 고정.

## 평가표 (eval_sheet.csv)

조건·반복·문항마다 한 줄. 교사가 5점 척도로 기록:
정답 정확 / 근거 일치 / 오답 선지 타당 / 정답 누설 없음 / 어휘 적합 / 채점기준 명확(서술형만)
+ 오류 유형 하나: 정답오류 · 근거불일치 · 오답선지부적절 · 정답누설 · 어휘위반 · 없음

## 어휘 목록 출처

교육부(2022). 영어과 교육과정. 교육부 고시 제2022-33호 [별책 14] 별표 3 기본 어휘 목록 (3,000어).
초등 권장 800 / 중·고 공통과목 권장 1,200 / 고등 선택과목 권장 1,000.

## 다음 단계 (5주차 이후)

- 챕터 2 추가 → 짧은 챕터는 1~2장을 한 단위로
- 레벨 다른 원서 2~3권으로 확대 (Nate the Great 등)
- 교사 평가지(5기준 × 5점 척도) 만들기
- 웹 입력 화면 (Antigravity)
