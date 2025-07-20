import os
import requests
import zipfile
import pandas as pd
import networkx as nx
from pyvis.network import Network
import community as community_louvain


def download_and_unzip(url, output_folder, zip_name="data.zip"):
    print("📥 Baixando dataset...")
    response = requests.get(url)
    with open(zip_name, 'wb') as f:
        f.write(response.content)

    print("📦 Descompactando dataset...")
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(output_folder)

    os.remove(zip_name)
    print("✅ Download e descompactação concluídos.")


def carregar_dados(pasta):
    df_receitas = pd.read_csv(
        os.path.join(pasta, "receitas_orgaos_partidarios_2024_RN.csv"),
        sep=';', encoding='latin1', decimal=','
    )
    df_doador = pd.read_csv(
        os.path.join(pasta, "receitas_orgaos_partidarios_doador_originario_2024_RN.csv"),
        sep=';', encoding='latin1', decimal=','
    )
    # Merge
    df_merge = pd.merge(
        df_doador,
        df_receitas[["SQ_RECEITA", "SG_PARTIDO", "NM_PARTIDO"]],
        on="SQ_RECEITA",
        how="left"
    )
    # Remover doador #NULO
    df_merge = df_merge[df_merge["NM_DOADOR_ORIGINARIO"] != "#NULO"]
    return df_merge


def calcular_metricas(G):
    metrics = {}
    metrics["closeness"] = nx.closeness_centrality(G)
    metrics["degree"] = dict(G.degree())
    metrics["eigenvector"] = nx.eigenvector_centrality(G, max_iter=1000)
    metrics["betweenness"] = nx.betweenness_centrality(G)
    return metrics


def construir_rede(df):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        doador = row.get("NM_DOADOR_ORIGINARIO", "DOADOR_DESCONHECIDO")
        partido = row.get("SG_PARTIDO", "PARTIDO_DESCONHECIDO")
        valor = row.get("VR_RECEITA", 0)

        G.add_node(doador, type="doador")
        G.add_node(partido, type="partido")
        G.add_edge(doador, partido, weight=valor)
    return G


def gerar_visualizacao(G, metrics, partition, output_html="docs/rede.html"):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False, directed=True)

    # Gerar lista única de comunidades e um mapa para cores
    comunidades = set(partition.values())
    palette = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
               '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe']
    color_map = {com: palette[i % len(palette)] for i, com in enumerate(comunidades)}

    # Adicionar nós com cor da comunidade + métricas no tooltip
    for node in G.nodes():
        com = partition.get(node, -1)
        color = color_map.get(com, '#ffffff')  # branco se não encontrado
        title = (
            f"<b>Nome:</b> {node}<br>"
            f"<b>Comunidade:</b> {com}<br>"
            f"<b>Degree Centrality:</b> {metrics['degree'].get(node, 0):.4f}<br>"
            f"<b>Closeness Centrality:</b> {metrics['closeness'].get(node, 0):.4f}<br>"
            f"<b>Eigenvector Centrality:</b> {metrics['eigenvector'].get(node, 0):.4f}<br>"
            f"<b>Betweenness Centrality:</b> {metrics['betweenness'].get(node, 0):.4f}"
        )
        net.add_node(node, label=node, title=title, color=color)

    # Adicionar arestas
    for u, v, data in G.edges(data=True):
        valor = data.get("weight", 1)
        width = max(1, valor / 1000)
        title = f"Valor da doação: R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        net.add_edge(u, v, value=valor, width=width, title=title)

    # Criar pasta docs se não existir
    os.makedirs("docs", exist_ok=True)
    net.write_html(output_html)
    print(f"🌐 Rede salva como {output_html}")


def detectar_comunidades(G):
    partition = community_louvain.best_partition(G.to_undirected())
    return partition


def main():
    url = "https://cdn.tse.jus.br/estatistica/sead/odsele/prestacao_contas/prestacao_de_contas_eleitorais_orgaos_partidarios_2024.zip"
    pasta_dados = "prestacao_de_contas_2024"

    download_and_unzip(url, pasta_dados)
    df = carregar_dados(pasta_dados)

    if df is not None:
        G = construir_rede(df)
        metrics = calcular_metricas(G)
        partition = detectar_comunidades(G)
        gerar_visualizacao(G, metrics, partition)


if __name__ == "__main__":
    main()
