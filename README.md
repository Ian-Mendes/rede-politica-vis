# Rede Política - Análise de Doações

[![GitHub Pages](https://img.shields.io/badge/Visualização-Online-green)](https://Ian-Mendes.github.io/rede-politica-vis)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-blue)](https://seu-app.streamlit.app)

## 📊 Visualização Interativa
Acesse o grafo de doações partidárias:
👉 [https://Ian-Mendes.github.io/rede-politica-vis](https://Ian-Mendes.github.io/rede-politica-vis)

## 🛠 Como Executar Localmente
```bash
git clone https://github.com/Ian-Mendes/rede-politica-vis.git
cd rede-politica-vis
pip install -r requirements.txt
python main.py
```

## 🗂 Estrutura do Projeto
```
/rede-politica-vis
├── docs/            # GitHub Pages (visualização)
├── data/            # Dados processados
├── src/             # Código-fonte
├── .nojekyll        # Configuração GitHub Pages
└── requirements.txt # Dependências
```

## 📌 Métricas Geradas
- Detecção de comunidades (Louvain)
- Centralidade de grau, intermediação e proximidade
- Visualização interativa com PyVis