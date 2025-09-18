@echo off
echo === Iniciando VerificAI com PostgreSQL ===

:: 1. Configurar PostgreSQL
echo 1. Configurando PostgreSQL...
python setup-postgres.py
if errorlevel 1 (
    echo ERRO: Falha ao configurar PostgreSQL
    pause
    exit /b 1
)

:: 2. Instalar dependências
echo 2. Instalando dependências...
call npm run install:all

:: 3. Iniciar aplicação
echo 3. Iniciando aplicação...
call npm run dev

echo Aplicação iniciada!
pause