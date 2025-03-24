import os
import subprocess

# Caminho completo do pyinstaller
pyinstaller_path = r"C:\Users\lnsan\AppData\Local\Programs\Python\Python311\Scripts\pyinstaller.exe"

# Direção do seu projeto
diretorio_projeto = "C:/Users/lnsan/projeto-flinn"

# Função para gerar todos os caminhos de arquivos, excluindo pastas "venv"
def incluir_arquivos(diretorio):
    arquivos = []
    for root, dirs, files in os.walk(diretorio):
        # Ignorar diretórios 'venv'
        dirs[:] = [d for d in dirs if d != 'venv']
        
        for file in files:
            caminho_arquivo = os.path.join(root, file)
            destino = os.path.relpath(caminho_arquivo, diretorio)
            arquivos.append(f"{caminho_arquivo};{destino}")
    
    return arquivos

# Obtendo todos os arquivos e caminhos relativos
arquivos_incluidos = incluir_arquivos(diretorio_projeto)

# Montando o comando PyInstaller com todos os arquivos
comando = [pyinstaller_path, "--onefile", "--windowed"]
for arquivo in arquivos_incluidos:
    comando.append(f"--add-data {arquivo}")

comando.append("main.py")

# Executando o comando no terminal
print(comando)
