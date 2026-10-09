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

def generate_single_dossier(company_name, companies_list=None, auto_open_prompt=True, tipo_dossie="pre_reuniao"):
    """Gera o dossiê estratégico (Pré-Reunião ou Pós-Reunião) para uma empresa específica."""
    comp = find_or_create_company(company_name, companies_list)
    nome = comp["nome"]
    
    tipo_label = "PÓS-REUNIÃO (PÚBLICO, PIPELINE & INICIATIVAS)" if tipo_dossie == "pos_reuniao" else "PRÉ-REUNIÃO (PROSPECÇÃO COMERCIAL)"
    print(f"\n" + "="*65)
    print(f" 🎯 PROCESSANDO DOSSIÊ {tipo_label}: {nome.upper()}")
    print("="*65)
    
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

    print(f"\n🔍 Analisando mercado, cursos-alvo e inteligência ({tipo_label})...")
    ai_res = analyze_company(comp, tipo_dossie=tipo_dossie)
    
    if tipo_dossie == "pos_reuniao":
        print("📊 Filtrando estatísticas reais da base de estudantes da UFMG...")
        from student_analyzer import analyze_student_base
        student_stats = analyze_student_base(nome)
        print(f"   • Alunos no perfil da empresa: {student_stats.get('total_target')} ({student_stats.get('pct_target')}%)")
        print(f"   • Abertos a propostas: {student_stats.get('total_abertos')} ({student_stats.get('pct_abertos')}%)")
        
        print("📝 Formatando e gerando Dossiê Pós-Reunião em Word (.docx)...")
        from docx_generator import generate_post_meeting_docx
        output_file = generate_post_meeting_docx(comp, ai_res, student_stats)
    else:
        print("📝 Formatando e gerando Dossiê Pré-Reunião em Word (.docx)...")
        output_file = generate_one_page_docx(comp, ai_res)
    
    # Copia automaticamente para a Área de Trabalho (Desktop) para facilidade do usuário
    try:
        import shutil
        desktop_dir = Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Desktop"
        if not desktop_dir.exists():
            desktop_dir = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
        if desktop_dir.exists():
            shutil.copy2(output_file, desktop_dir / output_file.name)
            print(f"🖥️  Cópia enviada para a Área de Trabalho: {desktop_dir / output_file.name}")
    except Exception:
        pass

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
    """Modo interativo onde o usuário digita o nome de qualquer empresa e escolhe o tipo."""
    print("\n" + "="*65)
    print(" 🤖 AGENTE DE INTELIGÊNCIA COMERCIAL — UFMG HUB / FEIRA DE CARREIRAS")
    print("    Geração de Dossiês: Pré-Reunião & Pós-Reunião (Público & Pipeline)")
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
            print("\nEscolha o modelo de dossiê:")
            print("  [1] Dossiê Pré-Reunião (Preparação de Vendas, Mercado e Objeções)")
            print("  [2] Dossiê Pós-Reunião (Público Filtrado, Pipeline, Estágio/Trainee e Iniciativas UFMG)")
            tipo_input = input("👉 Opção (1 ou 2, padrão 1): ").strip()
            tipo_dossie = "pos_reuniao" if tipo_input == "2" else "pre_reuniao"

            generate_single_dossier(prompt_input, companies_list, auto_open_prompt=True, tipo_dossie=tipo_dossie)
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
