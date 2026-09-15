import os
import sys
from pathlib import Path
import streamlit as st

# Garante codificação UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import GEMINI_API_KEY, GEMINI_MODEL, OUTPUT_DIR
from data_loader import load_companies_data, find_or_create_company
from ai_analyzer import analyze_company
from docx_generator import generate_one_page_docx

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="UFMG Hub — Dossiês Comerciais",
    page_icon="https://ufmghub.com.br/img/logo-hub.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Oficial UFMG Hub (Cores extraídas de ufmghub.com.br)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    /* Tipografia e cores base */
    html, body, [class*="css"], .stMarkdown, p, div, span, label {
        font-family: 'Lexend', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    :root {
        --azul-escuro: #024c76;
        --azul-claro: #57a0bc;
        --laranja: #f6a21c;
        --quase-preto: #0a1c2b;
        --bg-light: #f5f8fa;
        --text-main: #16313f;
        --text-muted: #5e7682;
        --border-color: #e1eaef;
        --radius-md: 14px;
        --shadow-sm: 0 4px 16px -4px rgba(2, 28, 43, 0.08);
    }
    
    /* Cabeçalho do Hub */
    .hub-header {
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 10px 0 20px 0;
        border-bottom: 2px solid var(--border-color);
        margin-bottom: 25px;
    }
    
    .hub-logo {
        height: 60px;
        border-radius: 8px;
    }
    
    .hub-title-container {
        display: flex;
        flex-direction: column;
    }
    
    .hub-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: var(--azul-escuro);
        line-height: 1.15;
        margin: 0;
    }
    
    .hub-title span.orange {
        color: var(--laranja);
    }
    
    .hub-tagline {
        font-size: 0.95rem;
        font-weight: 400;
        color: var(--text-muted);
        letter-spacing: 0.02em;
        margin-top: 4px;
    }
    
    /* Cartões e Métricas */
    .hub-card {
        background-color: var(--bg-light);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 18px 22px;
        box-shadow: var(--shadow-sm);
        margin-bottom: 20px;
    }
    
    .metric-box {
        background: #ffffff;
        border-radius: 10px;
        padding: 14px 18px;
        border-left: 4px solid var(--azul-escuro);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
    }
    
    .metric-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin-bottom: 4px;
    }
    
    .metric-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--azul-escuro);
    }
    
    .metric-sub {
        font-size: 0.85rem;
        color: var(--laranja);
        font-weight: 600;
    }
    
    /* Botões */
    div.stButton > button:first-child {
        background-color: var(--azul-escuro) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(2, 76, 118, 0.25) !important;
    }
    
    div.stButton > button:first-child:hover {
        background-color: var(--quase-preto) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(2, 76, 118, 0.35) !important;
    }
    
    /* Botão de Download Laranja Destaque */
    div[data-testid="stDownloadButton"] > button {
        background-color: var(--laranja) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 14px 28px !important;
        box-shadow: 0 4px 14px rgba(246, 162, 28, 0.35) !important;
    }
    
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #e08f12 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(246, 162, 28, 0.45) !important;
    }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        color: var(--text-muted);
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--azul-escuro) !important;
        border-bottom-color: var(--laranja) !important;
    }
</style>
""", unsafe_allow_html=True)

# Recupera Chave de IA (suporta Streamlit Secrets na nuvem ou .env local)
default_key = ""
try:
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        default_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not default_key:
    default_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY

# Barra Lateral: Configurações de IA
st.sidebar.image("https://ufmghub.com.br/img/logo-hub.png", width=110)
st.sidebar.markdown("### ⚙️ Conexão de IA")

user_key = st.sidebar.text_input(
    "Chave Google Gemini (API Key):",
    value=default_key,
    type="password",
    help="Chave gratuita gerada em aistudio.google.com/app/apikey"
)

if user_key and user_key.strip():
    os.environ["GEMINI_API_KEY"] = user_key.strip()
    st.sidebar.success("🟢 Inteligência Artificial Ativa")
else:
    st.sidebar.warning("⚠️ Chave não configurada. Empresas fora da base usarão dados gerais.")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 💡 Obter Chave Gratuita:")
st.sidebar.markdown("""
1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Clique em **'Create API key'**
3. Cole o código no campo acima!
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**UFMG Hub · Mercado em Conexão**")
st.sidebar.caption("Escola de Engenharia da UFMG")

