import re
from pathlib import Path
import pandas as pd

_CACHED_DF = None

COMPANY_TARGET_COURSES = {
    "weg": [
        "Engenharia Elétrica",
        "Engenharia de Controle e Automação",
        "Engenharia Mecânica",
        "Engenharia de Computação",
        "Engenharia de Produção",
        "Ciência da Computação",
        "Engenharia de Sistemas",
        "Engenharia Química",
        "Engenharia Aeroespacial",
        "Administração"
    ],
    "petronas": [
        "Engenharia Mecânica",
        "Engenharia Elétrica",
        "Engenharia Química",
        "Engenharia de Produção",
        "Engenharia Metalúrgica",
        "Engenharia de Minas",
        "Química",
        "Química Tecnológica",
        "Administração",
        "Ciências Econômicas"
    ],
    "arcelormittal": [
        "Engenharia Metalúrgica",
        "Engenharia Mecânica",
        "Engenharia de Minas",
        "Engenharia Elétrica",
        "Engenharia de Controle e Automação",
        "Engenharia de Produção",
        "Engenharia de Materiais",
        "Ciência da Computação",
        "Administração"
    ],
    "carmeuse": [
        "Engenharia de Minas",
        "Engenharia Química",
        "Engenharia Metalúrgica",
        "Engenharia Mecânica",
        "Engenharia de Produção",
        "Engenharia Ambiental",
        "Química",
        "Química Tecnológica",
        "Administração"
    ],
    "hotmart": [
        "Ciência da Computação",
        "Engenharia de Software",
        "Sistemas de Informação",
        "Ciência de Dados",
        "Engenharia de Computação",
        "Engenharia de Controle e Automação",
        "Engenharia de Produção",
        "Design",
        "Administração"
    ],
    "stellantis": [
        "Engenharia Mecânica",
        "Engenharia de Controle e Automação",
        "Engenharia Elétrica",
        "Engenharia de Produção",
        "Engenharia Aeroespacial",
        "Engenharia de Materiais",
        "Ciência da Computação",
        "Design",
        "Administração"
    ]
}

MACRO_AREAS_COURSES = {
    "⚡ Elétrica, Automação & Robótica": [
        "Engenharia Elétrica",
        "Engenharia de Controle e Automação",
        "Engenharia de Sistemas",
        "Engenharia Eletrônica"
    ],
    "⚙️ Mecânica, Manufatura & Aeroespacial": [
        "Engenharia Mecânica",
        "Engenharia Aeroespacial",
        "Engenharia Mecatrônica"
    ],
    "💻 TI, Computação & Software": [
        "Ciência da Computação",
        "Engenharia de Computação",
        "Sistemas de Informação",
        "Engenharia de Software",
        "Matemática Computacional",
        "Ciência de Dados",
        "Estatística"
    ],
    "🧪 Química, Materiais & Metalurgia": [
        "Engenharia Química",
        "Engenharia Metalúrgica",
        "Engenharia de Materiais",
        "Química Tecnológica",
        "Química"
    ],
    "⛏️ Mineração, Geotecnia & Ambiental": [
        "Engenharia de Minas",
        "Engenharia Ambiental",
        "Geologia",
        "Engenharia Civil"
    ],
    "📈 Gestão, Produção & Negócios": [
        "Engenharia de Produção",
        "Administração",
        "Ciências Econômicas",
        "Controladoria",
        "Ciências Contábeis"
    ],
    "🎨 Design, Comunicação & Marketing": [
        "Design",
        "Comunicação Social",
        "Publicidade e Propaganda",
        "Jornalismo",
        "Relações Públicas"
    ]
}

MACRO_INICIATIVAS_UFMG = [
    "🏎️ Fórmula SAE UFMG (Carro de corrida a combustão, telemetria e powertrain)",
    "⚡ Tesla UFMG (Veículo 100% elétrico de competição, inversores e baterias)",
    "🏁 Baja SAE UFMG (Veículo off-road robusto, tração e resistência mecânica)",
    "🌱 Milhagem UFMG (Veículo de ultraeficiência energética e consumo mínimo)",
    "✈️ AeroDesign / Uai Sô Fly (Aeronaves rádio-controladas e aerodinâmica)",
    "💡 Empresas Juniores da UFMG (CPE Jr., Minas Jr., Otimiza Jr., EMAS Jr., etc.)",
    "🎓 PETs (Programas de Educação Tutorial) (PET Elétrica, Mecânica, Civil, etc.)",
    "🔬 Laboratórios de Pesquisa Aplicada & P&D da Escola de Engenharia",
    "🏛️ Diretórios e Centros Acadêmicos (DA / CAs)"
]

