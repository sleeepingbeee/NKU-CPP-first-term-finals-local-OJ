@echo off
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
where python >nul 2>&1
if errorlevel 1 (
  if exist "D:\Program Files (x86)\python\python.exe" (
    "D:\Program Files (x86)\python\python.exe" -X utf8 server.py %*
    goto :done
  )
  echo [!] 找不到 python，请先安装 Python 3 并加入 PATH。
  pause
  exit /b 1
)
python -X utf8 server.py %*
:done
if errorlevel 1 pause
