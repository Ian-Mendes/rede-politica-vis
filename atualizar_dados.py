#!/usr/bin/env python3
import time
from datetime import datetime
import logging
from pathlib import Path

# Configuração de caminhos
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / 'atualizacao.log'),
        logging.StreamHandler()
    ]
)

def executar_pipeline():
    """Função para executar a pipeline principal"""
    try:
        from main import pipeline
        pipeline()
        return True
    except Exception as e:
        logging.error(f"Falha na execução da pipeline: {str(e)}")
        return False

def monitorar():
    """Monitora e executa a pipeline periodicamente"""
    logging.info("👀 Iniciando monitoramento de dados (Ctrl+C para sair)")
    
    while True:
        agora = datetime.now()
        
        # Executa toda segunda-feira às 5:00
        if agora.weekday() == 0 and agora.hour == 5:
            logging.info(f"⏰ Horário agendado detectado: {agora.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if executar_pipeline():
                logging.info("✅ Pipeline executada com sucesso")
            else:
                logging.warning("⚠️ Pipeline concluída com erros")
        
        # Verifica a cada hora
        time.sleep(3600)

if __name__ == "__main__":
    # Garante que o diretório de output existe
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    try:
        monitorar()
    except KeyboardInterrupt:
        logging.info("👋 Monitoramento encerrado pelo usuário")
    except Exception as e:
        logging.error(f"❌ Erro fatal no monitoramento: {str(e)}")