OPCOES_CICLOS_SELETIVOS = [
    "🌸 1º Semestre (Fevereiro a Abril) — Ciclo de Estágio do Meio do Ano",
    "☀️ Meio do Ano (Maio a Junho) — Programas de Férias e Estágio",
    "🍂 2º Semestre (Agosto a Outubro) — Principal Ciclo de Estágio & Trainee (Alinhado à Feira)",
    "❄️ Fim de Ano (Novembro a Dezembro) — Fechamento e Banco de Talentos",
    "🔄 Fluxo Contínuo (Vagas Abertas o Ano Todo)"
]

OPCOES_ATUACAO_UFMG = [
    "❌ Ainda não atuam formalmente (Oportunidade pioneira na Feira)",
    "🎓 Sim: Parcerias com PETs ou Projetos Acadêmicos (ex: PET Elétrica, palestras)",
    "🏢 Sim: Participaram de edições anteriores da Feira de Carreiras",
    "🔬 Sim: Projetos de Pesquisa, P&D ou Laboratórios com professores",
    "🏎️ Sim: Patrocínio de Equipes de Competição ou Empresas Juniores",
    "📢 Sim: Divulgação esporádica de vagas em murais e centros acadêmicos"
]

OPCOES_DURACAO_ESTAGIO = [
    "Não informado / Usar inteligência de mercado (Opcional)",
    "1 a 2 anos (Jornada de 20h ou 30h semanais)",
    "1 ano (Renovável por mais 1 ano)",
    "6 meses a 1 ano",
    "Até 2 anos (Foco em formandos e efetivação)"
]

OPCOES_DURACAO_TRAINEE = [
    "Não informado / Usar inteligência de mercado (Opcional)",
    "Não possui programa de Trainee",
    "12 a 18 meses (Job rotation e imersão)",
    "18 a 24 meses (Desenvolvimento de liderança executiva)",
    "12 meses (1 ano de aceleração)",
    "2 anos ou mais"
]

def courses_from_macro_areas(selected_macro_areas):
    """Retorna lista de cursos correspondentes às macro áreas selecionadas."""
    if not selected_macro_areas:
        return []
    courses = []
    for area in selected_macro_areas:
        if area in MACRO_AREAS_COURSES:
            for c in MACRO_AREAS_COURSES[area]:
                if c not in courses:
                    courses.append(c)
    return courses

def get_default_macro_areas(company_name):
    """Retorna macro áreas padrão recomendadas para a empresa."""
    key = normalize_key(company_name)
    if "weg" in key:
        return [
            "⚡ Elétrica, Automação & Robótica",
            "⚙️ Mecânica, Manufatura & Aeroespacial",
            "💻 TI, Computação & Software",
            "📈 Gestão, Produção & Negócios"
        ]
    elif "petronas" in key:
        return [
            "🧪 Química, Materiais & Metalurgia",
            "⚙️ Mecânica, Manufatura & Aeroespacial",
            "⚡ Elétrica, Automação & Robótica",
            "📈 Gestão, Produção & Negócios"
        ]
    elif "arcelor" in key:
        return [
            "🧪 Química, Materiais & Metalurgia",
            "⚙️ Mecânica, Manufatura & Aeroespacial",
            "⛏️ Mineração, Geotecnia & Ambiental",
            "📈 Gestão, Produção & Negócios"
        ]
    elif "carmeuse" in key:
        return [
            "⛏️ Mineração, Geotecnia & Ambiental",
            "🧪 Química, Materiais & Metalurgia",
            "⚙️ Mecânica, Manufatura & Aeroespacial",
            "📈 Gestão, Produção & Negócios"
        ]
    elif "hotmart" in key:
        return [
            "💻 TI, Computação & Software",
            "📈 Gestão, Produção & Negócios",
            "🎨 Design, Comunicação & Marketing"
        ]
    elif "stellantis" in key or "fiat" in key:
        return [
            "⚙️ Mecânica, Manufatura & Aeroespacial",
            "⚡ Elétrica, Automação & Robótica",
            "📈 Gestão, Produção & Negócios",
            "💻 TI, Computação & Software"
        ]
    return [
        "⚡ Elétrica, Automação & Robótica",
        "⚙️ Mecânica, Manufatura & Aeroespacial",
        "📈 Gestão, Produção & Negócios"
    ]

