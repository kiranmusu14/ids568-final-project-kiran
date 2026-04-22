@echo off
setlocal enabledelayedexpansion

set PYTHON_BIN=python
where py >nul 2>nul
if %ERRORLEVEL%==0 set PYTHON_BIN=py -3.13

%PYTHON_BIN% -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import importlib; [importlib.import_module(m) for m in ['fastapi','uvicorn','prometheus_client','dotenv','PIL']]; print('Environment verification passed.')"
