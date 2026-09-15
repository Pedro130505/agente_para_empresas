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
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada (UFMG Hub Design)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f4c81;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #0f4c81;
        margin-bottom: 15px;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Barra Lateral: Configurações de IA
st.sidebar.markdown("### ⚙️ Configurações da IA")

env_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
user_key = st.sidebar.text_input(
    "Chave Google Gemini (API Key):",
    value=env_key,
    type="password",
    help="Obtenha gratuitamente em https://aistudio.google.com/app/apikey"
)

if user_key and user_key.strip():
    os.environ["GEMINI_API_KEY"] = user_key.strip()
    st.sidebar.success("🟢 Chave de IA ativa!")
else:
    st.sidebar.warning("⚠️ Chave de IA não informada. Empresas não mapeadas usarão o modelo de contingência.")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 💡 Como obter sua chave gratuita:")
st.sidebar.markdown("""
1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em **'Create API key'**
4. Cole o código no campo acima!
""")

st.sidebar.markdown("---")
st.sidebar.caption("UFMG Hub — Escola de Engenharia da UFMG")

# Área Principal
st.markdown("<p class='main-header'>🎯 Inteligência Comercial & Dossiês de Patrocínio</p>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Feira de Carreiras da Escola de Engenharia da UFMG | Geração Sob Demanda de Dossiês Executivos (3 Páginas)</p>", unsafe_allow_html=True)

# Carrega base histórica das 52 empresas
@st.cache_data(show_spinner=False)
def get_cached_companies():
    return load_companies_data()

companies_list = get_cached_companies()
company_names = sorted([c["nome"] for c in companies_list if c.get("nome")])

col_select, col_custom = st.columns([1.2, 1])

with col_select:
    empresa_selecionada = st.selectbox(
        "🏢 Selecione uma empresa da base UFMG (52 mapeadas):",
        options=["-- Selecione ou digite ao lado --"] + company_names,
        index=0
    )

with col_custom:
    empresa_digitada = st.text_input(
        "✍️ Ou digite o nome de QUALQUER outra empresa:",
        placeholder="Ex: Nubank, Embraer, Ambev, Banco Inter..."
    )

# Define qual empresa será pesquisada
nome_final = ""
if empresa_digitada.strip():
    nome_final = empresa_digitada.strip()
elif empresa_selecionada != "-- Selecione ou digite ao lado --":
    nome_final = empresa_selecionada

# Exibe card de dados se for empresa da base
if nome_final:
    comp_info = find_or_create_company(nome_final, companies_list)
    
    with st.container():
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        col_info1, col_info2, col_info3, col_info4 = st.columns(4)
        
        with col_info1:
            st.markdown(f"**Empresa:** {comp_info['nome']}")
            st.caption(f"Status: {comp_info.get('origem', 'Base UFMG')}")
            
        with col_info2:
            st.markdown(f"**Feira 2024:** {comp_info.get('participou_2024', 'Não')}")
            st.caption(f"Cota: {comp_info.get('cota_2024', 'N/A')}")
            
        with col_info3:
            st.markdown(f"**Feira 2025:** {comp_info.get('participou_2025', 'Não')}")
            st.caption(f"Cota: {comp_info.get('cota_2025', 'N/A')}")
            
        with col_info4:
            st.markdown(f"**Feira 2026:** {comp_info.get('participou_2026', 'Não')}")
            st.caption(f"Cota: {comp_info.get('cota_2026', 'N/A')}")
            
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botão de Ação
    btn_gerar = st.button("🚀 Gerar Dossiê Estratégico Completo (Word .docx)", type="primary", use_container_width=True)
    
    if btn_gerar:
        progresso = st.progress(0, text="Iniciando geração do dossiê...")
        
        try:
            progresso.progress(25, text="🔍 Consultando IA e analisando mercado, concorrentes e polos...")
            comp_data = find_or_create_company(nome_final, companies_list)
            
            ai_data = analyze_company(comp_data)
            
            progresso.progress(70, text="📝 Montando documento Word executivo no padrão institucional...")
            output_file = generate_one_page_docx(comp_data, ai_data)
            
            progresso.progress(100, text="✅ Dossiê concluído!")
            st.balloons()
            
            # Carrega bytes do docx para download
            with open(output_file, "rb") as f:
                docx_bytes = f.read()
                
            st.success(f"🎉 Dossiê Estratégico de **{nome_final}** gerado com sucesso!")
            
            # Botão de Download em Destaque
            st.download_button(
                label=f"📥 Baixar Dossiê de {nome_final} (.docx)",
                data=docx_bytes,
                file_name=f"Dossie_Estrategico_{nome_final.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )
            
            # Visualização Rápida em Abas
            st.markdown("### 📋 Resumo Rápido da Inteligência Gerada:")
            tab1, tab2, tab3, tab4 = st.tabs([
                "1.0 Visão Geral & Concorrentes",
                "2.0 Presença em MG & BH",
                "5.0 Feiras Verificadas (Poli & PUC)",
                "7.0 Playbook de Reunião"
            ])
            
            with tab1:
                st.write(ai_data.get("resumo_extenso", "Informação disponível no Word."))
                
            with tab2:
                st.write(ai_data.get("atuacao_bh_mg_detalhada", "Informação disponível no Word."))
                
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
                    
                st.markdown("**Pitch de Valor (Discurso B2B):**")
                st.info(ai_data.get("guia_reuniao_pitch", ""))
                
                st.markdown("**Quebra de Objeções:**")
                obj_list = ai_data.get("guia_reuniao_objecoes", [])
                for item in obj_list:
                    with st.expander(f"❌ Objeção: {item.get('objecao', '')}"):
                        st.write(f"💡 **Resposta recomendada:** {item.get('resposta', '')}")

        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar o dossiê: {e}")
            progresso.empty()

else:
    st.info("👈 Selecione uma empresa acima ou digite o nome de qualquer organização para iniciar a geração.")

st.markdown("---")
st.caption("Desenvolvido para o time comercial da Feira de Carreiras — UFMG Hub")
