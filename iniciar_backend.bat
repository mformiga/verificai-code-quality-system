@echo off
cd /d "C:\Users\formi\teste_gemini\dev\verificAI-code\backend"
echo Iniciando backend na porta 3011...
python -m uvicorn app.main:app --host 0.0.0.0 --port 3011
pause