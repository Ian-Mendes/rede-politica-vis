import pandas as pd
import networkx as nx
from pyvis.network import Network
import plotly.express as px
import matplotlib.pyplot as plt
import os
import numpy as np
from community import community_louvain
from pathlib import Path

# Configuração de caminhos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "output"
DOCS_DIR = BASE_DIR / "docs"

def carregar_dados():
    """Carrega o grafo a partir dos dados processados"""
    caminho = PROCESSED_DIR / "receitas_consolidadas.csv"
    df = pd.read_csv(caminho, sep=';', encoding='latin1')
    
    # Processamento dos dados
    df['VR_RECEITA'] = df['VR_RECEITA'].str.replace('.', '').str.replace(',', '.').astype(float)
    df = df[df['VR_RECEITA'] > 0]
    
    # Criação do grafo
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
    
    return G

def detectar_comunidades(G):
    """Detecta comunidades usando o algoritmo de Louvain"""
    print("\nDETECÇÃO DE COMUNIDADES:")
    
    # Converte para grafo não-direcionado
    G_undirected = G.to_undirected()
    
    # Calcula a partição ótima
    partition = community_louvain.best_partition(G_undirected, weight='weight')
    
    # Número de comunidades
    num_communities = len(set(partition.values()))
    print(f"Número de comunidades detectadas: {num_communities}")
    
    # Adiciona a comunidade como atributo aos nós
    nx.set_node_attributes(G, partition, 'comunidade')
    
    # Exemplo: mostra 10 nós e suas comunidades
    print("\nExemplo de comunidades (10 primeiros nós):")
    print({k: v for k, v in list(partition.items())[:10]})
    
    return G, partition

def calcular_centralidades(G):
    """Calcula todas as medidas de centralidade"""
    print("\nCÁLCULO DE CENTRALIDADES:")
    
    # 1. Degree Centrality
    degree_cent = nx.degree_centrality(G)
    
    # 2. Eigenvector Centrality (para o maior componente fortemente conectado)
    try:
        eigen_cent = nx.eigenvector_centrality_numpy(G, weight='weight', max_iter=1000)
    except Exception as e:
        print(f"Eigenvector centrality não pôde ser calculada: {str(e)}")
        eigen_cent = {n: 0 for n in G.nodes()}
    
    # 3. Closeness Centrality (versão para grafos desconectados)
    closeness_cent = nx.closeness_centrality(G, wf_improved=True)
    
    # 4. Betweenness Centrality
    betweenness_cent = nx.betweenness_centrality(G, weight='weight')
    
    # Cria DataFrames com os top 10 de cada centralidade
    def top_nodes(cent_dict, name):
        return (pd.DataFrame(sorted(cent_dict.items(), key=lambda x: x[1], reverse=True)[:10], 
                columns=['Nó', name])
                .reset_index(drop=True))
    
    df_degree = top_nodes(degree_cent, 'Degree')
    df_eigen = top_nodes(eigen_cent, 'Eigenvector')
    df_closeness = top_nodes(closeness_cent, 'Closeness')
    df_betweenness = top_nodes(betweenness_cent, 'Betweenness')
    
    # Combina todos os resultados
    df_centralidades = pd.concat([df_degree, df_eigen, df_closeness, df_betweenness], axis=1)
    
    # Salva em CSV
    caminho_centralidades = OUTPUT_DIR / "centralidades.csv"
    df_centralidades.to_csv(caminho_centralidades, index=False)
    print(f"\nCentralidades salvas em: {caminho_centralidades}")
    
    return df_centralidades

def visualizar_grafo_interativo(G):
    """Cria visualização interativa do grafo com comunidades"""
    # Garante que a pasta docs existe
    DOCS_DIR.mkdir(exist_ok=True)
    
    net = Network(
        notebook=False,
        directed=True,
        width="1000px",
        height="700px",
        bgcolor="#222222",
        font_color="white"
    )
    
    # Adiciona nós e arestas com cores por comunidade
    comunidades = nx.get_node_attributes(G, 'comunidade')
    cores = plt.cm.tab20.colors  # Paleta de 20 cores
    
    for node in G.nodes():
        comunidade = comunidades.get(node, 0)
        cor = cores[comunidade % len(cores)]
        cor_hex = '#%02x%02x%02x' % tuple(int(255*x) for x in cor[:3])
        net.add_node(
            node, 
            color=cor_hex,
            title=f"{node}\nComunidade: {comunidade}",
            size=20
        )
    
    for edge in G.edges(data=True):
        net.add_edge(
            edge[0], 
            edge[1], 
            value=edge[2]['weight'],
            title=f"Valor: R$ {edge[2]['weight']:,.2f}"
        )
    
    # Configurações de visualização
    net.repulsion(
        node_distance=200,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    )
    
    # Salva o arquivo HTML na pasta docs
    caminho_html = DOCS_DIR / "index.html"
    try:
        net.save_graph(str(caminho_html))  # Convertendo para string
        print(f"\n✅ Grafo interativo salvo em: {caminho_html}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar grafo: {str(e)}")
        raise

def main(grafo=None):
    print("Iniciando análise exploratória...")
    
    # Garante que os diretórios existem
    OUTPUT_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)
    
    # Carrega e processa os dados
    G = grafo if grafo else carregar_dados()
    
    # Detecção de comunidades
    G, partition = detectar_comunidades(G)
    
    # Cálculo de centralidades
    df_centralidades = calcular_centralidades(G)
    print("\nTop 10 por cada medida de centralidade:")
    print(df_centralidades)
    
    # Visualização interativa
    visualizar_grafo_interativo(G)
    
    print("\nAnálise concluída! Verifique os arquivos:")
    print(f"- Visualização: {DOCS_DIR / 'index.html'}")
    print(f"- Dados: {OUTPUT_DIR / 'centralidades.csv'}")

if __name__ == "__main__":
    main()