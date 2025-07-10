import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import altair as alt
from trip_control import TripControl, toggle_menu

GIST_ID_FIXO = "17d8f1120822dd11c2c519883d0ce963"
st.set_page_config(page_title="Assistente Viagem", layout="wide")

st.title("📱 Bem-vindo ao Assistente de Viagem 💸")

# Autenticação
if 'controle' not in st.session_state:
    st.session_state.controle = None

if st.session_state.controle is None:
    st.info("Insira seu Token do GitHub para iniciar.")
    with st.form("login_form"):
        st.text_input("ID do Gist (Fixo)", value=GIST_ID_FIXO, disabled=True)
        token_input = st.text_input("Token de Acesso do GitHub", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if not token_input:
                st.warning("Por favor, preencha o Token.")
            else:
                try:
                    controle = TripControl(token=token_input, gist_id=GIST_ID_FIXO)
                    st.session_state.controle = controle
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha no login: {e}")
else:
    controle: TripControl = st.session_state.controle

    if "menu_visivel" not in st.session_state:
        st.session_state.menu_visivel = False
    if "ultima_pagina" not in st.session_state:
        st.session_state.ultima_pagina = "Home"

    col1_button, _ = st.columns([0.05, 0.95])
    with col1_button:
        st.button("☰", on_click=toggle_menu, help="Abrir/Fechar Menu")

    if st.session_state.menu_visivel:
        col_menu, col_conteudo = st.columns([0.2, 0.8])
        
        with col_menu:
            pagina_selecionada = option_menu(
                menu_title=None,
                options=["Home", "Cadastrar", "Dashboard", "Sobre"],
                icons=["house-door-fill", "pencil-square", "bar-chart-line-fill", "info-circle-fill"],
                default_index=["Home", "Cadastrar", "Dashboard", "Sobre"].index(st.session_state.ultima_pagina),
                styles={
                    "container": {"padding": "0!important", "background-color": "#0E1117"},
                    "icon": {"color": "#0d6efd", "font-size": "20px"}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#444"},
                    "nav-link-selected": {"background-color": "#0d6efd"},
                }
            )

        # LÓGICA DE RECOLHIMENTO AUTOMÁTICO
        if pagina_selecionada != st.session_state.ultima_pagina:
            st.session_state.ultima_pagina = pagina_selecionada
            st.session_state.menu_visivel = False
            st.rerun()

    else:
        col_conteudo = st.container()
        pagina_selecionada = st.session_state.ultima_pagina

    st.session_state.ultima_pagina = pagina_selecionada
    
    with col_conteudo:
        if pagina_selecionada == "Home":
            st.subheader("🏠 Home")
            st.info("👈 Clique no '☰' para exibir o menu e navegar pelas funcionalidades.")
            st.markdown("---")

        elif pagina_selecionada == "Cadastrar":
            st.subheader("💸 Cadastrar/Consultar Novo Gasto")
            st.markdown("---")
            tipo_gasto = st.selectbox("Tipo de gasto", ["Combustivel", "Alimentação", "Hotel", "Pedagio", "Lazer"])
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
            data_gasto = st.date_input("Data de Vencimento Inicial")
            data_gasto_str = data_gasto.strftime("%Y-%m-%d")
            if st.button("➕ Adicionar Gasto"):
                dados = controle.consultar_dados()
                dados.append({"tipo_gasto": tipo_gasto, "valor": valor, "data": data_gasto_str})
                controle.atualizar_dados(dados)
                st.success("Dados Cadastrados com sucesso!")
            st.subheader("🏠 Gastos:")
            df = pd.DataFrame(controle.consultar_dados())
            if 'Deletar' not in df.columns:
                df['Deletar'] = False
            df_editado = st.data_editor(df, num_rows="dynamic")
            if st.button("💾 Salvar Alterações"):
                df_filtrado = df_editado[~df_editado['Deletar']]
                dados_para_salvar = df_filtrado.drop(columns=['Deletar']).to_dict(orient='records')
                controle.atualizar_dados(dados_para_salvar)
                st.success("Dados foram alterados com sucesso!")
                st.rerun()
    
        elif pagina_selecionada == "Dashboard":
            st.subheader("📝 Dashboard")
            df = pd.DataFrame(controle.consultar_dados())
            df['data'] = pd.to_datetime(df['data'])
            gasto_total = df['valor'].sum()
            ultimo_dia = df['data'].max()
            penultimo_dia = df['data'].max() - pd.Timedelta(days=1)
            gasto_ultimo_dia = df[df['data'] == ultimo_dia]['valor'].sum()
            gasto_penultimo_dia = df[df['data'] == penultimo_dia]['valor'].sum()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Gasto Total", value=f"R$ {gasto_total:.2f}")
            with col2:
                st.metric(label=f"Gasto em {ultimo_dia.date()}", value=f"R$ {gasto_ultimo_dia:.2f}")
            with col3:
                st.metric(label=f"Gasto em {penultimo_dia.date()}", value=f"R$ {gasto_penultimo_dia:.2f}")

            # Agrupa o valor total por tipo de gasto
            df_agg = df.groupby('tipo_gasto', as_index=False)['valor'].sum()

            # Calcular o ângulo para cada fatia (proporção)
            df_agg['angle'] = df_agg['valor'] / df_agg['valor'].sum() * 2 * 3.1416

            # Criar gráfico de pizza usando mark_arc
            chart = alt.Chart(df_agg).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="valor", type="quantitative"),
                color=alt.Color(field="tipo_gasto", type="nominal"),
                tooltip=['tipo_gasto', 'valor']
            ).properties(
                width=400,
                height=400,
                title='Distribuição de Gastos por Tipo'
            )

            st.altair_chart(chart, use_container_width=True)
                                
        elif pagina_selecionada == "Sobre":
            st.subheader("ℹ️ Sobre o Projeto")
            
