import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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

        # Date range com quick selects - VERSÃO CORRIGIDA
        date_range_type = st.radio(
            "Período",
            ["Todo Período", "Último Mês", "Último Trimestre", "Último Ano", "Customizado"],
            horizontal=True
        )

        min_date = df['order_date'].min().date()
        max_date = df['order_date'].max().date()

        # Inicializar start_date e end_date com valores padrão
        start_date = min_date
        end_date = max_date

        # Data atual para referência
        today = datetime.now().date()

        # CORREÇÃO: Lógica simplificada para cada tipo de período
        if date_range_type == "Último Mês":
            # Último mês com dados disponíveis
            last_date = max_date
            start_date = last_date.replace(day=1)
            end_date = last_date

        elif date_range_type == "Último Trimestre":
            # Último trimestre completo baseado na última data
            last_date = max_date

            # Encontrar o primeiro dia do trimestre da última data
            quarter_start_month = ((last_date.month - 1) // 3) * 3 + 1
            quarter_start = datetime(last_date.year, quarter_start_month, 1).date()

            # Se a última data não é o último dia do trimestre, pegar o trimestre anterior
            quarter_end = (quarter_start + relativedelta(months=3) - timedelta(days=1))

            if last_date < quarter_end:
                # Pegar trimestre anterior
                quarter_start = quarter_start - relativedelta(months=3)
                quarter_end = quarter_start + relativedelta(months=3) - timedelta(days=1)

            start_date = quarter_start
            end_date = quarter_end

        elif date_range_type == "Último Ano":
            # Último ano completo baseado na última data
            last_date = max_date
            start_date = datetime(last_date.year - 1, 1, 1).date()
            end_date = datetime(last_date.year - 1, 12, 31).date()

        elif date_range_type == "Customizado":
            date_range = st.date_input(
                "Selecione o período",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
        # else "Todo Período" - já temos start_date e end_date com min_date e max_date

        # Garantir que as datas estão dentro do range disponível
        start_date = max(start_date, min_date)
        end_date = min(end_date, max_date)

        # Garantir que start_date é menor ou igual a end_date
        if start_date > end_date:
            start_date, end_date = min_date, max_date

        # Converter para datetime para filtrar
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date) + pd.DateOffset(days=1) - pd.DateOffset(seconds=1)

        df_filtered = df[(df['order_date'] >= start_datetime) &
                         (df['order_date'] <= end_datetime)]

        # Filtros multiselect
        regions = ['Todas'] + sorted(df['customer_region'].unique().tolist())
        selected_region = st.selectbox("📍 Região", regions)

        categories = ['Todas'] + sorted(df['product_category'].unique().tolist())
        selected_category = st.selectbox("📦 Categoria", categories)

        payment_methods = ['Todos'] + sorted(df['payment_method'].unique().tolist())
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
            # Calcular período anterior apenas se houver dados suficientes
            if len(df_filtered) > 0 and date_range_type != "Todo Período":
                period_days = (end_datetime - start_datetime).days
                prev_start = start_datetime - relativedelta(days=period_days)
                prev_end = start_datetime - timedelta(seconds=1)

                prev_period = df[(df['order_date'] >= prev_start) &
                                 (df['order_date'] <= prev_end)]['order_id'].nunique()
                growth = ((total_orders - prev_period) / prev_period * 100) if prev_period > 0 else 0
            else:
                growth = 0

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
                delta=f"${df_filtered['revenue_per_unit'].mean():,.2f} por unidade" if len(df_filtered) > 0 else "$0.00"
            )

        with col4:
            avg_rating = df_filtered['rating'].mean() if len(df_filtered) > 0 else 0
            high_rating_pct = (df_filtered['rating'] >= 4).mean() * 100 if len(df_filtered) > 0 else 0
            st.metric(
                "⭐ Rating Médio",
                f"{avg_rating:.2f}",
                delta=f"{high_rating_pct:.1f}% ⭐⭐⭐⭐"
            )

        # Verificar se há dados para exibir gráficos
        if len(df_filtered) > 0:
            # Gráficos em grid
            col1, col2 = st.columns(2)

            with col1:
                # Receita por Região (Pizza melhorada)
                region_revenue = df_filtered.groupby('customer_region')['total_revenue'].sum().reset_index()
                if len(region_revenue) > 0:
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
                else:
                    st.info("Sem dados de região para o período selecionado")

            with col2:
                # Métodos de Pagamento
                payment_revenue = df_filtered.groupby('payment_method')['total_revenue'].sum().reset_index()
                if len(payment_revenue) > 0:
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
                else:
                    st.info("Sem dados de pagamento para o período selecionado")

            # Timeline interativa
            daily_revenue = df_filtered.groupby('order_date')['total_revenue'].sum().reset_index()
            if len(daily_revenue) > 0:
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
            else:
                st.info("Sem dados diários para o período selecionado")
        else:
            st.warning("⚠️ Nenhum dado encontrado para o período e filtros selecionados")

    with tab2:
        st.subheader("💰 Análise Financeira Detalhada")

        if len(df_filtered) > 0:
            col1, col2 = st.columns(2)

            with col1:
                # Mapa de calor de receita (dia da semana x mês)
                try:
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

                    # Verificar se há dados antes de reindexar
                    if not heatmap_data.empty:
                        # Reindexar apenas com as colunas que existem
                        available_months = [m for m in month_order if m in heatmap_data.columns]
                        available_days = [d for d in day_order if d in heatmap_data.index]

                        if available_months and available_days:
                            heatmap_data = heatmap_data.reindex(available_days)[available_months]

                            fig = px.imshow(
                                heatmap_data,
                                title='🔥 Mapa de Calor: Receita por Dia da Semana vs Mês',
                                color_continuous_scale='Viridis',
                                aspect="auto"
                            )
                            fig.update_layout(height=500)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Dados insuficientes para o mapa de calor")
                    else:
                        st.info("Sem dados suficientes para o mapa de calor")
                except Exception as e:
                    st.info("Não foi possível gerar o mapa de calor para o período selecionado")

            with col2:
                # Análise de desconto x receita
                if 'discount_percent' in df_filtered.columns:
                    discount_analysis = df_filtered.groupby('discount_percent')['total_revenue'].agg(
                        ['sum', 'count']).reset_index()
                    discount_analysis['avg_revenue'] = discount_analysis['sum'] / discount_analysis['count']

                    if len(discount_analysis) > 0:
                        fig = make_subplots(specs=[[{"secondary_y": True}]])
                        fig.add_trace(
                            go.Bar(x=discount_analysis['discount_percent'], y=discount_analysis['sum'],
                                   name="Receita Total"),
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
                    else:
                        st.info("Sem dados de desconto para análise")

            # Top produtos por receita
            st.subheader("🏆 Top 10 Produtos por Receita")
            if 'product_id' in df_filtered.columns:
                top_products = df_filtered.groupby('product_id').agg({
                    'total_revenue': 'sum',
                    'quantity_sold': 'sum',
                    'rating': 'mean'
                }).sort_values('total_revenue', ascending=False).head(10).reset_index()

                if len(top_products) > 0:
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
                else:
                    st.info("Sem dados de produtos para o período selecionado")
            else:
                st.info("Coluna 'product_id' não encontrada nos dados")
        else:
            st.warning("⚠️ Nenhum dado encontrado para o período e filtros selecionados")

    with tab3:
        st.subheader("📦 Análise de Performance por Categoria")

        if len(df_filtered) > 0:
            # Métricas por categoria
            category_metrics = df_filtered.groupby('product_category').agg({
                'total_revenue': 'sum',
                'quantity_sold': 'sum',
                'order_id': 'nunique',
                'rating': 'mean',
                'price': 'mean'
            }).reset_index()

            if len(category_metrics) > 0:
                category_metrics['avg_ticket'] = category_metrics['total_revenue'] / category_metrics['order_id']
                category_metrics['revenue_per_unit'] = category_metrics['total_revenue'] / category_metrics[
                    'quantity_sold']

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
            else:
                st.info("Sem dados de categoria para o período selecionado")
        else:
            st.warning("⚠️ Nenhum dado encontrado para o período e filtros selecionados")

    with tab4:
        st.subheader("🎯 Insights Estratégicos")

        if len(df_filtered) > 0:
            # Cálculos para insights
            total_revenue_filtered = df_filtered['total_revenue'].sum()
            total_revenue_full = df['total_revenue'].sum()

            # Top categorias
            top_categories = df_filtered.groupby('product_category')['total_revenue'].sum().nlargest(3)

            # Melhor período
            monthly_revenue = df_filtered.groupby('month')['total_revenue'].sum()
            if not monthly_revenue.empty:
                best_month = monthly_revenue.idxmax()
                best_month_name = calendar.month_name[best_month]
            else:
                best_month_name = "N/A"

            # Análise de rentabilidade por desconto
            if 'discount_percent' in df_filtered.columns:
                discount_efficiency = df_filtered.groupby('discount_percent').agg({
                    'total_revenue': 'sum',
                    'quantity_sold': 'sum'
                }).reset_index()
                discount_efficiency['revenue_per_unit'] = discount_efficiency['total_revenue'] / discount_efficiency[
                    'quantity_sold']
                if not discount_efficiency.empty:
                    best_discount = discount_efficiency.loc[
                        discount_efficiency['revenue_per_unit'].idxmax(), 'discount_percent']
                else:
                    best_discount = 0
            else:
                best_discount = 0

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

                if not top_categories.empty:
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

                # Gráfico de tendência
                st.markdown("### 🔮 Tendência Mensal")

                # Agrupar por mês de forma segura
                monthly_trend = df_filtered.groupby(
                    pd.Grouper(key='order_date', freq='ME')
                )['total_revenue'].sum().reset_index()

                if len(monthly_trend) > 0:
                    # Garantir que a data está no formato correto
                    monthly_trend['order_date'] = pd.to_datetime(monthly_trend['order_date'])

                    # Criar gráfico de linhas
                    fig = px.line(
                        monthly_trend,
                        x='order_date',
                        y='total_revenue',
                        title="📈 Tendência de Receita Mensal",
                        markers=True
                    )

                    # Personalizar
                    fig.update_traces(
                        line=dict(color='#FF9900', width=3),
                        marker=dict(size=8, color='#FF9900')
                    )
                    fig.update_layout(
                        xaxis_title="Mês",
                        yaxis_title="Receita Total ($)",
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados suficientes para mostrar tendência mensal")
        else:
            st.warning("⚠️ Nenhum dado encontrado para o período e filtros selecionados")


if __name__ == "__main__":
    main()