def get_default_initiatives(company_name):
    """Retorna iniciativas padrão recomendadas para a empresa."""
    key = normalize_key(company_name)
    if "weg" in key:
        return [
            "⚡ Tesla UFMG (Veículo 100% elétrico de competição, inversores e baterias)",
            "🌱 Milhagem UFMG (Veículo de ultraeficiência energética e consumo mínimo)",
            "💡 Empresas Juniores da UFMG (CPE Jr., Minas Jr., Otimiza Jr., EMAS Jr., etc.)",
            "🎓 PETs (Programas de Educação Tutorial) (PET Elétrica, Mecânica, Civil, etc.)"
        ]
    elif "petronas" in key:
        return [
            "🏎️ Fórmula SAE UFMG (Carro de corrida a combustão, telemetria e powertrain)",
            "🏁 Baja SAE UFMG (Veículo off-road robusto, tração e resistência mecânica)",
            "🌱 Milhagem UFMG (Veículo de ultraeficiência energética e consumo mínimo)",
            "💡 Empresas Juniores da UFMG (CPE Jr., Minas Jr., Otimiza Jr., EMAS Jr., etc.)"
        ]
    elif "arcelor" in key:
        return [
            "💡 Empresas Juniores da UFMG (CPE Jr., Minas Jr., Otimiza Jr., EMAS Jr., etc.)",
            "🔬 Laboratórios de Pesquisa Aplicada & P&D da Escola de Engenharia",
            "🏁 Baja SAE UFMG (Veículo off-road robusto, tração e resistência mecânica)",
            "🏎️ Fórmula SAE UFMG (Carro de corrida a combustão, telemetria e powertrain)"
        ]
    elif "carmeuse" in key:
        return [
            "💡 Empresas Juniores da UFMG (CPE Jr., Minas Jr., Otimiza Jr., EMAS Jr., etc.)",
            "🔬 Laboratórios de Pesquisa Aplicada & P&D da Escola de Engenharia",
            "🏁 Baja SAE UFMG (Veículo off-road robusto, tração e resistência mecânica)"
        ]
    elif "hotmart" in key:
        return [
            "💡 Empresas Juniores da UFMG (CPE Jr., Minas Jr., Otimiza Jr., EMAS Jr., etc.)",
            "🎓 PETs (Programas de Educação Tutorial) (PET Elétrica, Mecânica, Civil, etc.)"
        ]
    elif "stellantis" in key or "fiat" in key:
        return [
            "🏎️ Fórmula SAE UFMG (Carro de corrida a combustão, telemetria e powertrain)",
            "⚡ Tesla UFMG (Veículo 100% elétrico de competição, inversores e baterias)",
            "🏁 Baja SAE UFMG (Veículo off-road robusto, tração e resistência mecânica)",
            "🌱 Milhagem UFMG (Veículo de ultraeficiência energética e consumo mínimo)"
        ]
    return [
        "💡 Empresas Juniores da UFMG (CPE Jr., Minas Jr., Otimiza Jr., EMAS Jr., etc.)",
        "🏎️ Fórmula SAE UFMG (Carro de corrida a combustão, telemetria e powertrain)",
        "🎓 PETs (Programas de Educação Tutorial) (PET Elétrica, Mecânica, Civil, etc.)"
    ]

def get_default_ciclos(company_name):
    """Retorna ciclos seletivos padrão recomendados para a empresa."""
    key = normalize_key(company_name)
    if "hotmart" in key:
        return [
            "🔄 Fluxo Contínuo (Vagas Abertas o Ano Todo)",
            "🍂 2º Semestre (Agosto a Outubro) — Principal Ciclo de Estágio & Trainee (Alinhado à Feira)"
        ]
    elif "petronas" in key:
        return [
            "🌸 1º Semestre (Fevereiro a Abril) — Ciclo de Estágio do Meio do Ano",
            "🍂 2º Semestre (Agosto a Outubro) — Principal Ciclo de Estágio & Trainee (Alinhado à Feira)"
        ]
    return [
        "🍂 2º Semestre (Agosto a Outubro) — Principal Ciclo de Estágio & Trainee (Alinhado à Feira)",
        "🌸 1º Semestre (Fevereiro a Abril) — Ciclo de Estágio do Meio do Ano"
    ]

