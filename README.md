# 🔗 Análise de Rede Política

Este projeto realiza uma **análise de redes direcionadas** usando dados públicos do [Tribunal Superior Eleitoral (TSE)](https://dadosabertos.tse.jus.br/dataset/prestacao-de-contas-eleitorais-2024), com foco nas **doações originárias a partidos políticos** no ano de 2024.  
A visualização interativa foi desenvolvida com **Pyvis** e está disponível tanto via **GitHub Pages** quanto em uma aplicação web interativa no **Streamlit Cloud**.

> 📍 Visualização estática (Pyvis): [https://ian-mendes.github.io/rede-politica-vis/rede.html](https://ian-mendes.github.io/rede-politica-vis/rede.html)  
> 🌐 Aplicação interativa (Streamlit Cloud): [https://rede-doacao-politica-2024-rn.streamlit.app/](https://rede-doacao-politica-2024-rn.streamlit.app/)

---

## 📚 Sobre os Dados

- **Fonte:** [TSE — Prestação de Contas Eleitorais 2024](https://dadosabertos.tse.jus.br/)
- **Arquivos utilizados:**
  - `receitas_orgaos_partidarios_doador_originario.csv`
  - `receitas_orgaos_partidarios.csv`

Esses arquivos são baixados automaticamente e unidos com base no identificador da receita (`SQ_RECEITA`).

---

## 🎯 Objetivo

Investigar as relações financeiras entre **doadores originários** e **partidos políticos**, representando-as por meio de uma **rede direcionada e ponderada**.

**Estrutura da Rede:**

- 🔹 **Nós:**
  - `NM_DOADOR_ORIGINARIO` → Doador
  - `SG_PARTIDO` → Partido Receptor
- 🔹 **Arestas:**
  - Direcionadas do doador para o partido
  - Ponderadas por `VR_RECEITA` (valor da doação)

---

## 📈 Métricas (Exemplo de uma execução)

### 🧮 Grafo completo

- **Total de Nós:** 56  
- **Total de Arestas:** 32  
- **Doadores:** 31  
- **Partidos:** 25  
- **Componentes Conectados:** 24  
- **Densidade:** 0.0104  
- **Assortatividade:** -0.4224  

### 🔍 Componente Principal

- **Nós:** 10  
- **Arestas:** 9  
- **Diâmetro:** 2  
- **Clustering global:** 0.0000  

### 💠 Centralidades — Top 5

| Métrica                  | 1º            | 2º            | 3º           | 4º           | 5º              |
|--------------------------|---------------|---------------|--------------|--------------|-----------------|
| **Degree**               | UNIÃO         | PSDB          | PODE         | PSD          | REPUBLICANOS    |
| **Closeness**            | UNIÃO         | PSDB          | PODE         | PSD          | REPUBLICANOS    |
| **Betweenness**          | UNIÃO         | REPUBLICANOS  | SOLIDARIEDADE| MDB          | PC do B         |
| **Eigenvector**          | UNIÃO         | PSDB          | PODE         | PSD          | REPUBLICANOS    |

---

## 🧩 Comunidades Detectadas (Louvain)

| Partido          | Nº Doadores | Valor Total        |
|------------------|-------------|--------------------|
| **UNIÃO**        | 9           | R$ 1.826,64        |
| **REPUBLICANOS** | 2           | R$ 7.063,75        |
| **PSDB**         | 7           | R$ 150,51          |
| **PODE**         | 7           | R$ 31.685,00       |
| *(demais)*       | -           | -                  |

---

## 🌐 Visualização Interativa

- A visualização estática em HTML é gerada automaticamente no diretório `docs/` com a biblioteca [Pyvis](https://pyvis.readthedocs.io/).  
- Para uma experiência interativa mais rica, incluindo filtros e métricas em tempo real, acesse a aplicação no **Streamlit Cloud**:  
  [https://rede-doacao-politica-2024-rn.streamlit.app/](https://rede-doacao-politica-2024-rn.streamlit.app/)

---

## 🚀 Como Executar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/Ian-Mendes/rede-politica-vis.git
   cd rede-politica-vis
