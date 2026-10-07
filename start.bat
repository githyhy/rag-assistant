@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Autonomous Driving RAG Assistant  -  Launcher
echo ============================================================
echo.

REM ---------- 1. virtual environment ----------
if not exist ".venv\Scripts\python.exe" (
    echo [X] Virtual environment not found: .venv
    echo     Create it in PyCharm, or run: py -m venv .venv
    echo.
    pause
    exit /b 1
)
echo [OK] Virtual environment ready

REM ---------- 2. dependencies ----------
".venv\Scripts\python.exe" -c "import fastapi, uvicorn, openai, chromadb" 2>nul
if errorlevel 1 (
    echo [!] Dependencies missing, installing...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [X] Failed to install dependencies
        pause
        exit /b 1
    )
)
echo [OK] Dependencies ready

REM ---------- 3. vector store ----------
if not exist "chroma_db" (
    echo [!] Vector store not found, building...
    ".venv\Scripts\python.exe" ingest.py
    if errorlevel 1 (
        echo [X] Ingest failed. Please check the API key in .env
        pause
        exit /b 1
    )
)
echo [OK] Vector store ready

REM ---------- 4. start server ----------
echo.
echo ============================================================
echo   Starting server ...
echo   Chat UI  : http://127.0.0.1:8000
echo   API docs : http://127.0.0.1:8000/docs
echo   Press Ctrl+C to stop
echo ============================================================
echo.

REM open browser 3 seconds later
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000"

".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000

echo.
echo Server stopped.
pause
