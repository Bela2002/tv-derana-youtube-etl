@echo off

cd /d "%~dp0"

call ".venv\Scripts\activate.bat"

python -m src.main

if %ERRORLEVEL% NEQ 0 (
    echo ETL process failed.
    exit /b %ERRORLEVEL%
)

echo ETL process completed successfully.