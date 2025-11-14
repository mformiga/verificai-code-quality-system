from app.core.database import Base, engine
from app.models.prompt import GeneralAnalysisResult
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Testar conexão e ver dados
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Ver quantos resultados existem
    total_results = session.query(GeneralAnalysisResult).count()
    print(f"Total de resultados no banco: {total_results}")

    if total_results > 0:
        # Mostrar os resultados mais recentes
        results = session.query(GeneralAnalysisResult).order_by(GeneralAnalysisResult.created_at.desc()).limit(3).all()
        print("\nResultados mais recentes:")
        for result in results:
            print(f"\nID: {result.id}")
            print(f"Nome: {result.analysis_name}")
            print(f"User ID: {result.user_id}")
            print(f"Created: {result.created_at}")
            print(f"Criteria Results: {type(result.criteria_results)}")
            if result.criteria_results:
                print(f"  Keys: {list(result.criteria_results.keys()) if isinstance(result.criteria_results, dict) else 'Not a dict'}")
    else:
        print("Nenhum resultado encontrado no banco de dados")

    # Testar query SQL bruta
    print("\n=== Testando query SQL bruta ===")
    raw_results = session.execute(text("SELECT id, analysis_name, criteria_results FROM general_analysis_results LIMIT 5"))
    for row in raw_results:
        print(f"ID: {row.id}, Nome: {row.analysis_name}, Criteria: {type(row.criteria_results)}")

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()