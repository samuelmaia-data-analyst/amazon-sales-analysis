# 🛒 Amazon Sales Analysis
### Dashboard Estratégico de Performance de Vendas

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://amazon-sales-analysis-samuelmaia-data-analyst.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-brightgreen)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Plotly](https://img.shields.io/badge/Plotly-5.14+-orange)
![Licença](https://img.shields.io/badge/Licença-MIT-green)

## 📊 Visão Geral do Projeto

Este projeto consiste em um **dashboard interativo e executivo** para análise aprofundada de vendas, desenvolvido com o objetivo de transformar dados brutos em **insights estratégicos de negócio**. A aplicação vai além da simples visualização, atuando como uma ferramenta de suporte à decisão ao responder não apenas **"o que aconteceu"**, mas também **"o que isso significa"** e **"para onde estamos indo"**.

O projeto foi construído com foco em **reprodutibilidade, boas práticas de engenharia de dados e design de informação**, resultando em uma solução profissional e pronta para produção.

**🔗 Acesse o dashboard online:** [amazon-sales-analysis-samuelmaia-data-analyst.streamlit.app](https://amazon-sales-analysis-samuelmaia-data-analyst.streamlit.app)

## 🎯 Principais Funcionalidades e Insights

O dashboard é organizado em 4 visões estratégicas que permitem uma análise completa do negócio:

| Aba | Funcionalidades | Valor para o Negócio |
| :--- | :--- | :--- |
| **📈 Visão Geral** | KPIs de alto nível (Receita Total, Pedidos, Ticket Médio, Rating), distribuição geográfica e por método de pagamento, evolução diária das vendas. | Panorama instantâneo da saúde do negócio e identificação de canais de venda mais fortes. |
| **💰 Análise Financeira** | Mapa de calor de receita (dia da semana x mês), impacto do desconto no faturamento e no ticket médio, ranking dos top 10 produtos. | Identificação de padrões de sazonalidade e otimização da estratégia de descontos para maximizar receita. |
| **📦 Performance de Produtos** | Matriz de performance por categoria (bubble chart), relacionando quantidade vendida, receita, rating e ticket médio. Tabela detalhada com métricas consolidadas. | Classificação de categorias para decisões de portfólio (investir, manter ou descontinuar). |
| **🎯 Insights Estratégicos** | Compilação de descobertas com análise de market share do período, melhor mês de vendas, desconto ótimo e gráfico de tendência mensal. | Recomendações acionáveis baseadas em dados para orientar a estratégia comercial. |

## 🛠️ Arquitetura do Projeto e Stack Tecnológica

O projeto foi estruturado com uma arquitetura modular e profissional, seguindo as melhores práticas do mercado.

### Estrutura de Diretórios
```
amazon-sales-analysis/
├─ data/
│  ├─ raw/                 # Dados brutos (ignorados pelo git)
│  └─ processed/           # Dados limpos e tratados (amazon_sales_clean.csv)
├─ notebooks/              # Jupyter notebooks para análises exploratórias
├─ src/                    # Código fonte modular (pipelines)
│  ├─ __init__.py
│  ├─ config.py            # Configurações de caminhos e constantes
│  ├─ data_ingestion.py    # Download do dataset via KaggleHub
│  ├─ data_preprocessing.py# Limpeza, tipagem e feature engineering
│  ├─ eda.py               # Análise exploratória inicial
│  └─ visualization.py     # Funções de geração de gráficos
├─ tests/                  # Testes unitários (pytest)
│  └─ test_data_quality.py
├─ .gitignore
├─ requirements.txt        # Dependências do projeto
├─ README.md               # Esta documentação
└─ streamlit_app.py        # Aplicação principal do dashboard
```

### Stack Tecnológica

| Categoria | Tecnologias |
| :--- | :--- |
| **Linguagem** | ![Python](https://img.shields.io/badge/Python-3.13-blue) |
| **Manipulação de Dados** | ![Pandas](https://img.shields.io/badge/Pandas-2.0+-brightgreen) ![NumPy](https://img.shields.io/badge/NumPy-1.24+-blue) |
| **Visualização** | ![Plotly](https://img.shields.io/badge/Plotly-5.14+-orange) ![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7+-red) ![Seaborn](https://img.shields.io/badge/Seaborn-0.12+-cyan) |
| **Dashboard** | ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red) |
| **Fonte de Dados** | ![Kaggle](https://img.shields.io/badge/Kaggle-Dataset-blue) `aliiihussain/amazon-sales-dataset` |
| **Versionamento e Deploy** | ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white) ![Streamlit Cloud](https://img.shields.io/badge/Streamlit%20Cloud-FF4B4B?logo=streamlit&logoColor=white) |
| **Testes** | ![Pytest](https://img.shields.io/badge/Pytest-7.0+-yellow) |

## 🚀 Como Executar o Projeto Localmente

Siga estes passos para reproduzir o ambiente e executar o projeto em sua máquina.

### Pré-requisitos
- Python 3.13 ou superior instalado.
- Git instalado.

### Passo a Passo

1.  **Clone o repositório**
    ```bash
    git clone https://github.com/samuelmaia-data-analyst/amazon-sales-analysis.git
    cd amazon-sales-analysis
    ```

2.  **Crie e ative um ambiente virtual**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit**
    ```bash
    streamlit run streamlit_app.py
    ```
    O dashboard será aberto automaticamente em seu navegador padrão (geralmente em `http://localhost:8501`).

### (Opcional) Pipeline Completo de Dados
Para reproduzir todo o pipeline de ingestão e processamento (que gera o arquivo `data/processed/amazon_sales_clean.csv` a partir da fonte no Kaggle), execute:
```bash
python main.py
```

## 📈 Demonstração e Resultados

A aplicação entrega uma experiência de análise fluida e profissional. Abaixo, alguns exemplos de visões disponíveis:

### Visão Executiva
A aba "Visão Geral" oferece um resumo instantâneo com os KPIs mais importantes e a evolução das vendas no período selecionado, permitindo uma leitura rápida da saúde do negócio.

### Análise de Sazonalidade
O mapa de calor na aba "Análise Financeira" revela padrões como os dias da semana e meses com maior concentração de receita, um insight valioso para planejamento de campanhas e estoque.

### Recomendações Baseadas em Dados
A aba "Insights Estratégicos" sintetiza as principais descobertas, como o percentual de desconto que maximiza a receita por unidade, fornecendo uma recomendação clara e acionável para a área comercial.

## 🧪 Testes e Qualidade de Código

Para garantir a confiabilidade do pipeline de dados, o projeto inclui testes automatizados. Execute a suíte de testes com:

```bash
pytest tests/ -v
```

Os testes atuais verificam:
- A existência do arquivo de dados processados.
- A ausência de colunas completamente nulas no dataset final.

## 💡 Sobre o Desenvolvedor

Este projeto foi desenvolvido por **Samuel Maia**, Analista de Dados com mais de 10 anos de experiência em gestão e uma sólida trajetória em tecnologia. O objetivo foi construir uma solução de ponta a ponta que demonstrasse não apenas habilidades técnicas (Python, Streamlit, análise de dados), mas principalmente uma **mentalidade estratégica e de negócio**.

**Diferenciais aplicados neste projeto:**
*   **Pensamento Analítico:** A estrutura do dashboard foi desenhada para guiar o usuário do macro (Visão Geral) ao micro (Insights), facilitando a descoberta de valor.
*   **Comunicação com Dados:** A escolha de gráficos, cores e a disposição das informações seguem princípios de storytelling com dados, tornando a análise acessível a públicos não-técnicos.
*   **Resolução de Problemas:** A métrica de "desconto ótimo" e a análise de sazonalidade são exemplos de como o projeto busca responder a perguntas de negócio concretas.
*   **Profissionalismo e Boas Práticas:** O código é modular, documentado e segue as melhores práticas de engenharia de software, incluindo uso de ambientes virtuais, controle de versão e testes.

### 🎯 Competências em Destaque

| Competência | Nível | Aplicação no Projeto |
| :--- | :--- | :--- |
| Análise de Dados | ⭐⭐⭐⭐⭐ | Transformação de dados brutos em insights estratégicos |
| Python | ⭐⭐⭐⭐ | Desenvolvimento de pipeline ETL e dashboard interativo |
| Visualização de Dados | ⭐⭐⭐⭐⭐ | Criação de gráficos intuitivos e acionáveis com Plotly |
| Storytelling com Dados | ⭐⭐⭐⭐ | Estruturação do dashboard para guiar a descoberta de insights |
| Resolução de Problemas | ⭐⭐⭐⭐⭐ | Implementação de métricas como "desconto ótimo" para responder perguntas de negócio |

## 📫 Vamos Conectar?

⭐ **"Dados não são apenas números; são histórias esperando para serem contadas e problemas esperando para serem resolvidos."**

| Canal | Link |
| :--- | :--- |
| **GitHub** | [github.com/samuelmaia-data-analyst](https://github.com/samuelmaia-data-analyst) |
| **LinkedIn** | [linkedin.com/in/samuelmaia-data-analyst](https://linkedin.com/in/samuelmaia-data-analyst) |
| **Email** | smaia2@gmail.com |

Para conhecer mais sobre minha trajetória e outros projetos, visite meu perfil no GitHub ou entre em contato pelo LinkedIn.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela no GitHub!** Isso ajuda a divulgar o trabalho e é muito importante para mim.
```