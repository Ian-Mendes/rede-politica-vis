import pandas as pd
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt
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
    
    G_undirected = G.to_undirected()
    partition = community_louvain.best_partition(G_undirected, weight='weight')
    
    num_communities = len(set(partition.values()))
    print(f"Número de comunidades detectadas: {num_communities}")
    
    nx.set_node_attributes(G, partition, 'comunidade')
    
    print("\nExemplo de comunidades (10 primeiros nós):")
    print({k: v for k, v in list(partition.items())[:10]})
    
    return G, partition

def calcular_centralidades(G):
    """Calcula todas as medidas de centralidade e adiciona atributos aos nós"""
    print("\nCÁLCULO DE CENTRALIDADES:")
    
    degree_cent = nx.degree_centrality(G)
    try:
        eigen_cent = nx.eigenvector_centrality_numpy(G, weight='weight', max_iter=1000)
    except Exception as e:
        print(f"Eigenvector centrality não pôde ser calculada: {str(e)}")
        eigen_cent = {n: 0 for n in G.nodes()}
    closeness_cent = nx.closeness_centrality(G, wf_improved=True)
    betweenness_cent = nx.betweenness_centrality(G, weight='weight')
    
    # Adiciona centralidades como atributos do nó
    nx.set_node_attributes(G, degree_cent, 'degree_cent')
    nx.set_node_attributes(G, eigen_cent, 'eigen_cent')
    nx.set_node_attributes(G, closeness_cent, 'closeness_cent')
    nx.set_node_attributes(G, betweenness_cent, 'betweenness_cent')
    
    # DataFrames top 10 (opcional)
    def top_nodes(cent_dict, name):
        return (pd.DataFrame(sorted(cent_dict.items(), key=lambda x: x[1], reverse=True)[:10], 
                             columns=['Nó', name]).reset_index(drop=True))
    
    df_degree = top_nodes(degree_cent, 'Degree')
    df_eigen = top_nodes(eigen_cent, 'Eigenvector')
    df_closeness = top_nodes(closeness_cent, 'Closeness')
    df_betweenness = top_nodes(betweenness_cent, 'Betweenness')
    
    df_centralidades = pd.concat([df_degree, df_eigen, df_closeness, df_betweenness], axis=1)
    
    caminho_centralidades = OUTPUT_DIR / "centralidades.csv"
    df_centralidades.to_csv(caminho_centralidades, index=False)
    print(f"\nCentralidades salvas em: {caminho_centralidades}")
    
    return df_centralidades

def visualizar_grafo_interativo(G):
    """Visualiza grafo interativo com tamanho e labels"""
    DOCS_DIR.mkdir(exist_ok=True)
    
    net = Network(
        notebook=False,
        directed=True,
        width="1000px",
        height="700px",
        bgcolor="#222222",
        font_color="white"
    )
    
    comunidades = nx.get_node_attributes(G, 'comunidade')
    cores = plt.cm.tab20.colors  # 20 cores
    
    for node in G.nodes():
        comunidade = comunidades.get(node, 0)
        cor = cores[comunidade % len(cores)]
        cor_hex = '#%02x%02x%02x' % tuple(int(255*x) for x in cor[:3])
        
        # Pega centralidades para tooltip e tamanho
        degree = G.nodes[node].get('degree_cent', 0)
        eigen = G.nodes[node].get('eigen_cent', 0)
        closeness = G.nodes[node].get('closeness_cent', 0)
        betweenness = G.nodes[node].get('betweenness_cent', 0)
        
        tooltip = (
            f"{node}\n"
            f"Comunidade: {comunidade}\n"
            f"Degree: {degree:.4f}\n"
            f"Eigenvector: {eigen:.4f}\n"
            f"Closeness: {closeness:.4f}\n"
            f"Betweenness: {betweenness:.4f}"
        )
        
        tamanho = 15 + degree * 50  # tamanho baseado no degree centrality
        
        net.add_node(
            node,
            label=node,   # label visível
            color=cor_hex,
            title=tooltip,
            size=tamanho
        )
    
    for source, target, data in G.edges(data=True):
        net.add_edge(
            source,
            target,
            value=data['weight'],
            title=f"Valor: R$ {data['weight']:,.2f}"
        )
    
    net.repulsion(
        node_distance=200,
        central_gravity=0.2,
        spring_length=200,
        spring_strength=0.05,
        damping=0.09
    )
    
    caminho_html = DOCS_DIR / "index.html"
    net.save_graph(str(caminho_html))
    print(f"\n✅ Grafo interativo salvo em: {caminho_html}")

def main(grafo=None):
    print("Iniciando análise exploratória...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)
    
    G = grafo if grafo else carregar_dados()
    G, partition = detectar_comunidades(G)
    df_centralidades = calcular_centralidades(G)
    
    print("\nTop 10 por cada medida de centralidade:")
    print(df_centralidades)
    
    visualizar_grafo_interativo(G)
    
    print("\nAnálise concluída! Verifique os arquivos:")
    print(f"- Visualização: {DOCS_DIR / 'index.html'}")
    print(f"- Dados: {OUTPUT_DIR / 'centralidades.csv'}")

if __name__ == "__main__":
    main()
