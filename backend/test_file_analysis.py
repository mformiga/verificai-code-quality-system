from app.core.database import SessionLocal
from app.models.file_path import FilePath
from app.services.file_processor import FileProcessor
import asyncio

async def test_analysis():
    session = SessionLocal()
    try:
        # Obter o arquivo cadastrado
        file_path = session.query(FilePath).filter(FilePath.id == 210).first()
        if not file_path:
            print("Arquivo não encontrado!")
            return

        print(f"Testando análise do arquivo: {file_path.file_name}")
        print(f"Caminho: {file_path.full_path}")
        print("=" * 50)

        # Testar o processador de arquivos
        processor = FileProcessor()

        # Testar processamento do arquivo
        processed_file = await processor.process_file(file_path.full_path)

        if processed_file:
            print(f"✅ Arquivo processado com sucesso!")
            print(f"   - Linguagem: {processed_file.language}")
            print(f"   - Tamanho: {processed_file.size} bytes")
            print(f"   - Linhas: {processed_file.line_count}")
            print(f"   - Complexidade: {processed_file.complexity}")
            print(f"   - Palavras: {processed_file.word_count}")
            print(f"   - Caracteres: {processed_file.char_count}")

            # Mostrar primeiras linhas do conteúdo
            content_preview = processed_file.content[:200] + "..." if len(processed_file.content) > 200 else processed_file.content
            print(f"   - Preview: {content_preview}")
        else:
            print("❌ Falha ao processar o arquivo")

    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(test_analysis())