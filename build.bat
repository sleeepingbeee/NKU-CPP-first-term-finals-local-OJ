@echo off
setlocal
set "SRC=%~1"
set "OUT=%~2"
set "VCVARS=%OJ_VCVARS%"
if defined VCVARS if not exist "%VCVARS%" set "VCVARS="
if defined VCVARS goto :have
set "VSWHERE=C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" goto :fallback
for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VS=%%i"
if not defined VS goto :fallback
if not exist "%VS%\VC\Auxiliary\Build\vcvars64.bat" goto :fallback
set "VCVARS=%VS%\VC\Auxiliary\Build\vcvars64.bat"
goto :have
:fallback
set "VCVARS=D:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
:have
if not exist "%VCVARS%" (
  echo [build] vcvars64.bat NOT FOUND: %VCVARS%
  exit /b 2
)
call "%VCVARS%" >nul 2>&1
cl /nologo /EHsc /O2 /std:c++17 /utf-8 /Fe:"%OUT%" "%SRC%"
exit /b %errorlevel%
