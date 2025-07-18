import os
import logging
from pathlib import Path
from datetime import datetime

# Configuração de caminhos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "prestacao_contas_2024"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "output"

def setup_logging():
    """Configura o sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(OUTPUT_DIR / 'pipeline.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def run_import():
    """Executa a importação de dados"""
    from importacao_arquivo import main as importar_dados
    importar_dados()

def run_processing():
    """Executa o processamento dos dados"""
    from criar_df import main as processar_dados
    processar_dados()

def run_analysis():
    """Executa a análise do grafo"""
    from criar_grafo import criar_grafo_doacoes
    from analise_exploratoria import main as analisar_dados
    
    grafo = criar_grafo_doacoes()
    if grafo:
        analisar_dados(grafo)

def main():
    """Pipeline principal"""
    start_time = datetime.now()
    
    # Garante que os diretórios existam
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    setup_logging()
    logging.info("Iniciando pipeline de análise política")
    
    try:
        # Verifica se já existem dados processados
        if not list(PROCESSED_DIR.glob('*.csv')):
            logging.info("Etapa 1/3: Importando dados")
            run_import()
        
        logging.info("Etapa 2/3: Processando dados")
        run_processing()
        
        logging.info("Etapa 3/3: Analisando dados")
        run_analysis()
        
        logging.info(f"Pipeline concluída com sucesso em {datetime.now() - start_time}")
    
    except Exception as e:
        logging.error(f"Erro na pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()