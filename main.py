import streamlit as st
import pandas as pd
import os
from utils.helpers import carregar_dados, salvar_dados

#Configurando pagina
st.set_page_config(layout="wide")

# Dados de login fictícios
usuarios = {
    "admin": {"senha": "admin123", "tipo": "manutencao"},
    "joao": {"senha": "usuario123", "tipo": "usuario"},
    "maria": {"senha": "usuario456", "tipo": "usuario"}
}

# Função de login
def login():
    st.title("🔐 Login no Sistema PCM")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in usuarios and usuarios[usuario]["senha"] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.session_state["tipo"] = usuarios[usuario]["tipo"]
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# Checagem de login
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
    st.stop()


# Crio os caminhos dos arquivos de dados
CAMINHO_ATIVOS = "data/ativos.csv"
CAMINHO_ORDENS = "data/ordens.csv"

# Carrego os dados na inicialização
df_ativos = carregar_dados(CAMINHO_ATIVOS)
df_ordens = carregar_dados(CAMINHO_ORDENS)

# Defino as páginas disponíveis
if st.session_state["tipo"] == "manutencao":
    menu = ["🏠 Início", "🏭 Ativos", "🛠️ Ordens de Serviço", "📜 Histórico", "📊 Relatórios", "📩 Solicitar Manutenção"]
else:
    menu = ["📩 Solicitar Manutenção"]

opcao = st.sidebar.selectbox("Navegar", menu)

with st.sidebar:
    st.markdown("---")
    st.write(f"👤 Usuário: `{st.session_state['usuario']}`")
    if st.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

# Página: Cadastro de Ativos
if opcao == "🏭 Ativos":
    st.title("Cadastro de Ativos")

    with st.form("form_ativo"):
        nome = st.text_input("Nome do Ativo")
        codigo = st.text_input("Código ou Tag")
        local = st.text_input("Localização")
        fabricante = st.text_input("Fabricante / Modelo")
        aquisicao = st.date_input("Data de Aquisição")
        obs = st.text_area("Observações")
        enviar = st.form_submit_button("Salvar")

        if enviar:
            novo = {
                "Nome": nome,
                "Código": codigo,
                "Local": local,
                "Fabricante": fabricante,
                "Data de Aquisição": aquisicao,
                "Observações": obs
            }
            df_ativos = df_ativos._append(novo, ignore_index=True)
            salvar_dados(df_ativos, CAMINHO_ATIVOS)
            st.success("Ativo cadastrado com sucesso!")

    st.subheader("Lista de Ativos")
    st.dataframe(df_ativos, use_container_width=True)

# Página: Registro de O.S.
elif opcao == "🛠️ Ordens de Serviço":
    st.title("Ordens de Serviço")

    with st.form("form_os"):
        equipamento = st.selectbox("Equipamento", df_ativos["Nome"] if not df_ativos.empty else [])
        tipo = st.selectbox("Tipo de Manutenção", ["Preventiva", "Corretiva"])
        descricao = st.text_area("Descrição")
        abertura = st.date_input("Data de Abertura")
        execucao = st.date_input("Data de Execução (ou prevista)")
        responsavel = st.text_input("Responsável")
        status = st.selectbox("Status", ["Aberta", "Em andamento", "Finalizada"])
        enviar = st.form_submit_button("Registrar O.S.")

        if enviar:
            nova_os = {
                "Equipamento": equipamento,
                "Tipo": tipo,
                "Descrição": descricao,
                "Abertura": abertura,
                "Execução": execucao,
                "Responsável": responsavel,
                "Status": status
            }
            df_ordens = df_ordens._append(nova_os, ignore_index=True)
            salvar_dados(df_ordens, CAMINHO_ORDENS)
            st.success("Ordem registrada com sucesso!")

    st.subheader("Ordens Registradas")
    st.dataframe(df_ordens, use_container_width=True)

# Página: Histórico
elif opcao == "📜 Histórico":
    st.title("Histórico de Manutenção")

    historico = df_ordens[df_ordens["Status"] == "Finalizada"]
    st.dataframe(historico, use_container_width=True)

# Página: Relatórios
elif opcao == "📊 Relatórios":
    st.title("Relatórios Básicos")

    if not df_ordens.empty:
        st.subheader("Total de Manutenções por Equipamento")
        man_por_eqp = df_ordens["Equipamento"].value_counts()
        st.bar_chart(man_por_eqp)

        st.subheader("Manutenções por Tipo")
        por_tipo = df_ordens["Tipo"].value_counts()
        st.bar_chart(por_tipo)

        st.subheader("Tempo Médio de Atendimento")
        df_ordens["Abertura"] = pd.to_datetime(df_ordens["Abertura"])
        df_ordens["Execução"] = pd.to_datetime(df_ordens["Execução"])
        df_ordens["Tempo"] = (df_ordens["Execução"] - df_ordens["Abertura"]).dt.days
        tempo_medio = df_ordens["Tempo"].mean()
        st.metric("Tempo Médio (dias)", f"{tempo_medio:.1f}")
    else:
        st.info("Nenhuma ordem registrada ainda.")

# Página: Solicitação de Manutenção
elif opcao == "📩 Solicitar Manutenção":
    st.title("Solicitação de Manutenção")

    with st.form("form_solicitacao"):
        equipamento = st.selectbox("Equipamento", df_ativos["Nome"] if not df_ativos.empty else [])
        descricao = st.text_area("Descreva o problema")
        data = st.date_input("Data da solicitação")
        solicitante = st.text_input("Seu nome")
        enviar = st.form_submit_button("Enviar Solicitação")

        if enviar:
            nova_solicitacao = {
                "Equipamento": equipamento,
                "Tipo": "Corretiva",  # padrão para solicitações
                "Descrição": descricao,
                "Abertura": data,
                "Execução": "",  # ainda não executada
                "Responsável": solicitante,
                "Status": "Aberta"
            }
            df_ordens = df_ordens._append(nova_solicitacao, ignore_index=True)
            salvar_dados(df_ordens, CAMINHO_ORDENS)
            st.success("Solicitação enviada com sucesso!")


