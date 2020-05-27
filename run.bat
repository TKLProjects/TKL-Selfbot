@echo off
SET root=%~dp0
CD /D %root%
python -V >nul 2>&1 || goto :python
goto run

:python
	TITLE Error!
	echo Python not added to PATH or not installed. Download Python 3.6 or higher, follow the README on Github for instructions.
	echo Press any key to exit.
	pause >nul
	CD /D "%root%"
	goto :EOF
:run
	echo Checking requirements...
	chcp 65001 >nul
  set PYTHONIOENCODING=utf-8
  python -m pip install --upgrade pip >nul
	python -m pip install -r requirements.txt >nul
	echo Requirements updated.
	echo Starting the bot (may take up to a minute)...
	python loop.py
