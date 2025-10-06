"""
Movies Big Data Pipeline - Web Interface com IA.

Interface interativa usando Streamlit com integração ao Google Gemini
para análise de dados em linguagem natural.
"""

import os
from pathlib import Path
from typing import Optional

import google.generativeai as genai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar página
st.set_page_config(
    page_title="Movies Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado para melhorar a interface
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 24px;
        background-color: #1f1f1f;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
    }
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #404040;
        padding: 15px;
        border-radius: 8px;
    }
    .plot-container {
        background-color: #262730;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Configurar Gemini
def configure_gemini() -> Optional[genai.GenerativeModel]:
    """Configurar Google Gemini API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        st.error(f"Erro ao configurar Gemini: {e}")
        return None


@st.cache_data
def load_data() -> dict:
    """Carregar dados da camada Gold."""
    gold_dir = Path("data/refined")

    if not gold_dir.exists():
        return {}

    data = {}

    files = {
        "movies": "movies_enriched.parquet",
        "yearly": "yearly_analytics.parquet",
        "genres": "genre_analytics.parquet",
        "top_movies": "top_movies.parquet",
        "directors": "director_analytics.parquet",
    }

    for key, filename in files.items():
        filepath = gold_dir / filename
        if filepath.exists():
            data[key] = pd.read_parquet(filepath)

    return data


def generate_chart_with_ai(prompt: str, data: dict, model: genai.GenerativeModel) -> None:
    """Gerar gráfico usando IA."""
    try:
        # Criar contexto dos dados disponíveis
        context = f"""
Você tem acesso aos seguintes dados de filmes:

1. movies: {len(data.get('movies', []))} filmes com colunas: title, release_year, budget, revenue, profit, roi, vote_average, genre_names, director

2. yearly: Análises por ano com colunas: release_year, movie_count, avg_budget, avg_revenue, avg_profit

3. genres: Análises por gênero com colunas: genre_names, movie_count, avg_budget, avg_revenue, avg_rating

4. top_movies: Top filmes com colunas: title, release_year, revenue, profit, roi, vote_average, rank_type

5. directors: Análises de diretores com colunas: director, movie_count, total_revenue, avg_rating

O usuário pediu: "{prompt}"

Gere um código Python usando plotly express para criar o gráfico solicitado.
Use apenas as bibliotecas: pandas, plotly.express, plotly.graph_objects
Assuma que os dataframes já estão carregados no dicionário 'data'.
Retorne APENAS o código Python, sem explicações.
O código deve criar uma variável 'fig' com o gráfico plotly.
"""

        response = model.generate_content(context)
        code = response.text

        # Limpar código
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]

        code = code.strip()

        # Executar código
        local_vars = {"data": data, "pd": pd, "px": px, "go": go}
        exec(code, local_vars)

        if "fig" in local_vars:
            st.plotly_chart(local_vars["fig"], use_container_width=True)
        else:
            st.error("O código gerado não criou uma variável 'fig'")

    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {e}")
        st.code(code if "code" in locals() else "Código não gerado")


def main() -> None:
    """Função principal da aplicação."""

    # Header
    st.title("🎬 Movies Big Data Analytics")
    st.markdown("### Dashboard Interativo com IA Generativa")

    # Carregar dados
    with st.spinner("Carregando dados..."):
        data = load_data()

    if not data:
        st.error(
            "❌ Dados não encontrados! Execute primeiro o pipeline: `python -m src.main`"
        )
        return

    # Sidebar
    st.sidebar.title("🎛️ Controles")

    # Configurar Gemini
    gemini_model = configure_gemini()

    if gemini_model:
        st.sidebar.success("✅ Gemini AI conectado")
    else:
        st.sidebar.warning("⚠️ Gemini AI não configurado")
        st.sidebar.info(
            "Adicione GOOGLE_API_KEY no .env para habilitar análises com IA"
        )

    # Estatísticas rápidas na sidebar
    movies_df = data.get("movies", pd.DataFrame())
    if not movies_df.empty:
        st.sidebar.divider()
        st.sidebar.markdown("### 📊 Estatísticas Rápidas")
        st.sidebar.metric("Total de Filmes", f"{len(movies_df):,}")
        st.sidebar.metric("Diretores", f"{data['directors'].shape[0]:,}")
        st.sidebar.metric("Gêneros", f"{data['genres'].shape[0]}")

    # Inicializar estado da tab se não existir
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0

    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Overview", "🎬 Filmes", "🤖 Análise com IA", "📈 Gráficos Customizados"]
    )

    # ==================== TAB 1: OVERVIEW ====================
    with tab1:
        st.header("📊 Visão Geral do Dataset")

        # Métricas principais
        if not movies_df.empty:
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric(
                    "Total de Filmes",
                    f"{len(movies_df):,}",
                )

            with col2:
                movies_with_finance = movies_df[
                    movies_df["has_budget"] & movies_df["has_revenue"]
                ]
                avg_revenue = movies_with_finance["revenue"].mean()
                st.metric(
                    "Receita Média",
                    f"${avg_revenue/1e6:.1f}M",
                )

            with col3:
                avg_rating = movies_df[movies_df["vote_average"] > 0][
                    "vote_average"
                ].mean()
                st.metric(
                    "Nota Média",
                    f"{avg_rating:.1f}/10",
                )

            with col4:
                year_range = f"{int(movies_df['release_year'].min())} - {int(movies_df['release_year'].max())}"
                st.metric(
                    "Período",
                    year_range,
                )
            
            with col5:
                total_revenue = movies_with_finance["revenue"].sum()
                st.metric(
                    "Receita Total",
                    f"${total_revenue/1e9:.1f}B",
                )

            st.divider()

            # Primeira linha de gráficos
            col1, col2 = st.columns(2)

            with col1:
                # Evolução temporal
                yearly_df = data.get("yearly", pd.DataFrame())
                if not yearly_df.empty:
                    yearly_recent = yearly_df[yearly_df["release_year"] >= 1990]

                    fig = go.Figure()
                    
                    # Linha de filmes
                    fig.add_trace(go.Scatter(
                        x=yearly_recent["release_year"],
                        y=yearly_recent["movie_count"],
                        mode='lines+markers',
                        name='Filmes Produzidos',
                        line=dict(color='#1f77b4', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(31, 119, 180, 0.2)'
                    ))
                    
                    fig.update_layout(
                        title="📅 Produção de Filmes por Ano (1990+)",
                        xaxis_title="Ano",
                        yaxis_title="Número de Filmes",
                        hovermode='x unified',
                        template='plotly_dark'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Top gêneros
                genres_df = data.get("genres", pd.DataFrame())
                if not genres_df.empty:
                    top_genres = genres_df.nlargest(10, "movie_count")

                    fig = px.bar(
                        top_genres,
                        x="movie_count",
                        y="genre_names",
                        orientation="h",
                        title="🎭 Top 10 Gêneros por Número de Filmes",
                        labels={
                            "movie_count": "Número de Filmes",
                            "genre_names": "Gênero",
                        },
                        color="movie_count",
                        color_continuous_scale="Blues",
                        template='plotly_dark'
                    )
                    fig.update_layout(yaxis={"categoryorder": "total ascending"})
                    st.plotly_chart(fig, use_container_width=True)

            # Segunda linha de gráficos
            col1, col2 = st.columns(2)

            with col1:
                # Evolução de receita
                if not yearly_df.empty:
                    yearly_recent = yearly_df[yearly_df["release_year"] >= 1990]
                    
                    fig = go.Figure()
                    
                    # Receita total
                    fig.add_trace(go.Bar(
                        x=yearly_recent["release_year"],
                        y=yearly_recent["total_revenue"] / 1e9,
                        name='Receita Total',
                        marker_color='#2ecc71',
                        opacity=0.7
                    ))
                    
                    # Receita média (linha)
                    fig.add_trace(go.Scatter(
                        x=yearly_recent["release_year"],
                        y=yearly_recent["avg_revenue"] / 1e6,
                        name='Receita Média/Filme',
                        yaxis='y2',
                        line=dict(color='#e74c3c', width=3),
                        mode='lines+markers'
                    ))
                    
                    fig.update_layout(
                        title="💰 Evolução de Receita (1990+)",
                        xaxis_title="Ano",
                        yaxis_title="Receita Total (Bilhões $)",
                        yaxis2=dict(
                            title="Receita Média (Milhões $)",
                            overlaying='y',
                            side='right'
                        ),
                        hovermode='x unified',
                        template='plotly_dark',
                        legend=dict(x=0.01, y=0.99)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Receita por gênero
                if not genres_df.empty:
                    top_revenue_genres = genres_df.nlargest(10, "avg_revenue")
                    
                    fig = px.bar(
                        top_revenue_genres,
                        x="avg_revenue",
                        y="genre_names",
                        orientation="h",
                        title="💵 Top 10 Gêneros por Receita Média",
                        labels={
                            "avg_revenue": "Receita Média ($)",
                            "genre_names": "Gênero",
                        },
                        color="avg_revenue",
                        color_continuous_scale="Greens",
                        template='plotly_dark'
                    )
                    fig.update_layout(yaxis={"categoryorder": "total ascending"})
                    fig.update_traces(
                        hovertemplate='<b>%{y}</b><br>Receita: $%{x:,.0f}<extra></extra>'
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Terceira linha - Análise de avaliações
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribuição de avaliações
                movies_rated = movies_df[movies_df["vote_average"] > 0]
                
                fig = px.histogram(
                    movies_rated,
                    x="vote_average",
                    nbins=20,
                    title="⭐ Distribuição de Avaliações",
                    labels={"vote_average": "Nota (0-10)", "count": "Número de Filmes"},
                    color_discrete_sequence=['#f39c12'],
                    template='plotly_dark'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top diretores
                directors_df = data.get("directors", pd.DataFrame())
                if not directors_df.empty:
                    top_directors = directors_df.nlargest(10, "total_revenue")
                    
                    fig = px.bar(
                        top_directors,
                        x="total_revenue",
                        y="director",
                        orientation="h",
                        title="🎬 Top 10 Diretores por Receita Total",
                        labels={
                            "total_revenue": "Receita Total ($)",
                            "director": "Diretor",
                        },
                        color="total_revenue",
                        color_continuous_scale="Purples",
                        template='plotly_dark'
                    )
                    fig.update_layout(yaxis={"categoryorder": "total ascending"})
                    fig.update_traces(
                        hovertemplate='<b>%{y}</b><br>Receita: $%{x:,.0f}<extra></extra>'
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # ==================== TAB 2: FILMES ====================
    with tab2:
        st.header("🎬 Explorador de Filmes")

        top_movies_df = data.get("top_movies", pd.DataFrame())

        if not top_movies_df.empty:
            # Controles de filtro
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                rank_type = st.selectbox(
                    "Ranking por:",
                    ["revenue", "profit", "rating"],
                    format_func=lambda x: {
                        "revenue": "💰 Receita",
                        "profit": "💵 Lucro",
                        "rating": "⭐ Avaliação",
                    }[x],
                )
            
            with col2:
                top_n = st.slider("Mostrar top:", 5, 50, 20)
            
            with col3:
                view_mode = st.radio("Visualização:", ["Tabela", "Cards"], horizontal=True)

            filtered = top_movies_df[top_movies_df["rank_type"] == rank_type].head(top_n)

            st.divider()

            if view_mode == "Tabela":
                # Tabela interativa
                st.dataframe(
                    filtered[
                        [
                            "rank",
                            "title",
                            "release_year",
                            "revenue",
                            "profit",
                            "roi",
                            "vote_average",
                        ]
                    ]
                    .style.format(
                        {
                            "revenue": "${:,.0f}",
                            "profit": "${:,.0f}",
                            "roi": "{:.1f}%",
                            "vote_average": "{:.1f}",
                            "release_year": "{:.0f}"
                        }
                    )
                    .background_gradient(cmap="Blues", subset=["revenue", "profit"]),
                    use_container_width=True,
                    height=600
                )
            else:
                # View em cards
                for i in range(0, len(filtered), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(filtered):
                            movie = filtered.iloc[i + j]
                            with col:
                                st.markdown(f"""
                                <div style='background-color: #262730; padding: 20px; border-radius: 10px; border: 1px solid #404040; height: 200px;'>
                                    <h4 style='color: #3498db; margin: 0;'>#{int(movie['rank'])} {movie['title']}</h4>
                                    <p style='color: #95a5a6; margin: 5px 0;'>Ano: {int(movie['release_year'])}</p>
                                    <hr style='margin: 10px 0; border-color: #404040;'>
                                    <p style='margin: 5px 0;'><b>💰 Receita:</b> ${movie['revenue']/1e6:.1f}M</p>
                                    <p style='margin: 5px 0;'><b>💵 Lucro:</b> ${movie['profit']/1e6:.1f}M</p>
                                    <p style='margin: 5px 0;'><b>⭐ Nota:</b> {movie['vote_average']:.1f}/10</p>
                                    <p style='margin: 5px 0;'><b>📈 ROI:</b> {movie['roi']:.0f}%</p>
                                </div>
                                """, unsafe_allow_html=True)

            st.divider()

            # Gráficos de análise
            col1, col2 = st.columns(2)

            with col1:
                # Gráfico de barras principal
                metric_col = "revenue" if rank_type == "revenue" else "profit" if rank_type == "profit" else "vote_average"
                metric_name = {"revenue": "Receita", "profit": "Lucro", "vote_average": "Avaliação"}[rank_type]
                
                fig = px.bar(
                    filtered.head(15),
                    x=metric_col if rank_type != "rating" else "vote_average",
                    y="title",
                    orientation="h",
                    title=f"Top 15 Filmes por {metric_name}",
                    labels={metric_col: metric_name, "title": "Filme", "vote_average": "Nota"},
                    color=metric_col if rank_type != "rating" else "vote_average",
                    color_continuous_scale="Viridis" if rank_type != "rating" else "YlOrRd",
                    template='plotly_dark'
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=600)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Scatter plot - Relação entre métricas
                fig = go.Figure()
                
                # Scatter de budget vs revenue
                movies_with_data = movies_df[
                    (movies_df["has_budget"]) & (movies_df["has_revenue"]) & (movies_df["budget"] > 0)
                ].head(500)
                
                fig.add_trace(go.Scatter(
                    x=movies_with_data["budget"] / 1e6,
                    y=movies_with_data["revenue"] / 1e6,
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=movies_with_data["vote_average"],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Nota"),
                        line=dict(width=0.5, color='white')
                    ),
                    text=movies_with_data["title"],
                    hovertemplate='<b>%{text}</b><br>Orçamento: $%{x:.1f}M<br>Receita: $%{y:.1f}M<extra></extra>',
                    showlegend=False
                ))
                
                # Linha de referência ROI 100%
                max_val = max(movies_with_data["budget"].max(), movies_with_data["revenue"].max()) / 1e6
                fig.add_trace(go.Scatter(
                    x=[0, max_val],
                    y=[0, max_val],
                    mode='lines',
                    line=dict(color='red', dash='dash', width=2),
                    name='ROI = 100%',
                    hoverinfo='skip'
                ))
                
                fig.update_layout(
                    title="💰 Orçamento vs Receita (Top 500 filmes)",
                    xaxis_title="Orçamento (Milhões $)",
                    yaxis_title="Receita (Milhões $)",
                    template='plotly_dark',
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)

            # Análise temporal dos top filmes
            st.subheader("📅 Análise Temporal")
            
            yearly_top = filtered.groupby("release_year").agg({
                "revenue": "mean",
                "profit": "mean",
                "vote_average": "mean",
                "title": "count"
            }).reset_index()
            yearly_top.columns = ["release_year", "avg_revenue", "avg_profit", "avg_rating", "count"]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=yearly_top["release_year"],
                y=yearly_top["count"],
                name='Número de Filmes',
                marker_color='rgba(55, 128, 191, 0.7)',
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=yearly_top["release_year"],
                y=yearly_top["avg_revenue"] / 1e6,
                name='Receita Média',
                line=dict(color='#2ecc71', width=3),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="📊 Distribuição Temporal dos Top Filmes",
                xaxis_title="Ano",
                yaxis_title="Número de Filmes",
                yaxis2=dict(
                    title="Receita Média (Milhões $)",
                    overlaying='y',
                    side='right'
                ),
                template='plotly_dark',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)

    # ==================== TAB 3: ANÁLISE COM IA ====================
    with tab3:
        st.header("🤖 Análise com IA Generativa")

        if not gemini_model:
            st.warning(
                "⚠️ Configure GOOGLE_API_KEY no arquivo .env para usar este recurso"
            )
            st.info(
                "Obtenha sua chave em: https://makersuite.google.com/app/apikey"
            )
        else:
            st.markdown(
                "💬 Pergunte qualquer coisa sobre os dados em linguagem natural!"
            )

            # Inicializar mensagens se não existir
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Container para o histórico de mensagens
            chat_container = st.container()
            
            with chat_container:
                # Exibir histórico
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Input do usuário (sempre no final)
            if prompt := st.chat_input("Ex: Qual é a tendência de receita ao longo dos anos?"):
                # Adicionar mensagem do usuário
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Exibir mensagem do usuário imediatamente
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    # Gerar resposta
                    with st.chat_message("assistant"):
                        with st.spinner("Pensando..."):
                            try:
                                # Criar contexto detalhado com dados temporais
                                yearly_df = data.get('yearly', pd.DataFrame())
                                
                                # Dados de tendência temporal (últimos 30 anos)
                                recent_years = yearly_df[yearly_df['release_year'] >= 1990].copy() if not yearly_df.empty else pd.DataFrame()
                                
                                temporal_context = ""
                                if not recent_years.empty:
                                    temporal_context = f"""

DADOS TEMPORAIS DISPONÍVEIS (1990-2017):
- Anos com dados: {len(recent_years)} anos
- Receita total por ano: de ${recent_years['total_revenue'].min()/1e9:.1f}B a ${recent_years['total_revenue'].max()/1e9:.1f}B
- Receita média por filme: de ${recent_years['avg_revenue'].min()/1e6:.1f}M a ${recent_years['avg_revenue'].max()/1e6:.1f}M
- Tendência de filmes: de {int(recent_years['movie_count'].min())} filmes/ano em {int(recent_years.iloc[0]['release_year'])} para {int(recent_years['movie_count'].max())} em {int(recent_years.loc[recent_years['movie_count'].idxmax(), 'release_year'])}
- Década de 1990: receita média ${recent_years[recent_years["release_year"] < 2000]["avg_revenue"].mean()/1e6:.1f}M/filme
- Década de 2000: receita média ${recent_years[(recent_years["release_year"] >= 2000) & (recent_years["release_year"] < 2010)]["avg_revenue"].mean()/1e6:.1f}M/filme
- Década de 2010: receita média ${recent_years[recent_years["release_year"] >= 2010]["avg_revenue"].mean()/1e6:.1f}M/filme

DADOS COMPLETOS POR ANO (amostra dos últimos 5 anos):
{recent_years[['release_year', 'movie_count', 'avg_revenue', 'total_revenue', 'avg_profit']].tail(5).to_string(index=False)}
"""
                                
                                movies_summary = f"""
Você é um analista de dados especializado em cinema. Analise os dados a seguir para responder à pergunta do usuário.

RESUMO GERAL DOS DADOS:
- Total de filmes no dataset: {len(data.get('movies', []))}
- Período completo: {int(data['movies']['release_year'].min())} a {int(data['movies']['release_year'].max())}
- Receita média global: ${data['movies']['revenue'].mean()/1e6:.1f}M
- Nota média: {data['movies']['vote_average'].mean():.1f}/10
- Top 5 gêneros: {', '.join(data['genres'].nlargest(5, 'movie_count')['genre_names'].tolist())}
{temporal_context}

PERGUNTA DO USUÁRIO: {prompt}

INSTRUÇÕES:
1. Use os DADOS TEMPORAIS acima para responder questões sobre tendências ao longo do tempo
2. Forneça números específicos e percentuais quando relevante
3. Identifique padrões e insights interessantes
4. Seja específico e baseado em dados, não genérico
5. Se a pergunta é sobre tendências temporais, SEMPRE use os dados temporais fornecidos
"""

                                response = gemini_model.generate_content(movies_summary)
                                answer = response.text

                                st.markdown(answer)

                                # Adicionar à sessão
                                st.session_state.messages.append(
                                    {"role": "assistant", "content": answer}
                                )
                            except Exception as e:
                                error_msg = f"Erro ao processar sua pergunta: {str(e)}"
                                st.error(error_msg)
                                st.session_state.messages.append(
                                    {"role": "assistant", "content": error_msg}
                                )

            # Botão para limpar histórico
            if st.session_state.messages:
                if st.button("🗑️ Limpar Histórico"):
                    st.session_state.messages = []
                    st.rerun()

    # ==================== TAB 4: GRÁFICOS CUSTOMIZADOS ====================
    with tab4:
        st.header("📈 Gráficos Customizados com IA")

        if not gemini_model:
            st.warning(
                "⚠️ Configure GOOGLE_API_KEY no arquivo .env para usar este recurso"
            )
        else:
            st.markdown(
                "🎨 Descreva o gráfico que você quer ver e a IA irá criá-lo para você!"
            )

            examples = st.expander("📝 Ver exemplos de comandos")
            with examples:
                st.markdown(
                    """
                - "Mostre um gráfico de linha da evolução da receita média por ano"
                - "Crie um gráfico de barras dos 10 diretores com maior receita total"
                - "Faça um scatter plot relacionando budget e revenue"
                - "Mostre um gráfico de pizza com a distribuição dos top 5 gêneros"
                - "Crie um gráfico de área mostrando a evolução do número de filmes por ano"
                """
                )

            chart_prompt = st.text_area(
                "Descreva o gráfico:",
                placeholder="Ex: Mostre a evolução da receita média dos filmes ao longo dos anos",
                height=100,
            )

            if st.button("🎨 Gerar Gráfico", type="primary"):
                if chart_prompt:
                    with st.spinner("Gerando gráfico..."):
                        generate_chart_with_ai(chart_prompt, data, gemini_model)
                else:
                    st.warning("Digite uma descrição para o gráfico")


if __name__ == "__main__":
    main()
