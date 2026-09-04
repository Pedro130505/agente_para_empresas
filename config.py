import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Arquivos de Entrada
EXCEL_PATH = BASE_DIR / "dados (2).xlsx"
TEMPLATE_DOCX_PATH = BASE_DIR / "Inauguracao_Anual_das_Aulas_de_Engenharia.docx"

# Pasta de Saída para Dossiês Estratégicos (2-3 páginas)
OUTPUT_DIR = BASE_DIR / "output_dossies"
OUTPUT_DIR.mkdir(exist_ok=True)

# Chave API Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Modelo padrão do Gemini (ativo para novas contas Google AI Studio)
GEMINI_MODEL = "gemini-3.6-flash"
