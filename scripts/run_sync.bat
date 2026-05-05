@echo off
cd /d "%~dp0.."
set "PYTHONPATH=%~dp0.."

echo ============================================
echo  AtualizadorSTG Globus - Sincronizacao
echo ============================================
echo  Inicio: %DATE% %TIME%
echo.

python -m app.core.sync_engine %*

echo.
echo  Fim: %DATE% %TIME%
echo ============================================

:: Pausa somente quando executado manualmente (duplo clique)
:: Quando chamado pelo Task Scheduler, nao pausa
echo %SESSIONNAME% | find /i "Console" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo.
    echo  Pressione qualquer tecla para fechar...
    pause >nul
)
