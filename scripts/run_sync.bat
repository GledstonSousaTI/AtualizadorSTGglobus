@echo off
cd /d "%~dp0.."
set "PYTHONPATH=%~dp0.."

:: Detecta o Python disponivel
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    set "PYTHON=python"
) else (
    :: fallback para caminhos comuns
    if exist "C:\Users\administrator\AppData\Local\Programs\Python\Python312\python.exe" (
        set "PYTHON=C:\Users\administrator\AppData\Local\Programs\Python\Python312\python.exe"
    ) else if exist "C:\Users\gledston.sousa\AppData\Local\Programs\Python\Python313\python.exe" (
        set "PYTHON=C:\Users\gledston.sousa\AppData\Local\Programs\Python\Python313\python.exe"
    ) else (
        echo [ERRO] Python nao encontrado. Configure a variavel PYTHON no topo deste arquivo.
        exit /b 1
    )
)

echo ============================================
echo  AtualizadorSTG Globus - Sincronizacao
echo ============================================
echo  Inicio: %DATE% %TIME%
echo.

%PYTHON% -m app.core.sync_engine %*

echo.
echo  Fim: %DATE% %TIME%
echo ============================================

:: Pausa somente quando executado manualmente (duplo clique)
echo %SESSIONNAME% | find /i "Console" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo.
    echo  Pressione qualquer tecla para fechar...
    pause >nul
)
