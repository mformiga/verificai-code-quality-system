#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def check_streamlit_health():
    """Verifica se a aplicação está saudável"""

    try:
        # Tenta conectar ao Streamlit
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Streamlit está respondendo")
            return True
        else:
            print(f"[AVISO] Streamlit respondeu com status: {response.status_code}")
            return False
    except:
        print("[INFO] Verificando via HTTP principal...")
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print("[OK] Aplicação acessível via HTTP")
                return True
            else:
                print(f"[ERRO] Aplicação respondeu com: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERRO] Não foi possível conectar: {e}")
            return False

def main():
    print("=== VERIFICAÇÃO AVALIA APP ===")
    print("Aguardando aplicação iniciar...")

    # Aguarda um pouco
    time.sleep(2)

    if check_streamlit_health():
        print("\n✅ Aplicação está rodando!")
        print("\n📋 Para testar:")
        print("1. Abra: http://localhost:8501")
        print("2. Teste registro de usuário")
        print("3. Teste upload de arquivo .py")
        print("4. Verifique análise de código")
        print("5. Confirme se histórico é salvo")

        print("\n🚀 Se tudo funcionar, você está pronto para deploy!")
        print("   - Faça push para GitHub")
        print("   - Configure secrets no Streamlit Cloud")
        print("   - Deploy!")

    else:
        print("\n❌ Aplicação não está respondendo")
        print("Verifique se há erros no console")

if __name__ == "__main__":
    main()