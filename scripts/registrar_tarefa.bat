@echo off
:: ============================================================
:: Registra as tarefas de sincronização no Windows Task Scheduler
:: Execute como Administrador
:: ============================================================

set "PROJETO_DIR=%~dp0.."
set "PYTHON_EXE=python"
set "SCRIPT=%PROJETO_DIR%\scripts\run_sync.bat"

echo Registrando tarefas no Agendador de Tarefas do Windows...
echo Diretorio do projeto: %PROJETO_DIR%
echo.

:: --- Lê as tabelas do config.json via Python e cria uma tarefa para cada ---
python -c "
import json, subprocess, sys, os

config_path = os.path.join(r'%PROJETO_DIR%', 'app', 'config', 'config.json')
with open(config_path, encoding='utf-8') as f:
    cfg = json.load(f)

script = os.path.join(r'%PROJETO_DIR%', 'scripts', 'run_sync.bat')

for tab in cfg.get('tabelas', []):
    if not tab.get('ativo', True):
        continue

    tabela_id = tab['id']
    horario = tab.get('horario', '01:00')
    nome_tarefa = f'AtualizadorGlobus_{tabela_id}'

    cmd = [
        'schtasks', '/Create', '/F',
        '/TN', nome_tarefa,
        '/TR', f'cmd /c \"{script}\" --table {tabela_id}',
        '/SC', 'DAILY',
        '/ST', horario,
        '/RL', 'HIGHEST',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f'  [OK] {nome_tarefa} - diario as {horario}')
    else:
        print(f'  [ERRO] {nome_tarefa}: {result.stderr.strip()}')
"

echo.
echo Feito. Verifique em: Agendador de Tarefas > Biblioteca > AtualizadorGlobus_*
pause
