@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Power BI UX MCP - Instalador
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Criando ambiente virtual...
python -m venv .venv
if errorlevel 1 (
    echo.
    echo ❌ Erro: Python não encontrado ou erro ao criar venv
    echo    Certifique-se de ter Python 3.12 instalado
    pause
    exit /b 1
)

echo [2/4] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo [3/4] Instalando dependências...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

echo [4/4] Configurando IDEs...
python setup_mcp.py

echo.
echo ========================================
echo   ✅ Instalação concluída!
echo ========================================
echo.
echo Próximos passos:
echo   1. Reinicie sua IDE
echo   2. Abra o Power BI Desktop
echo   3. Use o MCP 'powerbi-ux'
echo.
pause
