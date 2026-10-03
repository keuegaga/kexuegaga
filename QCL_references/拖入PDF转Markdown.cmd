@echo off
setlocal
title MinerU - PDF to Markdown (local GPU)

REM Clear proxy vars: MinerU mis-parses NO_PROXY entries that contain IPv6
REM loopback (::1 / [::1]) and then dies with "Invalid port: ':1]'".
set "HTTP_PROXY="
set "HTTPS_PROXY="
set "ALL_PROXY="
set "http_proxy="
set "https_proxy="
set "all_proxy="
set "NO_PROXY="
set "no_proxy="

if "%~1"=="" goto usage

set "KIT=D:\Codex-Obsidian\mineru-local\venv310\Scripts\mineru-kit.exe"
set "MINERU=D:\Codex-Obsidian\mineru-local\venv310\Scripts\mineru.exe"

REM Make sure the local MinerU service is up (safe to call when already running).
"%MINERU%" server start >nul 2>&1

:loop
if "%~1"=="" goto done
set "SRC=%~f1"
set "DIR=%~dp1"
set "BASE=%~n1"
set "SHORT=%BASE:~0,60%"
set "WORK=%DIR%%SHORT%_mineru"

echo.
echo ================================================================
echo   %BASE%
echo   output : %WORK%
echo ================================================================

if not exist "%WORK%" mkdir "%WORK%"

REM The zip is written to a short path inside the work folder. This avoids the
REM Windows 260-character MAX_PATH limit that breaks the web UI download button
REM on long literature filenames (it builds "<name>_markdown.zip" under a
REM ".bundle-xxxxxxxx" temp folder and the resulting path overflows).
"%KIT%" parse "%SRC%" -o "%WORK%\out.zip" --format zip --tier standard
if errorlevel 1 (
    echo   [FAILED] could not parse this file
    shift
    goto loop
)

tar -xf "%WORK%\out.zip" -C "%WORK%" markdown.md images
if exist "%WORK%\markdown.md" move /y "%WORK%\markdown.md" "%WORK%\%SHORT%.md" >nul
if exist "%WORK%\out.zip" del /q "%WORK%\out.zip"

echo   [OK] %WORK%\%SHORT%.md
shift
goto loop

:done
echo.
echo All done. Press any key to close.
pause >nul
exit /b 0

:usage
echo.
echo   MinerU - local document to Markdown (GPU, tier: standard)
echo.
echo   Drag one or more PDF / Office / image files onto this .cmd file.
echo   For every file a subfolder named _mineru is created next to it,
echo   containing the Markdown plus its images subfolder.
echo.
pause
exit /b 1