def get_default_atuacao(company_name):
    """Retorna histórico de atuação prévia recomendado para a empresa."""
    key = normalize_key(company_name)
    if "weg" in key:
        return [
            "🎓 Sim: Parcerias com PETs ou Projetos Acadêmicos (ex: PET Elétrica, palestras)",
            "🏢 Sim: Participaram de edições anteriores da Feira de Carreiras"
        ]
    elif "petronas" in key:
        return [
            "🏢 Sim: Participaram de edições anteriores da Feira de Carreiras",
            "🔬 Sim: Projetos de Pesquisa, P&D ou Laboratórios com professores"
        ]
    elif "arcelor" in key:
        return [
            "🏢 Sim: Participaram de edições anteriores da Feira de Carreiras",
            "🔬 Sim: Projetos de Pesquisa, P&D ou Laboratórios com professores"
        ]
    elif "carmeuse" in key:
        return ["❌ Ainda não atuam formalmente (Oportunidade pioneira na Feira)"]
    elif "hotmart" in key or "stellantis" in key:
        return ["🏢 Sim: Participaram de edições anteriores da Feira de Carreiras"]
    return ["❌ Ainda não atuam formalmente (Oportunidade pioneira na Feira)"]


def load_student_database(filepath="base_email_marketing.xlsx"):
    global _CACHED_DF
    if _CACHED_DF is not None:
        return _CACHED_DF
    
    path = Path(filepath)
    if not path.exists():
        return None
    
    try:
        df = pd.read_excel(path, sheet_name="Base")
        _CACHED_DF = df
        return df
    except Exception:
        return None

def normalize_key(name):
    if not name:
        return ""
    text = name.lower().strip()
    text = re.sub(r"[áàãâä]", "a", text)
    text = re.sub(r"[éèêë]", "e", text)
    text = re.sub(r"[íìîï]", "i", text)
    text = re.sub(r"[óòõôö]", "o", text)
    text = re.sub(r"[úùûü]", "u", text)
    text = re.sub(r"[ç]", "c", text)
    text = re.sub(r"[^a-z0-9]", "", text)
    return text

def infer_courses_for_company(company_name, fallback_courses=None):
    if fallback_courses:
        return fallback_courses
        
    key = normalize_key(company_name)
    for c_key, c_courses in COMPANY_TARGET_COURSES.items():
        if c_key in key or key in c_key:
            return c_courses
            
    # Default industrial engineering mix
    return [
        "Engenharia Mecânica",
        "Engenharia Elétrica",
        "Engenharia de Controle e Automação",
        "Engenharia de Produção",
        "Engenharia Química",
        "Ciência da Computação",
        "Administração"
    ]

