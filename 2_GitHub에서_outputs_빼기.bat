@echo off
chcp 65001 >nul
cd /d "%~dp0"
set GIT=git
where git >nul 2>nul
if errorlevel 1 (
  for /d %%D in ("%LOCALAPPDATA%\GitHubDesktop\app-*") do (
    if exist "%%D\resources\app\git\cmd\git.exe" set GIT="%%D\resources\app\git\cmd\git.exe"
  )
)
echo GitHub 추적 목록에서 outputs 폴더만 뺍니다. (PC 파일은 지워지지 않아요)
%GIT% rm -r --cached outputs
echo.
echo 이제 GitHub Desktop 을 열어 Commit 하고 Push 하세요.
pause
