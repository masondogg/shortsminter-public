@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ====================================================
echo   ShortsMinter(TM) -- Deploy Script
echo   Masondogg Studios, LLC
echo ====================================================
echo.

:: ── Check git is installed ───────────────────────────
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERROR: Git is not installed.
    echo   Download it at: git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

:: ── Check we are inside a git repo ───────────────────
git rev-parse --git-dir >nul 2>&1
if %errorlevel% neq 0 (
    echo   ERROR: This folder is not a git repository.
    echo   Make sure deploy.bat is inside your cloned repo folder.
    echo.
    pause
    exit /b 1
)

:: ── Show changed files BEFORE doing anything ─────────
echo   Checking for changes...
echo.

git status --short > "%TEMP%\sm_changes.txt" 2>&1
set CHANGE_COUNT=0
for /f %%i in ('git status --short ^| find /c /v ""') do set CHANGE_COUNT=%%i

if "%CHANGE_COUNT%"=="0" (
    echo   No changes detected -- everything is already up to date.
    echo   Nothing was pushed.
    echo.
    pause
    exit /b 0
)

echo   The following files will be uploaded to GitHub:
echo   ------------------------------------------------
type "%TEMP%\sm_changes.txt"
echo   ------------------------------------------------
echo.
echo   Legend:
echo    M  = Modified  (you edited this file)
echo    A  = Added     (new file)
echo    D  = Deleted   (removed file)
echo    ?? = Untracked (new file not yet tracked)
echo.

:: ── Confirm before touching anything ─────────────────
set /p CONFIRM="   Push these changes? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo.
    echo   Cancelled -- nothing was pushed.
    echo.
    pause
    exit /b 0
)

echo.

:: ── Ask for commit message ────────────────────────────
set /p MSG="   Commit message (describe what you changed): "
if "%MSG%"=="" set MSG=Site update

:: ── Stage all changes ─────────────────────────────────
echo.
echo   Staging files...
git add -A
if %errorlevel% neq 0 (
    echo   ERROR: git add failed.
    pause
    exit /b 1
)

:: ── Commit ────────────────────────────────────────────
echo   Committing...
git commit -m "%MSG%"
if %errorlevel% neq 0 (
    echo   ERROR: git commit failed.
    pause
    exit /b 1
)

:: ── Push ──────────────────────────────────────────────
echo.
echo   Pushing to GitHub...
echo   (A browser window may open on first run -- just click Authorize)
echo.
git push
if %errorlevel% neq 0 (
    echo.
    echo   ERROR: Push failed.
    echo   Common causes:
    echo    - No internet connection
    echo    - Not authenticated -- re-run and authorize in browser
    echo    - Remote has changes you need to pull first
    echo.
    pause
    exit /b 1
)

:: ── Success ───────────────────────────────────────────
echo.
echo ====================================================
echo   SUCCESS -- Changes pushed to GitHub!
echo ====================================================
echo.
echo   Files uploaded:
type "%TEMP%\sm_changes.txt"
echo.
echo   GitHub Pages will update in 1-2 minutes.
echo   Check: https://shortsminter.com
echo.
pause
