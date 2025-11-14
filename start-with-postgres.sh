#!/bin/bash

# Script de inicialização do VerificAI com PostgreSQL
echo "=== Iniciando VerificAI com PostgreSQL ==="

# 1. Configurar PostgreSQL
echo "1. Configurando PostgreSQL..."
python setup-postgres.py
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao configurar PostgreSQL"
    exit 1
fi

# 2. Instalar dependências
echo "2. Instalando dependências..."
npm run install:all

# 3. Iniciar aplicação
echo "3. Iniciando aplicação..."
npm run dev

echo "Aplicação iniciada!"