# Cabeçalho Principal Estilo UFMG Hub
st.markdown("""
<div class="hub-header">
    <img src="https://ufmghub.com.br/img/logo-hub.png" class="hub-logo" alt="UFMG Hub Logo">
    <div class="hub-title-container">
        <h1 class="hub-title">UFMG <span class="orange">Hub</span> &middot; Inteligência Comercial</h1>
        <span class="hub-tagline">Conexão &middot; Ação &middot; Inovação &mdash; Dossiês Estratégicos para a Feira de Carreiras</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Carrega base histórica das 52 empresas
@st.cache_data(show_spinner=False)
def get_cached_companies():
    return load_companies_data()

companies_list = get_cached_companies()
company_names = sorted([c["nome"] for c in companies_list if c.get("nome")])

col_select, col_custom = st.columns([1.2, 1])

with col_select:
    empresa_selecionada = st.selectbox(
        "🏢 Selecione uma empresa cadastrada da Feira UFMG:",
        options=["-- Selecionar da base histórica --"] + company_names,
        index=0
    )

with col_custom:
    empresa_digitada = st.text_input(
        "✍️ Ou digite o nome de QUALQUER empresa para prospecção:",
        placeholder="Ex: Nubank, Embraer, Ambev, Banco Inter, Totvs..."
    )

# Define qual empresa será pesquisada
nome_final = ""
if empresa_digitada.strip():
    nome_final = empresa_digitada.strip()
elif empresa_selecionada != "-- Selecionar da base histórica --":
    nome_final = empresa_selecionada

# Exibe card de dados se houver empresa selecionada
if nome_final:
    comp_info = find_or_create_company(nome_final, companies_list)
    
    st.markdown("<div class='hub-card'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Empresa</div><div class='metric-value'>{comp_info['nome']}</div><div class='metric-sub'>{comp_info.get('origem', 'Base UFMG')}</div></div>", unsafe_allow_html=True)
        
    with c2:
        part_24 = comp_info.get('participou_2024', 'Não')
        cota_24 = comp_info.get('cota_2024', 'N/A')
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Edição 2024</div><div class='metric-value'>{part_24}</div><div class='metric-sub'>Cota: {cota_24}</div></div>", unsafe_allow_html=True)
        
    with c3:
        part_25 = comp_info.get('participou_2025', 'Não')
        cota_25 = comp_info.get('cota_2025', 'N/A')
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Edição 2025</div><div class='metric-value'>{part_25}</div><div class='metric-sub'>Cota: {cota_25}</div></div>", unsafe_allow_html=True)
        
    with c4:
        part_26 = comp_info.get('participou_2026', 'Não')
        cota_26 = comp_info.get('cota_2026', 'N/A')
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Edição 2026</div><div class='metric-value'>{part_26}</div><div class='metric-sub'>Cota: {cota_26}</div></div>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    # Botão de Ação Principal
    btn_gerar = st.button("🚀 Gerar Dossiê Estratégico (3 Páginas em Word)", type="primary", use_container_width=True)
    
    if btn_gerar:
        progresso = st.progress(0, text="Iniciando inteligência de mercado...")
        
        try:
            progresso.progress(25, text="🔍 Mapeando produtos, operações em MG, polos e concorrentes via Google Gemini...")
            comp_data = find_or_create_company(nome_final, companies_list)
            
            ai_data = analyze_company(comp_data)
            
            progresso.progress(70, text="📝 Estruturando documento Word com padrão executivo e dados de feiras...")
            output_file = generate_one_page_docx(comp_data, ai_data)
            
            progresso.progress(100, text="✅ Dossiê concluído!")
            st.balloons()
            
            with open(output_file, "rb") as f:
                docx_bytes = f.read()
                
            st.success(f"🎉 Dossiê Estratégico de **{nome_final}** pronto para uso!")
            
            # Botão de Download Laranja Oficial
            st.download_button(
                label=f"📥 Baixar Dossiê Executivo de {nome_final} (.docx)",
                data=docx_bytes,
                file_name=f"Dossie_Estrategico_{nome_final.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
            
            # Abas com Resumo Visual
            st.markdown("### 📋 Síntese Executiva para Reunião Comercial:")
            tab1, tab2, tab3, tab4 = st.tabs([
                "1.0 Visão Geral & Concorrentes",
                "2.0 Presença em Minas Gerais & BH",
                "5.0 Feiras Verificadas (Poli USP & PUC)",
                "7.0 Playbook de Vendas & Objeções"
            ])
            
            with tab1:
                st.write(ai_data.get("resumo_extenso", "Informação disponível no arquivo Word."))
                
            with tab2:
                st.write(ai_data.get("atuacao_bh_mg_detalhada", "Informação disponível no arquivo Word."))
                
            with tab3:
                feiras_tab = ai_data.get("outras_feiras_tabela", [])
                if feiras_tab:
                    st.table(feiras_tab)
                else:
                    st.info("Sem registro prévio nas feiras da Poli USP e PUC Minas.")
                    
            with tab4:
                st.markdown("**Ganchos de Abertura:**")
                for g in ai_data.get("guia_reuniao_ganchos", []):
                    st.markdown(f"- {g}")
                    
                st.markdown("**Pitch de Valor B2B:**")
                st.info(ai_data.get("guia_reuniao_pitch", ""))
                
                st.markdown("**Matriz de Quebra de Objeções:**")
                obj_list = ai_data.get("guia_reuniao_objecoes", [])
                for item in obj_list:
                    with st.expander(f"❌ Objeção: {item.get('objecao', '')}"):
                        st.write(f"💡 **Resposta recomendada:** {item.get('resposta', '')}")

        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar o dossiê: {e}")
            progresso.empty()

else:
    st.info("👈 Selecione uma empresa acima ou digite o nome de qualquer organização para iniciar a análise.")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #5e7682; font-size: 0.85rem; border-top: 1px solid #e1eaef; padding-top: 20px;">
    © 2026 UFMG Hub &middot; Mercado em Conexão &middot; Escola de Engenharia da UFMG<br>
    Unindo a tradição acadêmica da UFMG à inovação prática do mercado corporativo.
</div>
""", unsafe_allow_html=True)
