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
    page_title="UFMG Hub — Inteligência Comercial",
    page_icon="https://ufmghub.com.br/img/logo-hub.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Enterprise & Responsiva (UFMG Hub Brand Guidelines)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    :root {
        --azul-escuro: #024c76;
        --azul-profundo: #01324e;
        --azul-claro: #57a0bc;
        --laranja: #f6a21c;
        --laranja-hover: #e08f12;
        --quase-preto: #0a1c2b;
        --bg-light: #f8fafc;
        --bg-card: #ffffff;
        --text-main: #16313f;
        --text-muted: #64748b;
        --border-color: #e2e8f0;
        --radius-lg: 16px;
        --radius-md: 10px;
        --shadow-sm: 0 2px 8px rgba(2, 76, 118, 0.06);
        --shadow-md: 0 8px 24px -4px rgba(2, 76, 118, 0.10);
        --shadow-lg: 0 16px 36px -6px rgba(2, 76, 118, 0.16);
    }

    html, body, [class*="css"], .stMarkdown, p, span, label {
        font-family: 'Lexend', 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-main);
    }

    /* Esconde o cabeçalho padrão do Streamlit para controle total do navbar */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Navbar Superior Fixo (Sticky) */
    .sticky-navbar {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 9999;
        background: rgba(255, 255, 255, 0.96);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 2px solid var(--border-color);
        padding: 12px 36px;
        margin: -4.5rem -3.5rem 1.8rem -3.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 20px rgba(2, 28, 43, 0.08);
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .nav-brand img {
        height: 44px;
        object-fit: contain;
    }

    .nav-brand-text {
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--azul-escuro);
        line-height: 1.1;
    }

    .nav-brand-text span {
        color: var(--laranja);
    }

    .nav-brand-sub {
        display: block;
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--azul-claro);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .nav-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    /* Correção do campo de senha no sidebar para não sobrepor o botão de visibilidade */
    div[data-baseweb="input"] input {
        padding-right: 48px !important;
    }

    .hero-container::after {
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(246, 162, 28, 0.22) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-content {
        max-width: 820px;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #f6a21c;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff !important;
        line-height: 1.2;
        margin: 0 0 10px 0;
        letter-spacing: -0.02em;
    }

    .hero-title span {
        color: var(--laranja);
    }

    .hero-subtitle {
        font-size: 1.05rem;
        font-weight: 300;
        color: rgba(255, 255, 255, 0.88);
        line-height: 1.5;
        margin: 0;
    }

    .hero-logo-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 12px 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hero-logo-box img {
        height: 60px;
        object-fit: contain;
    }

    /* Cards de Dados */
    .company-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 24px;
        box-shadow: var(--shadow-sm);
        margin-bottom: 24px;
    }

    .company-card-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--azul-escuro);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .stat-box {
        background: var(--bg-light);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        text-align: center;
        transition: all 0.2s ease;
    }

    .stat-box:hover {
        border-color: var(--azul-claro);
        transform: translateY(-2px);
        box-shadow: var(--shadow-sm);
    }

    .stat-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--text-muted);
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }

    .stat-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--azul-escuro);
        line-height: 1.2;
    }

    .badge-sim {
        display: inline-block;
        background: #e6f6ed;
        color: #0f7642;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .badge-nao {
        display: inline-block;
        background: #f1f5f9;
        color: #64748b;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .badge-cota {
        display: inline-block;
        background: #fff6e8;
        border: 1px solid #fed7aa;
        color: #c2410c;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-top: 4px;
    }

    /* Botão Principal Estilizado */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #024c76 0%, #01324e 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 16px 28px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 4px 16px rgba(2, 76, 118, 0.28) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #035b8d 0%, #024369 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(2, 76, 118, 0.38) !important;
    }

    /* Botão de Download Destaque Laranja */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #f6a21c 0%, #e08f12 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 16px 28px !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        box-shadow: 0 6px 20px rgba(246, 162, 28, 0.35) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }

    div[data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #ffae2b 0%, #e69314 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 28px rgba(246, 162, 28, 0.48) !important;
    }

    /* Abas Customizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 0.92rem;
        color: var(--text-muted);
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: var(--azul-escuro) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    }

    /* Pitch Card */
    .pitch-quote {
        background: #f0f7fb;
        border-left: 5px solid var(--azul-escuro);
        border-radius: 0 10px 10px 0;
        padding: 18px 22px;
        font-style: italic;
        font-size: 1.02rem;
        line-height: 1.6;
        color: var(--azul-profundo);
        margin: 12px 0;
    }

    /* Responsividade Mobile */
    @media (max-width: 768px) {
        .hero-container {
            flex-direction: column;
            text-align: center;
            padding: 24px 20px;
        }
        .hero-logo-box {
            margin-top: 18px;
        }
        .hero-title {
            font-size: 1.7rem;
        }
        .hero-subtitle {
            font-size: 0.95rem;
        }
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

# Barra Lateral: Inteligência e Conexão
with st.sidebar:
    st.image("https://ufmghub.com.br/img/logo-hub.png", width=140)
    st.markdown("### ⚙️ Painel de Controle")
    
    user_key = st.text_input(
        "Chave Google Gemini (API Key):",
        value=default_key,
        type="password",
        help="Chave gratuita gerada em aistudio.google.com/app/apikey"
    )
    
    if user_key and user_key.strip():
        cleaned_key = user_key.strip()
        os.environ["GEMINI_API_KEY"] = cleaned_key
        try:
            env_path = Path(".env")
            current_env = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
            if f"GEMINI_API_KEY={cleaned_key}" not in current_env:
                env_path.write_text(f"GEMINI_API_KEY={cleaned_key}\n", encoding="utf-8")
        except Exception:
            pass
        st.success("🟢 IA Pronta: Gemini 3.6 Flash")
    else:
        st.warning("⚠️ Chave não detectada. Adicione sua chave gratuita abaixo.")
        
    st.markdown("---")
    
    # Status da Base
    st.markdown("#### 📊 Base de Inteligência")
    st.markdown("""
    * **52 Empresas Mapeadas:** Histórico 2024, 2025 e 2026.
    * **Feiras Verificadas:** Workshop Integrativo (Poli USP) e PUC Carreiras (PUC Minas).
    * **Dossiê Padrão:** 3 Páginas Executivas em Word (.docx).
    """)
    
    st.markdown("---")
    st.markdown("#### 🔑 Como pegar a chave grátis:")
    st.markdown("""
    1. Acesse: [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Clique em **'Create API key'**
    3. Cole o código no campo acima!
    """)
    
    st.markdown("---")
    st.caption("© 2026 UFMG Hub · Mercado em Conexão")
    st.caption("Escola de Engenharia da UFMG")

# Navbar Superior Fixo (Sticky) no topo
st.markdown("""
<div class="sticky-navbar">
    <div class="nav-brand">
        <img src="https://ufmghub.com.br/img/logo-hub.png" alt="UFMG Hub">
        <div class="nav-brand-text">
            UFMG <span>Hub</span>
            <span class="nav-brand-sub">Mercado em Conexão &middot; Inteligência Comercial</span>
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 14px;">
        <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-muted);">Escola de Engenharia da UFMG</span>
        <div class="nav-pill">
            <span style="display: inline-block; width: 8px; height: 8px; background: #22c55e; border-radius: 50%;"></span>
            Feira de Carreiras 2026
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-content">
        <div class="hero-badge">🎓 Escola de Engenharia da UFMG &middot; Mercado em Conexão</div>
        <h1 class="hero-title">Dossiês Estratégicos de <span>Patrocínio</span></h1>
        <p class="hero-subtitle">Inteligência comercial B2B para prospecção ativa, reuniões de vendas e retenção de empresas parceiras na Feira de Carreiras.</p>
    </div>
    <div class="hero-logo-box">
        <img src="https://ufmghub.com.br/img/logo-hub.png" alt="UFMG Hub">
    </div>
</div>
""", unsafe_allow_html=True)

# Carrega base histórica das 52 empresas
@st.cache_data(show_spinner=False)
def get_cached_companies():
    return load_companies_data()

companies_list = get_cached_companies()
company_names = sorted([c["nome"] for c in companies_list if c.get("nome")])

# Card de Seleção e Busca
st.markdown("<div class='company-card'>", unsafe_allow_html=True)
st.markdown("<div class='company-card-header'>🔍 Selecionar Empresa para Geração do Dossiê</div>", unsafe_allow_html=True)

tab_busca1, tab_busca2 = st.tabs(["🏢 Escolher da Base da Feira UFMG (52 Mapeadas)", "✍️ Digitar Qualquer Outra Empresa (Nova Prospecção)"])

nome_final = ""

with tab_busca1:
    col_sel, col_btn_clear = st.columns([4, 1])
    with col_sel:
        empresa_selecionada = st.selectbox(
            "Selecione uma empresa cadastrada:",
            options=["-- Selecione uma empresa --"] + company_names,
            index=0,
            label_visibility="collapsed"
        )
    if empresa_selecionada != "-- Selecione uma empresa --":
        nome_final = empresa_selecionada

with tab_busca2:
    empresa_digitada = st.text_input(
        "Digite o nome da empresa desejada:",
        placeholder="Ex: Nubank, Embraer, Ambev, Banco Inter, Totvs, Cargill...",
        label_visibility="collapsed"
    )
    if empresa_digitada.strip():
        nome_final = empresa_digitada.strip()

st.markdown("</div>", unsafe_allow_html=True)

# Exibe card detalhado se uma empresa for selecionada
if nome_final:
    comp_info = find_or_create_company(nome_final, companies_list)
    
    st.markdown("<div class='company-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='company-card-header'>📊 Diagnóstico Histórico: <span style='color: var(--laranja);'>{comp_info['nome']}</span></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Origem do Lead</div>
            <div class="stat-value" style="font-size: 1rem;">{comp_info.get('origem', 'Base UFMG')}</div>
            <span class="badge-cota">{comp_info.get('cota_2026', 'A Prospectar')}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        part_24 = comp_info.get('participou_2024', 'Não')
        badge_24 = "badge-sim" if part_24.lower() == "sim" else "badge-nao"
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Edição 2024</div>
            <div><span class="{badge_24}">{part_24}</span></div>
            <div class="stat-label" style="margin-top: 6px;">Cota: {comp_info.get('cota_2024', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        part_25 = comp_info.get('participou_2025', 'Não')
        badge_25 = "badge-sim" if part_25.lower() == "sim" else "badge-nao"
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Edição 2025</div>
            <div><span class="{badge_25}">{part_25}</span></div>
            <div class="stat-label" style="margin-top: 6px;">Cota: {comp_info.get('cota_2025', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        part_26 = comp_info.get('participou_2026', 'Não')
        badge_26 = "badge-sim" if part_26.lower() == "sim" else "badge-nao"
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Edição 2026</div>
            <div><span class="{badge_26}">{part_26}</span></div>
            <div class="stat-label" style="margin-top: 6px;">Cota: {comp_info.get('cota_2026', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
        
    if comp_info.get("nome_contato") or comp_info.get("email"):
        st.markdown(f"""
        <div style="margin-top: 14px; font-size: 0.88rem; color: #64748b; background: #f1f5f9; padding: 8px 14px; border-radius: 8px;">
            👤 <strong>Contato Registrado:</strong> {comp_info.get('nome_contato', 'Não informado')} &nbsp;|&nbsp; ✉️ {comp_info.get('email', 'Não informado')}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    # Botão de Ação Principal
    col_btn, _ = st.columns([1, 0.01])
    with col_btn:
        btn_gerar = st.button("🚀 Gerar Dossiê Estratégico Completo (3 Páginas em Word)", type="primary", use_container_width=True)
        
    if btn_gerar:
        status_box = st.empty()
        progresso = st.progress(0, text="Iniciando inteligência de mercado...")
        
        try:
            progresso.progress(25, text="🔍 Mapeando produtos, operações em MG, polos e concorrentes via Google Gemini...")
            comp_data = find_or_create_company(nome_final, companies_list)
            
            ai_data = analyze_company(comp_data)
            
            progresso.progress(70, text="📝 Estruturando documento Word com padrão executivo e dados de feiras...")
            output_file = generate_one_page_docx(comp_data, ai_data)
            
            progresso.progress(100, text="✅ Dossiê concluído com sucesso!")
            st.balloons()
            
            with open(output_file, "rb") as f:
                docx_bytes = f.read()
                
            st.markdown(f"""
            <div style="background: #e6f6ed; border: 1px solid #bbf7d0; border-radius: 12px; padding: 20px; text-align: center; margin: 20px 0;">
                <h3 style="color: #0f7642; margin: 0 0 6px 0;">🎉 Dossiê Estratégico de {nome_final} Pronto!</h3>
                <p style="color: #166534; margin: 0;">O documento executivo de 3 páginas foi formatado e está pronto para subsidiar sua reunião.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão de Download Destaque Laranja
            st.download_button(
                label=f"📥 Baixar Dossiê Executivo de {nome_final} (.docx)",
                data=docx_bytes,
                file_name=f"Dossie_Estrategico_{nome_final.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
            
            # Síntese Executiva em Abas
            st.markdown("<br><h4 style='color: var(--azul-escuro);'>📋 Síntese Executiva para a Reunião Comercial:</h4>", unsafe_allow_html=True)
            tab1, tab2, tab3, tab4 = st.tabs([
                "🏢 1.0 Visão Geral & Concorrentes",
                "🏭 2.0 Presença em Minas Gerais & BH",
                "📊 5.0 Feiras Verificadas (Poli USP & PUC)",
                "🎯 7.0 Playbook de Vendas & Objeções"
            ])
            
            with tab1:
                st.markdown(f"<div style='background: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;'>{ai_data.get('resumo_extenso', 'Informação disponível no Word.')}</div>", unsafe_allow_html=True)
                
            with tab2:
                st.markdown(f"<div style='background: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;'>{ai_data.get('atuacao_bh_mg_detalhada', 'Informação disponível no Word.')}</div>", unsafe_allow_html=True)
                
            with tab3:
                feiras_tab = ai_data.get("outras_feiras_tabela", [])
                if feiras_tab:
                    st.table(feiras_tab)
                else:
                    st.info("Sem registro prévio nas feiras da Poli USP e PUC Minas.")
                    
            with tab4:
                st.markdown("**🎯 Ganchos de Abertura:**")
                for g in ai_data.get("guia_reuniao_ganchos", []):
                    st.markdown(f"- {g}")
                    
                st.markdown("**💬 Discurso de Valor B2B (Pitch):**")
                st.markdown(f"<div class='pitch-quote'>{ai_data.get('guia_reuniao_pitch', '')}</div>", unsafe_allow_html=True)
                
                st.markdown("**🛡️ Matriz de Quebra de Objeções:**")
                obj_list = ai_data.get("guia_reuniao_objecoes", [])
                for item in obj_list:
                    with st.expander(f"❌ Objeção: {item.get('objecao', '')}"):
                        st.markdown(f"💡 **Resposta recomendada:** {item.get('resposta', '')}")

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar: {e}")
            progresso.empty()

else:
    st.info("👈 Selecione uma empresa na lista ou digite o nome de qualquer organização acima para iniciar o dossiê.")

# Rodapé Oficial
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.88rem; border-top: 1px solid #e2e8f0; padding-top: 24px;">
    <strong>UFMG Hub &middot; Mercado em Conexão</strong> &middot; Escola de Engenharia da UFMG<br>
    <span style="font-size: 0.8rem; color: #94a3b8;">Unindo a tradição acadêmica da UFMG à inovação prática do mercado corporativo.</span>
</div>
""", unsafe_allow_html=True)
