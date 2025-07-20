import streamlit as st
import pandas as pd
import os
import subprocess
import time
import networkx as nx
import streamlit.components.v1 as components
from main import carregar_dados, construir_rede, calcular_metricas, detectar_comunidades, gerar_visualizacao

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

# Constrói rede e calcula métricas
if df.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
else:
    G = construir_rede(df)
    metrics = calcular_metricas(G)
    partition = detectar_comunidades(G)

    # Salva visualização
    gerar_visualizacao(G, metrics, partition, output_html="docs/rede.html")

    # 📊 Métricas da rede
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

    # Mostra rede
    components.iframe("docs/rede.html", height=750, scrolling=True)
