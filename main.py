import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date
from PIL import Image
from io import BytesIO
from fpdf import FPDF

# Configurando a página
st.set_page_config(layout="wide")

# Conexão com banco SQLite
DB_PATH = "data/pcm.db"
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()

try:
    c.execute("ALTER TABLE ordens ADD COLUMN conclusao TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass 

try:
    c.execute("ALTER TABLE ordens ADD COLUMN imagem BLOB")
    conn.commit()
except sqlite3.OperationalError:
    pass

# Criar tabelas se não existirem
c.execute('''CREATE TABLE IF NOT EXISTS ativos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    codigo TEXT,
    local TEXT,
    fabricante TEXT,
    aquisicao TEXT,
    observacoes TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS ordens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipamento TEXT,
    tipo TEXT,
    descricao TEXT,
    abertura TEXT,
    execucao TEXT,
    responsavel TEXT,
    status TEXT,
    conclusao TEXT,
    imagem BLOB
)''')

conn.commit()

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

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
    st.stop()

# Menu lateral
tipo_usuario = st.session_state.get("tipo", "")
if tipo_usuario == "manutencao":
    menu = ["🏠 Início", "🏭 Ativos", "🛠️ Ordens de Serviço", "📜 Histórico", "📊 Relatórios", "📩 Solicitar Manutenção"]
else:
    menu = ["🏠 Início", "📩 Solicitar Manutenção"]

opcao = st.sidebar.selectbox("Navegar", menu)
with st.sidebar:
    st.markdown("---")
    st.write(f"👤 Usuário: `{st.session_state['usuario']}`")
    if st.button("🚪 Sair"):
        st.session_state.clear()
        st.rerun()

if opcao == "🏠 Início":
    st.title("🔧 Sistema de PCM - Manutenção Industrial")
    st.markdown("Bem-vindo ao sistema de Planejamento e Controle da Manutenção (PCM) da Bandeirante Maquinas")

    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **Este sistema permite:**
        - Cadastrar e visualizar ativos industriais
        - Registrar e acompanhar ordens de serviço (preventiva e corretiva)
        - Consultar histórico de manutenções
        - Visualizar relatórios simples de desempenho
        """)
    with col2:
        st.success("""
        **Para usuários comuns:**
        - Solicite manutenção de forma simples e rápida
        - Descreva problemas encontrados nos equipamentos
        - Acompanhe o status da sua solicitação
        """)

    st.markdown("---")
    st.subheader("📊 Visão Geral Rápida")

    # Dados básicos
    total_ativos = c.execute("SELECT COUNT(*) FROM ativos").fetchone()[0]
    total_ordens = c.execute("SELECT COUNT(*) FROM ordens").fetchone()[0]
    ordens_abertas = c.execute("SELECT COUNT(*) FROM ordens WHERE status = 'Aberta'").fetchone()[0]
    ordens_finalizadas = c.execute("SELECT COUNT(*) FROM ordens WHERE status = 'Finalizada'").fetchone()[0]

    # Novos indicadores
    ordens_corretivas = c.execute("SELECT COUNT(*) FROM ordens WHERE tipo = 'Corretiva'").fetchone()[0]
    ordens_preventivas = c.execute("SELECT COUNT(*) FROM ordens WHERE tipo = 'Preventiva'").fetchone()[0]

    # Tempo médio de conclusão (em dias)
    df_tempo = pd.read_sql("SELECT abertura, execucao FROM ordens WHERE status = 'Finalizada' AND abertura != '' AND execucao != ''", conn)
    if not df_tempo.empty:
        df_tempo["abertura"] = pd.to_datetime(df_tempo["abertura"], errors="coerce")
        df_tempo["execucao"] = pd.to_datetime(df_tempo["execucao"], errors="coerce")
        df_tempo["dias"] = (df_tempo["execucao"] - df_tempo["abertura"]).dt.days
        tempo_medio = df_tempo["dias"].mean()
        tempo_medio_str = f"{tempo_medio:.1f}"
    else:
        tempo_medio_str = "N/A"

    # Percentual de ordens finalizadas
    percentual_finalizadas = (ordens_finalizadas / total_ordens * 100) if total_ordens > 0 else 0

    # CSS personalizado para caixas estilizadas
    # Substitua todo o CSS e HTML dos cards por este código:
    
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] > div:nth-child(1) > div > div {
            overflow: visible;
        }

        .card-container {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
            width: 100%;
        }

        .card {
            background: linear-gradient(135deg, #4B6CB7, #182848);
            color: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 160px;
            flex: 1;
        }

        .card.yellow {
            background: linear-gradient(135deg, #F7971E, #FFD200);
            color: #333;
        }

        .card h3 {
            margin: 0 0 8px 0;
            font-size: 1rem;
            font-weight: 600;
        }

        .card p {
            margin: 0;
            font-size: 1.6rem;
            font-weight: 700;
        }

        /* Ajuste para evitar quebra de layout no Streamlit */
        .st-emotion-cache-ocqkz7 {
            flex-wrap: wrap;
        }
        </style>
        """, unsafe_allow_html=True)

        # HTML dos cards - versão corrigida
    st.markdown(f"""
        <div class="card-container">
            <div class="card">
                <h3>Ativos Cadastrados</h3>
                <p>{total_ativos}</p>
            </div>
            <div class="card yellow">
                <h3>Ordens de Serviço</h3>
                <p>{total_ordens}</p>
            </div>
            <div class="card">
                <h3>OS Abertas</h3>
                <p>{ordens_abertas}</p>
            </div>
            <div class="card yellow">
                <h3>OS Finalizadas</h3>
                <p>{ordens_finalizadas}</p>
            </div>
            <div class="card">
                <h3>Ordens Corretivas</h3>
                <p>{ordens_corretivas}</p>
            </div>
            <div class="card yellow">
                <h3>Ordens Preventivas</h3>
                <p>{ordens_preventivas}</p>
            </div>
            <div class="card">
                <h3>Tempo Médio (dias)</h3>
                <p>{tempo_medio_str}</p>
            </div>
            <div class="card yellow">
                <h3>Percentual Finalizadas</h3>
                <p>{percentual_finalizadas:.1f}%</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


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
            c.execute("INSERT INTO ativos (nome, codigo, local, fabricante, aquisicao, observacoes) VALUES (?, ?, ?, ?, ?, ?)",
                      (nome, codigo, local, fabricante, str(aquisicao), obs))
            conn.commit()
            st.success("Ativo cadastrado com sucesso!")

    ativos = pd.read_sql("SELECT * FROM ativos", conn)
    st.subheader("Lista de Ativos")
    st.dataframe(ativos, use_container_width=True)

# Página: Ordens de Serviço
elif opcao == "🛠️ Ordens de Serviço":
    st.title("Ordens de Serviço")
    df = pd.read_sql("SELECT * FROM ordens", conn)

    st.subheader("📋 Solicitações Abertas")
    ordens_abertas = df[df['status'] != 'Finalizada']
    ordem_escolhida = st.selectbox("Selecione uma OS para visualizar e editar", ordens_abertas["id"].astype(str) + " - " + ordens_abertas["equipamento"])

    if ordem_escolhida:
        ordem_id = int(ordem_escolhida.split(" - ")[0])
        os_detalhe = df[df['id'] == ordem_id].iloc[0]

        st.markdown(f"### Equipamento: {os_detalhe['equipamento']}")
        st.markdown(f"**Tipo:** {os_detalhe['tipo']}")
        st.markdown(f"**Descrição:** {os_detalhe['descricao']}")
        st.markdown(f"**Abertura:** {os_detalhe['abertura']}")
        st.markdown(f"**Responsável:** {os_detalhe['responsavel']}")

        status = st.selectbox("Atualizar Status", ["Aberta", "Em andamento", "Finalizada"], index=["Aberta", "Em andamento", "Finalizada"].index(os_detalhe['status']))
        conclusao = st.text_area("Descrever o que foi feito")
        imagem = st.file_uploader("Upload de imagem (opcional)", type=["png", "jpg", "jpeg"])

        if st.button("Salvar Alterações"):
            imagem_bytes = imagem.read() if imagem else None
            c.execute("""
                UPDATE ordens
                SET status = ?, conclusao = ?, imagem = ?
                WHERE id = ?
            """, (status, conclusao, imagem_bytes, ordem_id))
            conn.commit()
            st.success("Ordem atualizada com sucesso!")
            st.rerun()

        if st.button("📄 Gerar PDF"):
            pdf = FPDF()
            pdf.add_page()

            # Cabeçalho
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"Relatório da Ordem de Serviço #{ordem_id}", ln=True, align='C')
            pdf.ln(10)

            # Dados principais
            pdf.set_font("Arial", '', 12)
            pdf.cell(50, 10, "Equipamento:", ln=False)
            pdf.cell(0, 10, os_detalhe['equipamento'], ln=True)
            pdf.cell(50, 10, "Tipo:", ln=False)
            pdf.cell(0, 10, os_detalhe['tipo'], ln=True)
            pdf.cell(50, 10, "Data de Abertura:", ln=False)
            pdf.cell(0, 10, os_detalhe['abertura'], ln=True)
            pdf.cell(50, 10, "Data de Execução:", ln=False)
            pdf.cell(0, 10, os_detalhe['execucao'], ln=True)
            pdf.cell(50, 10, "Responsável:", ln=False)
            pdf.cell(0, 10, os_detalhe['responsavel'], ln=True)
            pdf.cell(50, 10, "Status:", ln=False)
            pdf.cell(0, 10, status, ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Descrição da Ordem:", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 10, os_detalhe['descricao'])

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Conclusão:", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 10, conclusao)

            # Inserir imagem (se houver)
            if os_detalhe['imagem']:
                img_path = f"temp_os_{ordem_id}.jpg"
                with open(img_path, "wb") as f:
                    f.write(os_detalhe['imagem'])

                pdf.ln(10)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "Imagem da Manutenção:", ln=True)
                pdf.image(img_path, x=10, w=100)
                os.remove(img_path)

            # Salvar e baixar
            pdf_path = f"relatorio_os_{ordem_id}.pdf"
            pdf.output(pdf_path)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Baixar PDF", f, file_name=pdf_path)

            st.subheader("📚 Todas as Ordens")
            st.dataframe(df, use_container_width=True)

# Página: Histórico
elif opcao == "📜 Histórico":
    st.title("Histórico de Manutenção")
    historico = pd.read_sql("SELECT * FROM ordens WHERE status = 'Finalizada'", conn)
    st.dataframe(historico, use_container_width=True)

# Página: Relatórios
elif opcao == "📊 Relatórios":
    st.title("Relatórios Básicos")
    df = pd.read_sql("SELECT * FROM ordens", conn)

    if not df.empty:
        st.subheader("Total de Manutenções por Equipamento")
        st.bar_chart(df["equipamento"].value_counts())

        st.subheader("Manutenções por Tipo")
        st.bar_chart(df["tipo"].value_counts())

        df["abertura"] = pd.to_datetime(df["abertura"], errors="coerce")
        df["execucao"] = pd.to_datetime(df["execucao"], errors="coerce")
        df["dias"] = (df["execucao"] - df["abertura"]).dt.days
        st.metric("Tempo Médio (dias)", f"{df['dias'].mean():.1f}")
    else:
        st.info("Nenhuma ordem registrada ainda.")

# Página: Solicitação de Manutenção
elif opcao == "📩 Solicitar Manutenção":
    st.title("Solicitação de Manutenção")
    ativos = pd.read_sql("SELECT nome FROM ativos", conn)

    with st.form("form_solicitacao"):
        equipamento = st.selectbox("Equipamento", ativos["nome"] if not ativos.empty else [])
        descricao = st.text_area("Descreva o problema")
        data = st.date_input("Data da solicitação", value=date.today())
        solicitante = st.text_input("Seu nome")
        enviar = st.form_submit_button("Enviar Solicitação")

        if enviar:
            c.execute('''
                INSERT INTO ordens (
                    equipamento, tipo, descricao, abertura, execucao, responsavel, status, conclusao, imagem
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                equipamento,
                'Corretiva',
                descricao,
                str(data),
                '',  # execucao
                solicitante,
                'Aberta',
                '',  # conclusao
                None  # imagem
            ))
            conn.commit()
            st.success("Solicitação enviada com sucesso!")

