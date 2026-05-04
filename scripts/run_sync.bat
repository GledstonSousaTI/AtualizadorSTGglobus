@echo off
cd /d "%~dp0.."
set "PYTHONPATH=%~dp0.."
C:\Users\gledston.sousa\AppData\Local\Programs\Python\Python313\python.exe -m app.core.sync_engine %*
