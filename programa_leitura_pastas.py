import os
import tkinter as tk
from tkinter import filedialog, messagebox

# --- CONFIGURAÇÃO ---
# Separador usado entre o conteúdo de cada arquivo no resultado final
SEPARADOR = "\n" + "="*80 + "\n"

def selecionar_pasta_e_processar():
    """Função principal que gerencia a seleção de pasta e o processamento."""
    
    # 1. Seleção da Pasta de Origem (Raiz)
    pasta_origem = filedialog.askdirectory(title="Selecione a Pasta PRINCIPAL para Varredura (Inclui Subpastas)")
    
    if not pasta_origem:
        return

    # 2. Seleção do Arquivo de Saída
    arquivo_saida = filedialog.asksaveasfilename(
        title="Salvar arquivo de saída consolidado como...",
        defaultextension=".txt",
        filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
    )

    if not arquivo_saida:
        return

    arquivos_processados = 0
    arquivos_ignorados = 0
    conteudo_total = [] # Lista para armazenar o conteúdo de cada arquivo

    try:
        # 3. Varre a pasta e subpastas de forma RECURSIVA (os.walk) e armazena o conteúdo
        for raiz, diretorios, arquivos in os.walk(pasta_origem):
            
            # Adiciona um separador de diretório para clareza
            if arquivos:
                conteudo_total.append(f"\n--- INÍCIO DOS ARQUIVOS EM: {raiz} ---\n")
            
            for arquivo in arquivos:
                caminho_completo = os.path.join(raiz, arquivo)
                
                # Obtém Metadados
                try:
                    tamanho = os.path.getsize(caminho_completo)
                    nome, extensao = os.path.splitext(arquivo)
                except OSError:
                    arquivos_ignorados += 1
                    continue 

                # Tenta Ler o Conteúdo do Arquivo
                conteudo = None
                
                try:
                    with open(caminho_completo, 'r', encoding='utf-8') as infile:
                        conteudo = infile.read()
                except UnicodeDecodeError:
                    try:
                        with open(caminho_completo, 'r', encoding='latin-1', errors='replace') as infile:
                            conteudo = infile.read()
                    except Exception:
                        conteudo = f"\n[*** CONTEÚDO IGNORADO: ARQUIVO BINÁRIO OU COM ERRO DE LEITURA (ex: Imagem, PDF, Executável) ***]\n"
                        arquivos_ignorados += 1

                # Insere o Cabeçalho e o Conteúdo na lista temporária
                if conteudo is not None:
                    # Cabeçalho Requerido: Nome, Tamanho, Extensão
                    conteudo_total.append(SEPARADOR)
                    conteudo_total.append(f"ARQUIVO: {arquivo}\n")
                    conteudo_total.append(f"TAMANHO: {tamanho} bytes\n")
                    conteudo_total.append(f"EXTENSÃO: {extensao.upper() if extensao else '[SEM EXTENSÃO]'}\n")
                    conteudo_total.append(SEPARADOR)
                    
                    # Conteúdo
                    conteudo_total.append(conteudo)
                    conteudo_total.append("\n") # Garante uma linha extra após o conteúdo

                    arquivos_processados += 1

        # 4. GERA O CABEÇALHO FINAL COM A CONTAGEM
        cabecalho_final = (
            f"================================================================================\n"
            f"| RELATÓRIO DE CONSOLIDAÇÃO DE ARQUIVOS\n"
            f"| QUANTIDADE TOTAL DE ARQUIVOS LIDOS E INSERIDOS: {arquivos_processados}\n"
            f"| Diretório base: {pasta_origem}\n"
            f"================================================================================\n\n"
        )
        
        # 5. ESCREVE O CONTEÚDO FINAL (Cabeçalho + Conteúdo Total)
        with open(arquivo_saida, 'w', encoding='utf-8') as outfile:
            outfile.write(cabecalho_final)
            outfile.writelines(conteudo_total)

        # Exibe a mensagem de sucesso
        messagebox.showinfo(
            "Sucesso", 
            f"Processo concluído!\n\n"
            f"Arquivos processados: {arquivos_processados}\n"
            f"Arquivos ignorados (binários/erros): {arquivos_ignorados}\n"
            f"Saída salva em: {arquivo_saida}"
        )

    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Ocorreu um erro: {e}")

# --- CONFIGURAÇÃO DA INTERFACE GRÁFICA (Tkinter) ---

root = tk.Tk()
root.title("Juntador de Arquivos Recursivo")
root.geometry("350x180")

label = tk.Label(
    root, 
    text="1. Clique para selecionar a Pasta Raiz.\n2. Escolha o nome do arquivo de saída.", 
    pady=15, 
    font=('Arial', 10)
)
label.pack()

btn = tk.Button(
    root, 
    text="INICIAR VARREDURA E CONSOLIDAR", 
    command=selecionar_pasta_e_processar, 
    bg='#4CAF50', 
    fg='white', 
    padx=15, 
    pady=10
)
btn.pack(pady=10)

root.mainloop()