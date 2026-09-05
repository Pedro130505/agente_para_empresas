import argparse
import logging
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

from config import GEMINI_API_KEY, OUTPUT_DIR
from data_loader import load_companies_data, find_or_create_company
from ai_analyzer import analyze_company
from docx_generator import generate_one_page_docx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AgenteDossieEmpresas")

def ensure_api_key():
    """Verifica se a GEMINI_API_KEY está configurada; caso contrário, guia o cadastro no primeiro uso."""
    current_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if current_key and current_key.strip():
        return current_key.strip()
        
    print("\n" + "="*65)
    print(" 🔑 PRIMEIRO USO: CONFIGURAÇÃO DA CHAVE GOOGLE GEMINI")
    print("="*65)
    print(" Para que o agente pesquise QUALQUER empresa em tempo real,")
    print(" é necessária uma chave gratuita do Google AI Studio:")
    print("   1. Acesse: https://aistudio.google.com/app/apikey")
    print("   2. Clique em 'Create API key' com sua conta Google")
    print("   3. Cole o código gerado abaixo (leva 30 segundos):\n")
    
    try:
        user_key = input("👉 Cole sua chave GEMINI_API_KEY aqui: ").strip()
        if user_key:
            env_file = Path(".env")
            env_content = ""
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as f:
                    env_content = f.read()
            
            if "GEMINI_API_KEY=" in env_content:
                lines = [f"GEMINI_API_KEY={user_key}" if line.startswith("GEMINI_API_KEY=") else line for line in env_content.splitlines()]
                new_env = "\n".join(lines)
            else:
                new_env = env_content + f"\nGEMINI_API_KEY={user_key}\n"
                
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(new_env.strip() + "\n")
                
            os.environ["GEMINI_API_KEY"] = user_key
            print("\n✅ Chave salva com sucesso no seu computador!")
            print("🎉 Configuração concluída! Você não precisará digitar novamente.\n")
            return user_key
    except Exception as e:
        logger.warning(f"Não foi possível salvar chave no .env: {e}")
        
    return ""

def generate_single_dossier(company_name, companies_list=None, auto_open_prompt=True):
    """Gera o dossiê estratégico de 3 páginas para uma empresa específica."""
    comp = find_or_create_company(company_name, companies_list)
    nome = comp["nome"]
    
    print(f"\n" + "="*60)
    print(f" 🎯 PROCESSANDO DOSSIÊ ESTRATÉGICO: {nome.upper()}")
    print("="*60)
    
    # Exibe dados históricos se encontrados
    if comp.get("origem") == "Nova Prospecção":
        print(f"ℹ️  Empresa nova (sem histórico registrado nas edições 2024-2026 da Feira UFMG).")
    else:
        print(f"📊 Histórico na Feira UFMG:")
        print(f"   • 2024: {comp['participou_2024']} (Cota: {comp['cota_2024']})")
        print(f"   • 2025: {comp['participou_2025']} (Cota: {comp['cota_2025']})")
        print(f"   • 2026: {comp['participou_2026']} (Cota: {comp['cota_2026']})")
        if comp.get("nome_contato") or comp.get("email"):
            print(f"   • Contato: {comp.get('nome_contato', '')} ({comp.get('email', '')})")

    print("\n🔍 Analisando mercado, concorrentes, polos e dados de feiras...")
    ai_res = analyze_company(comp)
    
    print("📝 Formatando e gerando documento Word (.docx) no padrão executivo...")
    output_file = generate_one_page_docx(comp, ai_res)
    
    print(f"\n✅ DOSSIÊ GERADO COM SUCESSO!")
    print(f"📁 Arquivo: {output_file.resolve()}\n")

    if auto_open_prompt:
        try:
            abrir = input("📂 Deseja abrir o documento Word agora? (s/n, padrão s): ").strip().lower()
            if abrir in ["", "s", "sim", "y", "yes"]:
                if sys.platform.startswith("win"):
                    os.startfile(output_file.resolve())
                elif sys.platform == "darwin":
                    import subprocess
                    subprocess.run(["open", str(output_file.resolve())])
                elif sys.platform.startswith("linux"):
                    import subprocess
                    subprocess.run(["xdg-open", str(output_file.resolve())])
                print("📄 Abrindo o Word...")
        except Exception:
            pass

    return output_file

def run_interactive_mode():
    """Modo interativo onde o usuário digita o nome de qualquer empresa."""
    print("\n" + "="*65)
    print(" 🤖 AGENTE DE INTELIGÊNCIA COMERCIAL — UFMG HUB / FEIRA DE CARREIRAS")
    print("    Geração Sob Demanda de Dossiês Estratégicos (3 Páginas)")
    print("="*65)
    
    ensure_api_key()

    print("Carregando base histórica de empresas...")
    companies_list = load_companies_data()
    print(f"Base carregada: {len(companies_list)} empresas mapeadas na Feira UFMG.\n")

    while True:
        try:
            prompt_input = input("👉 Digite o nome da empresa desejada (ou 'sair' para encerrar): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando o agente. Até logo!")
            break

        if not prompt_input:
            continue
        if prompt_input.lower() in ["sair", "exit", "quit", "q"]:
            print("\nEncerrando o agente comercial. Bons negócios!")
            break

        try:
            generate_single_dossier(prompt_input, companies_list, auto_open_prompt=True)
            print("-" * 65)
        except Exception as e:
            logger.error(f"Erro ao gerar dossiê para '{prompt_input}': {e}", exc_info=True)

def run_batch_all():
    """Gera dossiês em lote para todas as empresas da base."""
    companies = load_companies_data()
    print(f"Iniciando geração em lote para {len(companies)} empresas...")
    for idx, comp in enumerate(companies, 1):
        print(f"\n[{idx}/{len(companies)}] Processando: {comp['nome']}")
        generate_single_dossier(comp["nome"], companies, auto_open_prompt=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente de IA para Geração de Dossiês Estratégicos sob demanda.")
    parser.add_argument("company_pos", nargs="?", default=None, help="Nome da empresa a gerar diretamente.")
    parser.add_argument("--company", type=str, default=None, help="Nome da empresa a gerar.")
    parser.add_argument("--all", action="store_true", help="Gerar para todas as empresas da base em lote.")
    
    args = parser.parse_args()
    target_company = args.company or args.company_pos
    
    if args.all:
        run_batch_all()
    elif target_company:
        companies_list = load_companies_data()
        generate_single_dossier(target_company, companies_list, auto_open_prompt=False)
    else:
        run_interactive_mode()
