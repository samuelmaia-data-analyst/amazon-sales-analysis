import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import calendar
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

# Configuração da página - MODO ULTRA WIDE
st.set_page_config(
    page_title="Amazon Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #FF9900, #146EB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .insight-box {
        background: rgba(255,255,255,0.1);
        border-left: 5px solid #FF9900;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 10px 10px 0px 0px;
        gap: 10px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF9900;
        color: white !important;
    }

    /* Logo container */
    .logo-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        border: 2px solid #FF9900;
    }

    /* Sidebar styling */
    .stSidebar {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #FF9900 !important;
    }

    .sidebar-footer {
        background: rgba(255, 153, 0, 0.2);
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #FF9900;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    """Carrega e prepara os dados."""
    BASE_DIR = Path(__file__).parent
    DATA_PATH = BASE_DIR / "data" / "processed" / "amazon_sales_clean.csv"

    df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])

    # Feature Engineering
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['month_name'] = df['order_date'].dt.month_name()
    df['quarter'] = df['order_date'].dt.quarter
    df['day_of_week'] = df['order_date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    df['revenue_per_unit'] = df['total_revenue'] / df['quantity_sold']

    return df


def main():
    st.markdown('<p class="main-header">Amazon Sales Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Dashboard Executivo de Performance de Vendas</p>', unsafe_allow_html=True)

    try:
        df = load_data()
    except Exception as e:
        st.error(f"🚨 Erro ao carregar dados: {e}")
        st.stop()

    # SIDEBAR
    with st.sidebar:
        st.markdown("""
        <div class="logo-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" 
                 style="width: 180px; height: auto;" 
                 alt="Amazon Logo">
        </div>
        """, unsafe_allow_html=True)

        st.markdown("## 🎯 Filtros")

        date_range_type = st.radio(
            "Período",
            ["Todo Período", "Último Mês", "Último Trimestre", "Último Ano", "Customizado"],
            horizontal=True
        )

        min_date = df['order_date'].min().date()
        max_date = df['order_date'].max().date()

        start_date = min_date
        end_date = max_date
        today = datetime.now().date()

        # CÁLCULO CORRETO DOS PERÍODOS
        if date_range_type == "Último Mês":
            # Primeiro dia do mês atual
            first_day_current_month = today.replace(day=1)
            # Último dia do mês anterior
            end_date = first_day_current_month - timedelta(days=1)
            # Primeiro dia do mês anterior
            start_date = end_date.replace(day=1)

        elif date_range_type == "Último Trimestre":
            # Encontrar o primeiro dia do trimestre atual
            current_quarter = (today.month - 1) // 3 + 1
            first_month_current_quarter = ((current_quarter - 1) * 3) + 1
            first_day_current_quarter = date(today.year, first_month_current_quarter, 1)

            # Último dia do trimestre anterior
            end_date = first_day_current_quarter - timedelta(days=1)
            # Primeiro dia do trimestre anterior
            start_date = date(
                end_date.year if end_date.month > 3 else end_date.year - 1,
                ((end_date.month - 1) // 3) * 3 + 1,
                1
            )

        elif date_range_type == "Último Ano":
            # Ano anterior completo
            start_date = date(today.year - 1, 1, 1)
            end_date = date(today.year - 1, 12, 31)

        elif date_range_type == "Customizado":
            date_range = st.date_input(
                "Selecione o período",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(date_range) == 2:
                start_date, end_date = date_range

        # Garantir que as datas estão dentro do range disponível
        start_date = max(start_date, min_date)
        end_date = min(end_date, max_date)

        # Converter para datetime
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.DateOffset(days=1) - pd.DateOffset(seconds=1)

        # Filtrar dados
        df_filtered = df[(df['order_date'] >= start_datetime) & (df['order_date'] <= end_datetime)]

        # Filtros adicionais
        if not df_filtered.empty:
            regions = ['Todas'] + sorted(df_filtered['customer_region'].unique().tolist())
            categories = ['Todas'] + sorted(df_filtered['product_category'].unique().tolist())
            payment_methods = ['Todos'] + sorted(df_filtered['payment_method'].unique().tolist())
        else:
            regions = categories = payment_methods = ['Todas']

        selected_region = st.selectbox("📍 Região", regions)
        selected_category = st.selectbox("📦 Categoria", categories)
        selected_payment = st.selectbox("💳 Método de Pagamento", payment_methods)

        # Aplicar filtros adicionais
        if not df_filtered.empty:
            if selected_region != 'Todas':
                df_filtered = df_filtered[df_filtered['customer_region'] == selected_region]
            if selected_category != 'Todas':
                df_filtered = df_filtered[df_filtered['product_category'] == selected_category]
            if selected_payment != 'Todos':
                df_filtered = df_filtered[df_filtered['payment_method'] == selected_payment]

        # Resumo do filtro
        st.markdown("---")
        st.markdown("""
        <div class="sidebar-footer">
            <h4 style='color: #FF9900; margin-top: 0;'>📊 Resumo do Filtro</h4>
        """, unsafe_allow_html=True)
        st.markdown(f"**Registros:** {len(df_filtered):,}")
        st.markdown(f"**Período:** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        st.markdown("</div>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 **Visão Geral**",
        "💰 **Análise Financeira**",
        "📦 **Performance de Produtos**",
        "🎯 **Insights Estratégicos**"
    ])

    if df_filtered.empty:
        for tab in [tab1, tab2, tab3, tab4]:
            with tab:
                st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    else:
        with tab1:
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_revenue = df_filtered['total_revenue'].sum()
                st.metric(
                    "💰 Receita Total",
                    f"${total_revenue:,.0f}",
                    delta=f"{((total_revenue / df['total_revenue'].sum()) * 100):.1f}% do total"
                )

            with col2:
                total_orders = df_filtered['order_id'].nunique()
                st.metric("📦 Total Pedidos", f"{total_orders:,}")

            with col3:
                avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
                st.metric("🎫 Ticket Médio", f"${avg_ticket:,.2f}")

            with col4:
                avg_rating = df_filtered['rating'].mean()
                st.metric("⭐ Rating Médio", f"{avg_rating:.2f}")

            # Gráficos
            col1, col2 = st.columns(2)

            with col1:
                region_revenue = df_filtered.groupby('customer_region')['total_revenue'].sum().reset_index()
                if not region_revenue.empty:
                    fig = px.pie(
                        region_revenue,
                        values='total_revenue',
                        names='customer_region',
                        title='🌍 Distribuição de Receita por Região',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Viridis
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                payment_revenue = df_filtered.groupby('payment_method')['total_revenue'].sum().reset_index()
                if not payment_revenue.empty:
                    fig = px.bar(
                        payment_revenue,
                        x='payment_method',
                        y='total_revenue',
                        title='💳 Receita por Método de Pagamento',
                        color='total_revenue',
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Timeline
            daily_revenue = df_filtered.groupby('order_date')['total_revenue'].sum().reset_index()
            if not daily_revenue.empty:
                fig = px.line(
                    daily_revenue,
                    x='order_date',
                    y='total_revenue',
                    title='📅 Evolução Diária da Receita'
                )
                fig.update_traces(line_color='#FF9900', line_width=3)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("💰 Análise Financeira Detalhada")

            col1, col2 = st.columns(2)

            with col1:
                # Mapa de calor
                try:
                    heatmap_data = df_filtered.pivot_table(
                        values='total_revenue',
                        index='day_of_week',
                        columns='month_name',
                        aggfunc='sum',
                        fill_value=0
                    )

                    if not heatmap_data.empty:
                        fig = px.imshow(
                            heatmap_data,
                            title='🔥 Receita por Dia da Semana vs Mês',
                            color_continuous_scale='Viridis',
                            aspect="auto"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    st.info("Não foi possível gerar o mapa de calor")

            with col2:
                # Top produtos
                top_products = df_filtered.groupby('product_id').agg({
                    'total_revenue': 'sum',
                    'quantity_sold': 'sum',
                    'rating': 'mean'
                }).sort_values('total_revenue', ascending=False).head(10)

                if not top_products.empty:
                    st.dataframe(
                        top_products.style.format({
                            'total_revenue': '${:,.0f}',
                            'quantity_sold': '{:,.0f}',
                            'rating': '{:.1f}'
                        }),
                        use_container_width=True
                    )

        with tab3:
            st.subheader("📦 Performance por Categoria")

            category_metrics = df_filtered.groupby('product_category').agg({
                'total_revenue': 'sum',
                'quantity_sold': 'sum',
                'order_id': 'nunique',
                'rating': 'mean'
            }).reset_index()

            if not category_metrics.empty:
                st.dataframe(
                    category_metrics.style.format({
                        'total_revenue': '${:,.0f}',
                        'quantity_sold': '{:,.0f}',
                        'order_id': '{:,.0f}',
                        'rating': '{:.2f}'
                    }),
                    use_container_width=True
                )

        with tab4:
            st.subheader("🎯 Insights Estratégicos")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📊 Performance Geral")
                st.markdown(f"""
                - **Receita total:** ${total_revenue:,.0f}
                - **Total pedidos:** {total_orders:,}
                - **Ticket médio:** ${avg_ticket:.2f}
                - **Rating médio:** {avg_rating:.2f}
                """)

            with col2:
                st.markdown("### 📈 Top Categorias")
                top_cats = df_filtered.groupby('product_category')['total_revenue'].sum().nlargest(3)
                for cat, val in top_cats.items():
                    st.markdown(f"- **{cat}:** ${val:,.0f}")


if __name__ == "__main__":
    main()