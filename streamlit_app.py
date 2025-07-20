import streamlit as st
import pandas as pd
import os
import subprocess
import networkx as nx
import streamlit.components.v1 as components

from main import carregar_dados, construir_rede, calcular_metricas, detectar_comunidades

# Função geradora de visualização inline (modificada do main.py)
from pyvis.network import Network

def gerar_visualizacao_inline(G, metrics, partition):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False, directed=True)

    comunidades = set(partition.values())
    palette = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
               '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe']
    color_map = {com: palette[i % len(palette)] for i, com in enumerate(comunidades)}

    for node in G.nodes():
        com = partition.get(node, -1)
        color = color_map.get(com, '#ffffff')
        title = (
            f"<b>Nome:</b> {node}<br>"
            f"<b>Comunidade:</b> {com}<br>"
            f"<b>Degree Centrality:</b> {metrics['degree'].get(node, 0):.4f}<br>"
            f"<b>Closeness Centrality:</b> {metrics['closeness'].get(node, 0):.4f}<br>"
            f"<b>Eigenvector Centrality:</b> {metrics['eigenvector'].get(node, 0):.4f}<br>"
            f"<b>Betweenness Centrality:</b> {metrics['betweenness'].get(node, 0):.4f}"
        )
        net.add_node(node, label=node, title=title, color=color)

    for u, v, data in G.edges(data=True):
        valor = data.get("weight", 1)
        width = max(1, valor / 1000)
        title = f"Valor da doação: R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        net.add_edge(u, v, value=valor, width=width, title=title)

    html_str = net.generate_html()
    return html_str

# Configuração da página
st.set_page_config(page_title="Análise de Rede Política", layout="wide")

st.title("🔗 Análise de Rede Política - TSE 2024")
st.markdown("""
Este app constrói uma rede de doações originárias com dados do TSE.

- **Nós**: Doadores e Partidos
- **Arestas**: Direcionadas, ponderadas pelo valor doado
- **Visualização**: Interativa com Pyvis
""")

st.markdown("---")

# Parâmetros e filtros
pasta_dados = "prestacao_de_contas_2024"

st.sidebar.header("🎛️ Filtros")
valor_min = st.sidebar.slider("Valor mínimo da doação (R$)", 0, 10000, 0, step=100)

# Baixar e carregar dados se necessário
if not os.path.exists(pasta_dados):
    with st.spinner("Baixando dados do TSE..."):
        subprocess.call(["python", "main.py"])  # faz download e unzip

# Carrega os dados e aplica filtros
df = carregar_dados(pasta_dados)
partidos_disponiveis = sorted(df['SG_PARTIDO'].dropna().unique().tolist())
partido_selecionado = st.sidebar.selectbox("Filtrar por partido", ["Todos"] + partidos_disponiveis)

if partido_selecionado != "Todos":
    df = df[df['SG_PARTIDO'] == partido_selecionado]

df = df[df['VR_RECEITA'] >= valor_min]

if df.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    G = construir_rede(df)
    metrics = calcular_metricas(G)
    partition = detectar_comunidades(G)

    st.subheader("📈 Métricas da Rede")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔹 Total de Nós", len(G.nodes()))
        st.metric("🔸 Doadores", len([n for n, d in G.nodes(data=True) if d['type'] == 'doador']))
    with col2:
        st.metric("🔹 Total de Arestas", len(G.edges()))
        st.metric("🔸 Partidos", len([n for n, d in G.nodes(data=True) if d['type'] == 'partido']))
    with col3:
        st.metric("🔸 Densidade", f"{nx.density(G):.4f}")
        st.metric("🔸 Componentes", nx.number_weakly_connected_components(G))

    st.markdown("---")
    st.subheader("🌐 Visualização Interativa")

    html_string = gerar_visualizacao_inline(G, metrics, partition)
    components.html(html_string, height=750, scrolling=True)
