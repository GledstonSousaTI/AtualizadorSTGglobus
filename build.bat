@echo off
:: ============================================================
:: Gera o executável .exe com PyInstaller
:: ============================================================
cd /d "%~dp0"

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Gerando executavel...
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "AtualizadorSTGGlobus" ^
    --add-data "app/config/config.json;app/config" ^
    --add-data "logs;logs" ^
    app/main.py

echo.
echo Executavel gerado em: dist\AtualizadorSTGGlobus.exe
pause
