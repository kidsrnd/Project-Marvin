@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ================================================
echo   B1 문항 따로 검사하기 (review.py)
echo ================================================
echo.
if "%ANTHROPIC_API_KEY%"=="" (
  echo API 키를 붙여넣고 Enter 를 누르세요. ^(sk-ant- 로 시작^)
  echo 붙여넣기: 마우스 오른쪽 클릭
  set /p ANTHROPIC_API_KEY=키: 
)
echo.
python review.py outputs/20261005_1336 data/chapter01.txt
echo.
echo ================================================
echo   끝났으면 Claude 에게 "검수 끝났어" 라고 말해 주세요.
echo   빨간 오류가 보이면 이 창을 사진 찍어 보여 주세요.
echo ================================================
pause
