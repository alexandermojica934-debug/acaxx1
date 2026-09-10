@echo off
REM ACASO Local Node launcher (Windows). Edit the two values below.
set ACASO_URL=https://contest-ready-app.preview.emergentagent.com
set ACASO_KEY=PASTE_YOUR_AGENT_BRIDGE_KEY_HERE
set ROOT=%USERPROFILE%\ACASO
if not exist "%ROOT%" mkdir "%ROOT%"
python "%~dp0acaso_node.py" --root "%ROOT%" --shell --browser --companion
pause
