import pandas as pd
import networkx as nx
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def parse_valor(valor):
    """Converte valores monetários para float"""
    if isinstance(valor, str):
        valor_limpo = valor.replace('.', '').replace(',', '.').replace(' ', '').replace('R$', '')
        try:
            return float(valor_limpo)
        except:
            return 0.0
    return float(valor) if pd.notna(valor) else 0.0

def criar_grafo_doacoes():
    """Cria e analisa grafo de doações partidárias"""
    print("\nANÁLISE DE DOAÇÕES PARTIDÁRIAS")
    print("----------------------------")
    
    # Carrega os dados
    caminho = PROCESSED_DIR / "receitas_consolidadas.csv"
    try:
        df = pd.read_csv(caminho, sep=';', encoding='latin1', low_memory=False)
    except FileNotFoundError:
        print(f"Arquivo {caminho} não encontrado!")
        return None
    
    # Processa os valores
    df['VR_RECEITA'] = df['VR_RECEITA'].apply(parse_valor)
    df = df[df['VR_RECEITA'] > 0]  # Filtra doações positivas
    
    # Cria o grafo direcionado
    G = nx.DiGraph()
    
    for _, row in df.iterrows():
        doador = str(row['NM_DOADOR_ORIGINARIO']).strip()
        partido = str(row['SG_PARTIDO']).strip()
        valor = row['VR_RECEITA']
        
        if doador and partido:
            if G.has_edge(doador, partido):
                G[doador][partido]['weight'] += valor
            else:
                G.add_edge(doador, partido, weight=valor)
    
    # Análise do grafo
    print(f"\nESTATÍSTICAS:")
    print(f"Total de doadores: {len({n for n in G.nodes() if n in df['NM_DOADOR_ORIGINARIO'].values})}")
    print(f"Total de partidos: {len({n for n in G.nodes() if n in df['SG_PARTIDO'].values})}")
    print(f"Conexões (doador->partido): {G.number_of_edges()}")
    
    # Top partidos por receita
    receita_partidos = {}
    for origem, destino, data in G.edges(data=True):
        if destino not in receita_partidos:
            receita_partidos[destino] = 0
        receita_partidos[destino] += data['weight']
    
    print("\nTOP 5 PARTIDOS POR RECEITA:")
    for partido, valor in sorted(receita_partidos.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{partido}: R$ {valor:,.2f}")
    
    return G

if __name__ == "__main__":
    grafo_doacoes = criar_grafo_doacoes()