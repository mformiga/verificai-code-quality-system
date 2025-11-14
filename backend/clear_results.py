#!/usr/bin/env python3
"""
Script para limpar o banco de dados de resultados de análise
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import get_db
from app.models.prompt import GeneralAnalysisResult

def clear_analysis_results():
    """Limpa todos os resultados de análise do banco de dados"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Contar quantos resultados existem
        count = db.query(GeneralAnalysisResult).count()
        print(f"Encontrados {count} resultados de análise no banco de dados")

        if count > 0:
            # Deletar todos os resultados
            db.query(GeneralAnalysisResult).delete()
            db.commit()
            print(f"OK: {count} resultados de análise foram deletados com sucesso")
        else:
            print("OK: Nenhum resultado de análise encontrado para deletar")

        # Verificar se realmente foram deletados
        remaining = db.query(GeneralAnalysisResult).count()
        print(f"OK: Resultados restantes no banco: {remaining}")

    except Exception as e:
        print(f"ERRO: Erro ao limpar resultados: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    clear_analysis_results()