def analyze_student_base(company_name, custom_courses=None, filepath="base_email_marketing.xlsx"):
    df = load_student_database(filepath)
    target_courses = infer_courses_for_company(company_name, custom_courses)
    
    if df is None or df.empty:
        # Fallback sintético proporcional quando o excel não estiver disponível
        return {
            "has_real_data": False,
            "total_base": 5290,
            "total_target": 1750,
            "pct_target": 33.1,
            "total_abertos": 1380,
            "pct_abertos": 78.9,
            "target_courses": target_courses,
            "cursos_detalhe": [
                {"curso": c, "inscritos": 250, "pct_abertos": 79.0, "relevancia": "Perfil de alta aderência técnica"}
                for c in target_courses[:8]
            ],
            "pipeline_formatura": [
                {"ano": "2025/2026", "alunos": 450, "pct": 25.7, "perfil": "Curtíssimo prazo / Contratação imediata"},
                {"ano": "2027", "alunos": 320, "pct": 18.3, "perfil": "Estágio prioritário (1-2 anos de curso)"},
                {"ano": "2028", "alunos": 390, "pct": 22.3, "perfil": "Trainee / Pipeline de aceleração"},
                {"ano": "2029+", "alunos": 590, "pct": 33.7, "perfil": "Banco de talentos e branding contínuo"}
            ],
            "organizacoes_estudantis": [
                {"organizacao": "Empresas Juniores (CPE, Minas Jr, etc.)", "membros": 240, "pct": 13.7},
                {"organizacao": "Equipes de Competição (Fórmula, Baja, Milhagem)", "membros": 150, "pct": 8.5},
                {"organizacao": "Centros Acadêmicos & Diretórios", "membros": 105, "pct": 6.0},
                {"organizacao": "PETs & Grupos de Pesquisa Acadêmica", "membros": 90, "pct": 5.1}
            ]
        }
    
    total_base = len(df)
    target_mask = df["Curso"].isin(target_courses)
    target_df = df[target_mask]
    total_target = len(target_df)
    
    if total_target == 0:
        target_df = df
        total_target = len(df)
        
    abertos_mask = target_df["Aberto a propostas"].astype(str).str.lower().str.contains("sim", na=False)
    total_abertos = int(abertos_mask.sum())
    pct_abertos = round((total_abertos / total_target * 100), 1) if total_target > 0 else 0.0
    pct_target = round((total_target / total_base * 100), 1) if total_base > 0 else 0.0
    
    # Detalhe por curso
    cursos_detalhe = []
    for c in target_courses:
        c_sub = target_df[target_df["Curso"] == c]
        c_inscritos = len(c_sub)
        if c_inscritos > 0:
            c_abertos = (c_sub["Aberto a propostas"].astype(str).str.lower().str.contains("sim", na=False)).sum()
            c_pct = round((c_abertos / c_inscritos * 100), 1)
            
            # Relevância descritiva automática
            relevancia = "Perfil essencial para a operação técnica e de engenharia"
            if "elétrica" in c.lower() or "automação" in c.lower():
                relevancia = "Perfil central de sistemas elétricos, acionamentos e automação industrial"
            elif "mecânica" in c.lower():
                relevancia = "Engenharia de equipamentos, estruturas, manufatura e termofluidos"
            elif "química" in c.lower():
                relevancia = "Processos químicos, formulação, reações industriais e lubrificantes/reagentes"
            elif "minas" in c.lower() or "metalúrgica" in c.lower():
                relevancia = "Extração mineral, beneficiamento, pirometalurgia e materiais metálicos"
            elif "computação" in c.lower() or "software" in c.lower() or "sistemas" in c.lower():
                relevancia = "TI industrial, inteligência artificial, automação e dados"
            elif "produção" in c.lower():
                relevancia = "Gestão de operações, PCP, logística e melhoria contínua"
            elif "administração" in c.lower() or "econômicas" in c.lower():
                relevancia = "Suprimentos, inteligência comercial, finanças e RH"
                
            cursos_detalhe.append({
                "curso": c,
                "inscritos": c_inscritos,
                "pct_abertos": c_pct,
                "relevancia": relevancia
            })
            
    cursos_detalhe.sort(key=lambda x: x["inscritos"], reverse=True)
    
    # Pipeline por ano de formatura
    pipeline_formatura = []
    ano_col = "Ano de conclusão"
    if ano_col in target_df.columns:
        counts = target_df[ano_col].value_counts()
        
        # Agrupamentos
        imediato = sum(counts.get(y, 0) for y in [2024, 2025, 2026, "2024", "2025", "2026"])
        estagio_2027 = counts.get(2027, counts.get("2027", 0))
        trainee_2028 = counts.get(2028, counts.get("2028", 0))
        futuro_2029 = sum(counts.get(y, 0) for y in [2029, 2030, 2031, 2032, "2029", "2030", "2031", "2032"])
        
        pipeline_formatura = [
            {
                "ano": "2025 / 2026",
                "alunos": int(imediato),
                "pct": round(imediato / total_target * 100, 1) if total_target else 0,
                "perfil": "Curtíssimo prazo / Contratação Imediata & Efetivação"
            },
            {
                "ano": "2027",
                "alunos": int(estagio_2027),
                "pct": round(estagio_2027 / total_target * 100, 1) if total_target else 0,
                "perfil": "Estágio Prioritário (Ciclo de 1 a 2 anos)"
            },
            {
                "ano": "2028",
                "alunos": int(trainee_2028),
                "pct": round(trainee_2028 / total_target * 100, 1) if total_target else 0,
                "perfil": "Estágio Longo & Pipeline de Trainee Corporativo"
            },
            {
                "ano": "2029 em diante",
                "alunos": int(futuro_2029),
                "pct": round(futuro_2029 / total_target * 100, 1) if total_target else 0,
                "perfil": "Banco de Talentos Futuro & Marca Empregadora Contínua"
            }
        ]
        
    organizacoes_estudantis = [
        {"organizacao": "Empresas Juniores da UFMG (CPE, Minas Jr, Otimiza, etc.)", "membros": int(round(total_target * 0.134)), "pct": 13.4},
        {"organizacao": "Equipes de Competição (Fórmula SAE, Baja, Milhagem, Aero)", "membros": int(round(total_target * 0.082)), "pct": 8.2},
        {"organizacao": "Centros Acadêmicos & Diretórios Acadêmicos", "membros": int(round(total_target * 0.058)), "pct": 5.8},
        {"organizacao": "PETs (Programa de Educação Tutorial) & Iniciação Científica", "membros": int(round(total_target * 0.051)), "pct": 5.1}
    ]
    
    return {
        "has_real_data": True,
        "total_base": total_base,
        "total_target": total_target,
        "pct_target": pct_target,
        "total_abertos": total_abertos,
        "pct_abertos": pct_abertos,
        "target_courses": target_courses,
        "cursos_detalhe": cursos_detalhe,
        "pipeline_formatura": pipeline_formatura,
        "organizacoes_estudantis": organizacoes_estudantis
    }
