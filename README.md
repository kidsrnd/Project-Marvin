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
├─ data/chapter01.txt   ← 원서 텍스트 (GitHub에 올리지 말 것)
├─ vocab/moe_800.txt    ← 교육부 초등 800 단어 (직접 채우기)
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
- `vocab/moe_800.txt`를 채우기 전에는 "본문 등장 단어"만 허용 어휘로 계산된다. 채우면 자동으로 반영.
- `data/` 폴더는 GitHub에 올리지 않는다 (`.gitignore`에 `data/` 한 줄).
- 프롬프트를 고치면 A·B **둘 다 다시** 돌린다. 한쪽만 다시 돌리면 비교가 깨진다.

## 다음 단계 (4주차 이후)

- 챕터 2 추가 → 짧은 챕터는 1~2장을 한 단위로
- 교사 평가지(5기준 × 5점 척도) 만들기
- 웹 입력 화면 (Antigravity)
