import os
import zipfile
import requests
from tqdm import tqdm
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "prestacao_contas_2024"

def baixar_arquivo(url, destino):
    """Baixa um arquivo com barra de progresso"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destino, 'wb') as file, tqdm(
        desc=destino.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def extrair_zip(arquivo_zip, pasta_destino):
    """Extrai arquivos ZIP mantendo a estrutura"""
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        zip_ref.extractall(pasta_destino)

def main():
    # Configurações
    URL_DADOS = "https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/prestacao_de_contas_eleitorais_orgaos_partidarios_2024.zip"
    ARQUIVO_ZIP = DATA_DIR / "prestacao_de_contas_2024.zip"

    # Criar diretórios se não existirem
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # 1. Baixar o arquivo
    print("⏳ Baixando arquivos do TSE...")
    baixar_arquivo(URL_DADOS, ARQUIVO_ZIP)

    # 2. Extrair o conteúdo
    print("📦 Extraindo arquivos...")
    extrair_zip(ARQUIVO_ZIP, RAW_DATA_DIR)

    # 3. Listar arquivos do RN
    arquivos_rn = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith("_RN.csv")]
    print(f"\n✅ Arquivos do RN encontrados ({len(arquivos_rn)}):")
    for arquivo in arquivos_rn:
        print(f" - {arquivo}")

if __name__ == "__main__":
    main()