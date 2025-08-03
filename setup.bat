@echo off
setlocal enabledelayedexpansion

goto :main

:print
powershell -command "Write-host %1 -ForegroundColor %2"
exit /b


:main

set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/c cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

for /f "tokens=3 delims=\" %%a in ("!cd!") do set "username=%%a"
set "NEWUSER=C:\Users\%username%"

call :print "Copying files" Yellow
set "pseudo=%NEWUSER%\pseudo"
xcopy %cd% "%pseudo%" /E /I /Y > nul
cd /d "%pseudo%"
call :print "Copied files to %pseudo%" Green

echo.

call :print "Adding path to system environment variables" Yellow
echo %PATH% | find /i "%cd%" > nul
if errorlevel 1 (
    setx /m PATH "%PATH%;%cd%"
    call :print "%cd% added to system environment variables" Green
) else (
    call :print "%cd% already exists in system environment variables" Yellow
)

echo.
pause