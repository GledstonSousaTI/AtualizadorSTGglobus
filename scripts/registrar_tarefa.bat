@echo off
:: ============================================================
:: Registra as tarefas de sincronizacao no Windows Task Scheduler
:: Execute como Administrador
:: ============================================================

set "PROJETO_DIR=%~dp0.."
set "SCRIPT=%~dp0run_sync.bat"

echo Registrando tarefas no Agendador de Tarefas do Windows...
echo Diretorio do projeto: %PROJETO_DIR%
echo Script: %SCRIPT%
echo.

schtasks /Create /F /TN "AtualizadorSTGGlobus" /TR "cmd /c \"%SCRIPT%\" --table funcionarios" /SC DAILY /ST "01:00" /RL HIGHEST

if %ERRORLEVEL% == 0 (
    echo [OK] AtualizadorGlobus_funcionarios - diario as 01:00
) else (
    echo [ERRO] Falha ao criar tarefa. Execute como Administrador.
)

echo.
echo Feito. Verifique em: Agendador de Tarefas ^> Biblioteca ^> AtualizadorGlobus_*
pause
