import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import calendar
from datetime import datetime

# Configuração da página - MODO ULTRA WIDE
st.set_page_config(
    page_title="Amazon Sales Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para dark mode elegante
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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        color: white;
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
</style>
""", unsafe_allow_html=True)


# Carregar dados
@st.cache_data(ttl=3600)
def load_data():
    """Carrega e prepara os dados com feature engineering."""
    BASE_DIR = Path(__file__).parent
    DATA_PATH = BASE_DIR / "data" / "processed" / "amazon_sales_clean.csv"

    df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])

    # Feature Engineering Avançado
    df['year'] = df['order_date'].dt.year
    df['month'] = df['order_date'].dt.month
    df['month_name'] = df['order_date'].dt.month_name()
    df['quarter'] = df['order_date'].dt.quarter
    df['day_of_week'] = df['order_date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    df['week'] = df['order_date'].dt.isocalendar().week

    # Métricas derivadas
    df['revenue_per_unit'] = df['total_revenue'] / df['quantity_sold']
    df['discount_impact'] = (df['price'] * df['quantity_sold']) - df['total_revenue']
    df['profit_margin'] = (df['total_revenue'] - df['discount_impact']) / df['total_revenue'] * 100

    return df


def main():
    # Header estiloso
    st.markdown('<p class="main-header">Amazon Sales Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Dashboard Executivo de Performance de Vendas</p>', unsafe_allow_html=True)

    try:
        df = load_data()
    except Exception as e:
        st.error(f"🚨 Erro ao carregar dados: {e}")
        st.stop()

    # SIDEBAR - Filtros Avançados
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=200)
        st.markdown("## 🎯 Filtros")

        # Date range com quick selects
        date_range_type = st.radio(
            "Período",
            ["Todo Período", "Último Mês", "Último Trimestre", "Último Ano", "Customizado"],
            horizontal=True
        )

        min_date = df['order_date'].min()
        max_date = df['order_date'].max()

        if date_range_type == "Último Mês":
            start_date = max_date - pd.DateOffset(months=1)
            end_date = max_date
        elif date_range_type == "Último Trimestre":
            start_date = max_date - pd.DateOffset(months=3)
            end_date = max_date
        elif date_range_type == "Último Ano":
            start_date = max_date - pd.DateOffset(years=1)
            end_date = max_date
        elif date_range_type == "Customizado":
            date_range = st.date_input(
                "Selecione o período",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

        df_filtered = df[(df['order_date'] >= pd.to_datetime(start_date)) &
                         (df['order_date'] <= pd.to_datetime(end_date))]

        # Filtros multiselect
        regions = ['Todas'] + sorted(df_filtered['customer_region'].unique().tolist())
        selected_region = st.selectbox("📍 Região", regions)

        categories = ['Todas'] + sorted(df_filtered['product_category'].unique().tolist())
        selected_category = st.selectbox("📦 Categoria", categories)

        payment_methods = ['Todos'] + sorted(df_filtered['payment_method'].unique().tolist())
        selected_payment = st.selectbox("💳 Método de Pagamento", payment_methods)

        # Aplicar filtros
        if selected_region != 'Todas':
            df_filtered = df_filtered[df_filtered['customer_region'] == selected_region]
        if selected_category != 'Todas':
            df_filtered = df_filtered[df_filtered['product_category'] == selected_category]
        if selected_payment != 'Todos':
            df_filtered = df_filtered[df_filtered['payment_method'] == selected_payment]

        # KPIs rápidos do filtro
        st.markdown("---")
        st.markdown(f"### 📊 Amostra: {len(df_filtered):,} registros")
        st.markdown(f"📅 {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")

    # MAIN CONTENT - Tabs organizadas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 **Visão Geral**",
        "💰 **Análise Financeira**",
        "📦 **Performance de Produtos**",
        "🎯 **Insights Estratégicos**"
    ])

    with tab1:
        # Métricas principais com design melhorado
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_revenue = df_filtered['total_revenue'].sum()
            st.metric(
                "💰 Receita Total",
                f"${total_revenue:,.0f}",
                delta=f"{((total_revenue / df['total_revenue'].sum()) * 100):.1f}% do total",
                delta_color="normal"
            )

        with col2:
            total_orders = df_filtered['order_id'].nunique()
            prev_period = df[(df['order_date'] >= start_date - pd.DateOffset(months=1)) &
                             (df['order_date'] < start_date)]['order_id'].nunique()
            growth = ((total_orders - prev_period) / prev_period * 100) if prev_period > 0 else 0
            st.metric(
                "📦 Total Pedidos",
                f"{total_orders:,}",
                delta=f"{growth:.1f}% vs período anterior",
                delta_color="inverse" if growth < 0 else "normal"
            )

        with col3:
            avg_ticket = total_revenue / total_orders if total_orders > 0 else 0
            st.metric(
                "🎫 Ticket Médio",
                f"${avg_ticket:,.2f}",
                delta=f"${df_filtered['revenue_per_unit'].mean():,.2f} por unidade"
            )

        with col4:
            avg_rating = df_filtered['rating'].mean()
            st.metric(
                "⭐ Rating Médio",
                f"{avg_rating:.2f}",
                delta=f"{(df_filtered['rating'] >= 4).mean() * 100:.1f}% ⭐⭐⭐⭐"
            )

        # Gráficos em grid
        col1, col2 = st.columns(2)

        with col1:
            # Receita por Região (Pizza melhorada)
            region_revenue = df_filtered.groupby('customer_region')['total_revenue'].sum().reset_index()
            fig = px.pie(
                region_revenue,
                values='total_revenue',
                names='customer_region',
                title='🌍 Distribuição de Receita por Região',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Métodos de Pagamento
            payment_revenue = df_filtered.groupby('payment_method')['total_revenue'].sum().reset_index()
            fig = px.bar(
                payment_revenue,
                x='payment_method',
                y='total_revenue',
                title='💳 Receita por Método de Pagamento',
                color='total_revenue',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(xaxis_title="", yaxis_title="Receita ($)")
            st.plotly_chart(fig, use_container_width=True)

        # Timeline interativa
        daily_revenue = df_filtered.groupby('order_date')['total_revenue'].sum().reset_index()
        fig = px.line(
            daily_revenue,
            x='order_date',
            y='total_revenue',
            title='📅 Evolução Diária da Receita',
            labels={'total_revenue': 'Receita ($)', 'order_date': 'Data'}
        )
        fig.update_traces(line_color='#FF9900', line_width=3)
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("💰 Análise Financeira Detalhada")

        col1, col2 = st.columns(2)

        with col1:
            # Mapa de calor de receita (dia da semana x mês)
            heatmap_data = df_filtered.pivot_table(
                values='total_revenue',
                index='day_of_week',
                columns='month_name',
                aggfunc='sum',
                fill_value=0
            )

            # Ordenar dias da semana e meses
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            month_order = list(calendar.month_name)[1:]
            heatmap_data = heatmap_data.reindex(day_order)[month_order]

            fig = px.imshow(
                heatmap_data,
                title='🔥 Mapa de Calor: Receita por Dia da Semana vs Mês',
                color_continuous_scale='Viridis',
                aspect="auto"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Análise de desconto x receita
            discount_analysis = df_filtered.groupby('discount_percent')['total_revenue'].agg(
                ['sum', 'count']).reset_index()
            discount_analysis['avg_revenue'] = discount_analysis['sum'] / discount_analysis['count']

            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=discount_analysis['discount_percent'], y=discount_analysis['sum'], name="Receita Total"),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(x=discount_analysis['discount_percent'], y=discount_analysis['avg_revenue'],
                           name="Ticket Médio", line=dict(color='red', width=3)),
                secondary_y=True
            )
            fig.update_layout(title="📊 Impacto do Desconto nas Vendas")
            fig.update_xaxes(title_text="Percentual de Desconto")
            fig.update_yaxes(title_text="Receita Total ($)", secondary_y=False)
            fig.update_yaxes(title_text="Ticket Médio ($)", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)

        # Top produtos por receita
        st.subheader("🏆 Top 10 Produtos por Receita")
        top_products = df_filtered.groupby('product_id').agg({
            'total_revenue': 'sum',
            'quantity_sold': 'sum',
            'rating': 'mean'
        }).sort_values('total_revenue', ascending=False).head(10).reset_index()

        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(
                top_products,
                x='product_id',
                y='total_revenue',
                color='rating',
                color_continuous_scale='RdYlGn',
                title="Top 10 Produtos por Receita"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.dataframe(
                top_products.style.format({
                    'total_revenue': '${:,.0f}',
                    'quantity_sold': '{:,.0f}',
                    'rating': '{:.1f}'
                }),
                use_container_width=True,
                height=400
            )

    with tab3:
        st.subheader("📦 Análise de Performance por Categoria")

        # Métricas por categoria
        category_metrics = df_filtered.groupby('product_category').agg({
            'total_revenue': 'sum',
            'quantity_sold': 'sum',
            'order_id': 'nunique',
            'rating': 'mean',
            'price': 'mean'
        }).reset_index()

        category_metrics['avg_ticket'] = category_metrics['total_revenue'] / category_metrics['order_id']
        category_metrics['revenue_per_unit'] = category_metrics['total_revenue'] / category_metrics['quantity_sold']

        # Bubble chart interativo
        fig = px.scatter(
            category_metrics,
            x='quantity_sold',
            y='total_revenue',
            size='avg_ticket',
            color='rating',
            hover_name='product_category',
            text='product_category',
            title='📊 Matriz de Performance por Categoria',
            labels={
                'quantity_sold': 'Quantidade Vendida',
                'total_revenue': 'Receita Total ($)',
                'rating': 'Rating Médio'
            },
            color_continuous_scale='RdYlGn'
        )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)

        # Tabela detalhada
        st.subheader("📋 Métricas Detalhadas por Categoria")
        st.dataframe(
            category_metrics.style.format({
                'total_revenue': '${:,.0f}',
                'quantity_sold': '{:,.0f}',
                'order_id': '{:,.0f}',
                'rating': '{:.2f}',
                'price': '${:.2f}',
                'avg_ticket': '${:.2f}',
                'revenue_per_unit': '${:.2f}'
            }),
            use_container_width=True,
            height=400
        )

    with tab4:
        st.subheader("🎯 Insights Estratégicos")

        # Cálculos para insights
        total_revenue_filtered = df_filtered['total_revenue'].sum()
        total_revenue_full = df['total_revenue'].sum()

        # Top categorias
        top_categories = df_filtered.groupby('product_category')['total_revenue'].sum().nlargest(3)

        # Melhor período
        monthly_revenue = df_filtered.groupby('month')['total_revenue'].sum()
        best_month = monthly_revenue.idxmax()
        best_month_name = calendar.month_name[best_month]

        # Análise de rentabilidade por desconto
        discount_efficiency = df_filtered.groupby('discount_percent').agg({
            'total_revenue': 'sum',
            'quantity_sold': 'sum'
        }).reset_index()
        discount_efficiency['revenue_per_unit'] = discount_efficiency['total_revenue'] / discount_efficiency[
            'quantity_sold']
        best_discount = discount_efficiency.loc[discount_efficiency['revenue_per_unit'].idxmax(), 'discount_percent']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🎯 Principais Descobertas")

            st.markdown(f"""
            <div class="insight-box">
                <h4>📊 Performance Geral</h4>
                <ul>
                    <li><b>Market Share:</b> Este período representa <b>{(total_revenue_filtered / total_revenue_full * 100):.1f}%</b> da receita total</li>
                    <li><b>Crescimento:</b> Ticket médio de <b>${avg_ticket:.2f}</b></li>
                    <li><b>Sazonalidade:</b> Melhor mês é <b>{best_month_name}</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="insight-box">
                <h4>🏆 Top 3 Categorias</h4>
                <ol>
                    {''.join([f'<li><b>{cat}</b>: ${val:,.0f}</li>' for cat, val in top_categories.items()])}
                </ol>
                <p>Representam <b>{(top_categories.sum() / total_revenue_filtered * 100):.1f}%</b> da receita total</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 💡 Recomendações")

            st.markdown(f"""
            <div class="insight-box">
                <h4>📈 Oportunidades</h4>
                <ul>
                    <li><b>Desconto Ótimo:</b> {best_discount}% maximiza receita por unidade</li>
                    <li><b>Rating:</b> {(df_filtered['rating'] >= 4).mean() * 100:.1f}% dos produtos têm rating ≥4 ⭐</li>
                    <li><b>Mix de produtos:</b> {df_filtered['product_category'].nunique()} categorias ativas</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # Gráfico de tendência com previsão simples
            st.markdown("### 🔮 Tendência e Projeção")
            monthly_trend = df_filtered.groupby(df_filtered['order_date'].dt.to_period('M'))[
                'total_revenue'].sum().reset_index()
            monthly_trend['order_date'] = monthly_trend['order_date'].astype(str)

            # Adicionar linha de tendência
            fig = px.scatter(
                monthly_trend,
                x='order_date',
                y='total_revenue',
                trendline="lowess",
                title="Tendência de Receita"
            )
            fig.update_traces(marker=dict(size=10, color='#FF9900'))
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()