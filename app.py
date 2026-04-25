import streamlit as st
from database import session, Companhia, Movimentacao, ItemChecklist
from datetime import datetime
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO VISUAL (LAYOUT PHOENIX PRO) ---
st.set_page_config(page_title="Phoenix Insurance - Gestão", layout="wide")

st.markdown("""
    <style>
    /* Fundo Azul Phoenix */
    .stApp {
        background-color: #002b5c !important;
    }
    
    /* Forçar todos os títulos e textos informativos para Branco */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stSubheader, [data-testid="stHeader"] {
        color: #ffffff !important;
    }

    /* BARRA LATERAL: Cinza claro com texto preto */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
    }
    [data-testid="stSidebar"] * {
        color: #000000 !important;
    }

    /* LABELS (Títulos dos campos) sempre em Branco */
    label, [data-testid="stWidgetLabel"] p, .stCheckbox p {
        color: #ffffff !important;
        font-weight: 600 !important;
        background-color: transparent !important;
    }

    /* INPUTS E SELECTBOXES: Fundo branco e Letra Preta Nítida */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
    }
/* BOTÃO SALVAR: Estilo Phoenix (Branco com Letra Preta) */
div.stButton > button {
    background-color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    height: 3.5em !important;
    width: 100% !important;
    transition: 0.3s;
}

/* Garante que o texto DENTRO do botão seja preto e negrito */
div.stButton > button p {
    color: #000000 !important;
    font-weight: bold !important;
    font-size: 16px !important;
}

/* Efeito ao passar o mouse para o usuário saber que clicou */
div.stButton > button:hover {
    background-color: #e0e0e0 !important;
}
  

    /* Ajuste de abas para não sumirem no azul */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 5px 5px 0 0;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGO E LOGIN ---
for ext in [".jpg", ".jpeg", ".png", ".JPG", ".JPEG"]:
    if os.path.exists(f"logo{ext}"):
        st.sidebar.image(f"logo{ext}", use_container_width=True)
        break

st.sidebar.title("🔑 Acesso ao Sistema")
perfil = st.sidebar.selectbox("Escolha o Perfil:", ["Pós-Vendas", "Administrador"])

admin_liberado = False
if perfil == "Administrador":
    senha = st.sidebar.text_input("Senha de Administrador:", type="password")
    if senha == "1234":
        admin_liberado = True
        st.sidebar.success("✅ ACESSO LIBERADO")
    elif senha != "":
        st.sidebar.error("❌ SENHA INCORRETA")
else:
    st.sidebar.info("🟦 PÓS-VENDAS ATIVO")

st.title("📋 Sistema de Movimentação")

# --- 3. DEFINIÇÃO DAS ABAS ---
if admin_liberado:
    tab1, tab2, tab3 = st.tabs(["🆕 Nova Movimentação", "📂 Gestão de Pendências", "🛠 Painel Admin"])
else:
    tab1, tab2 = st.tabs(["🆕 Nova Movimentação", "📂 Gestão de Pendências"])

# --- ABA 1: NOVA MOVIMENTAÇÃO ---
with tab1:
    st.header("Iniciar Novo Processo")
    cias = [c.nome for c in session.query(Companhia).all()] or ["Amil", "Bradesco", "SulAmérica"]
    
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do Beneficiário:", key="reg_nome")
        empresa = st.text_input("Empresa/Estipulante:", key="reg_empresa")
    with col2:
        cia = st.selectbox("Operadora/Seguradora:", cias)
        tipo = st.selectbox("Tipo de Movimentação:", ["Inclusão", "Inclusão compra de carencia", "Exclusão"])
    
    obs = st.text_area("Observações Iniciais:", placeholder="Informações relevantes para o processo...")

    # Definição dinâmica do Checklist
    itens_lista = ["RG/CNH", "CPF", "Comprovante Residência", "Ficha Assinada", "Declaração Saúde", "Elegibilidade"]
    if tipo == "Exclusão":
        itens_lista = ["Carta de Solicitação", "Protocolo", "Verificar Vigência"]
    elif tipo == "Inclusão compra de carencia":
        itens_lista.extend(["Carta Permanência", "3 Faturas", "Informar Compra"])

    st.markdown("---")
    st.subheader("📑 Checklist")
    
    # Organização em 2 colunas para melhor visual
    col_c1, col_c2 = st.columns(2)
    checks_input = {}
    for i, item in enumerate(itens_lista):
        target_col = col_c1 if i % 2 == 0 else col_c2
        checks_input[item] = target_col.checkbox(item, key=f"novo_{item}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Salvar Registro"):
        if nome and empresa:
            existente = session.query(Movimentacao).filter_by(beneficiario=nome, empresa=empresa, data_finalizacao=None).first()
            if existente:
                st.error("⚠️ Este processo já está aberto!")
            else:
                nova_m = Movimentacao(beneficiario=nome, empresa=empresa, tipo=tipo, cia_nome=cia, observacoes=obs)
                session.add(nova_m)
                session.flush()
                for n, v in checks_input.items():
                    session.add(ItemChecklist(nome_item=n, entregue=v, mov_id=nova_m.id))
                session.commit()
                st.success("✅ Registro criado com sucesso!")
                st.rerun()

# --- ABA 2: GESTÃO DE PENDÊNCIAS ---
with tab2:
    st.header("Pendências Atuais")
    pendentes = session.query(Movimentacao).filter(Movimentacao.data_finalizacao == None).all()
    
    if not pendentes:
        st.info("Nenhuma pendência encontrada.")

    for p in pendentes:
        with st.expander(f"⏳ {p.beneficiario} - {p.empresa} ({p.cia_nome})"):
            st.markdown(f"**Tipo:** {p.tipo}")
            nova_obs = st.text_area("Atualizar Notas:", value=p.observacoes if p.observacoes else "", key=f"obs_{p.id}")
            
            st.markdown("---")
            itens_p = session.query(ItemChecklist).filter_by(mov_id=p.id).all()
            novos_status = {}
            
            col_i1, col_i2 = st.columns(2)
            for i, item in enumerate(itens_p):
                target_col_i = col_i1 if i % 2 == 0 else col_i2
                if item.entregue:
                    target_col_i.success(f"✔️ {item.nome_item}")
                    novos_status[item.id] = True
                else:
                    novos_status[item.id] = target_col_i.checkbox(f"Marcar {item.nome_item}", key=f"p_{item.id}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Salvar Alterações", key=f"btn_{p.id}"):
                p.observacoes = nova_obs
                for tid, status in novos_status.items():
                    session.query(ItemChecklist).get(tid).entregue = status
                
                # Se marcar tudo, finaliza
                if all(novos_status.values()):
                    p.data_finalizacao = datetime.now().date()
                    st.toast(f"Processo de {p.beneficiario} finalizado!")
                
                session.commit()
                st.rerun()

# --- ABA 3: PAINEL ADMIN ---
if admin_liberado:
    with tab3:
        st.header("🛠 Painel Administrativo")
        busca = st.text_input("Filtrar por nome do beneficiário:")
        query_adm = session.query(Movimentacao)
        if busca:
            query_adm = query_adm.filter(Movimentacao.beneficiario.like(f"%{busca}%"))
        
        regs = query_adm.all()
        if regs:
            df_admin = pd.DataFrame([
                {"ID": r.id, "Nome": r.beneficiario, "Empresa": r.empresa, "Status": "Concluído" if r.data_finalizacao else "Pendente"} 
                for r in regs
            ])
            st.dataframe(df_admin, use_container_width=True)
        else:
            st.info("Nenhum registro encontrado para a busca.")
