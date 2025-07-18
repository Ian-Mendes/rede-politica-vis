import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "prestacao_contas_2024"
PROCESSED_DIR = DATA_DIR / "processed"

def carregar_dataframes(folder):
    """Carrega todos os arquivos CSV do diretório especificado"""
    arquivos_rn = [f for f in os.listdir(folder) if f.endswith("_RN.csv")]
    dfs = {}
    
    for arquivo in arquivos_rn:
        caminho = folder / arquivo
        nome_base = arquivo.replace("_2024_RN.csv", "").lower()
        
        try:
            dfs[nome_base] = pd.read_csv(
                caminho, 
                sep=';', 
                encoding='latin1',
                on_bad_lines='warn'
            )
            print(f"✅ {arquivo} carregado ({dfs[nome_base].shape[0]} registros)")
        except Exception as e:
            print(f"❌ Erro em {arquivo}: {str(e)}")
    
    return dfs

def processar_dados(dfs):
    """Processa e consolida os DataFrames"""
    # Merge entre receitas e doadores
    if 'receitas_orgaos_partidarios' in dfs and 'receitas_orgaos_partidarios_doador_originario' in dfs:
        dfs['receitas_consolidadas'] = pd.merge(
            dfs['receitas_orgaos_partidarios_doador_originario'],
            dfs['receitas_orgaos_partidarios'][['SQ_RECEITA', 'SG_PARTIDO', 'NM_PARTIDO']],
            on='SQ_RECEITA',
            how='left'
        )
    
    return dfs

def salvar_em_csv(dfs, output_folder=PROCESSED_DIR):
    """Salva todos os DataFrames como CSV"""
    os.makedirs(output_folder, exist_ok=True)
    
    for nome, df in dfs.items():
        caminho = output_folder / f"{nome}.csv"
        df.to_csv(caminho, index=False, sep=';', encoding='latin1')
        print(f"💾 {nome}.csv salvo ({df.shape[0]} registros)")

def main():
    print("\n📂 Carregando arquivos...")
    dataframes = carregar_dataframes(RAW_DATA_DIR)
    
    print("\n🔗 Processando dados...")
    dataframes = processar_dados(dataframes)
    
    print("\n💾 Salvando resultados...")
    salvar_em_csv(dataframes)
    
    print("\n✅ Concluído! Arquivos salvos em:", PROCESSED_DIR.resolve())

if __name__ == "__main__":
    main()