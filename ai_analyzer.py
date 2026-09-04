import os
import json
import logging
from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

PROMPT_TEMPLATE = """Você é um Analista Sênior de Inteligência de Mercado e Prospecção B2B do UFMG Hub (Escola de Engenharia da UFMG).

Sua missão é criar um **DOSSIÊ ESTRATÉGICO DE ALTA PRECISÃO FACTUAL** sobre a empresa **"{nome_empresa}"** para munir a equipe comercial em reuniões de venda de patrocínio para a Feira de Carreiras da UFMG.

REGRAS ABSOLUTAS DE QUALIDADE:
- Toda informação DEVE ser factual e verificável. NÃO invente dados.
- Se não souber algo com certeza, escreva "Não foi possível confirmar".
- Pesquise no site oficial da empresa, no LinkedIn, em portais de emprego e em notícias recentes.

Contexto da Empresa na Feira UFMG:
- Histórico 2024: {participou_2024} (Cota: {cota_2024})
- Histórico 2025: {participou_2025} (Cota: {cota_2025})
- Histórico 2026: {participou_2026} (Cota: {cota_2026})
- Contato Cadastrado: {nome_contato} | E-mail: {email}

Retorne ESTRITAMENTE um JSON válido com a seguinte estrutura:

{{
  "resumo_extenso": "FORMATO OBRIGATÓRIO - Texto denso, executivo e sucinto (sem prolixidade, mas citando todos os pontos obrigatórios):\n\nA [nome_empresa] atua no setor de [ramo], com foco principal em [core business]. Trabalha diretamente com [lista de produtos/serviços específicos]. No Brasil, [escala nacional, liderança de mercado, capacidade e dados econômicos/porte]. Em Minas Gerais, [operações no estado e sede se houver].\n\nSeus principais concorrentes diretos no país são: [Concorrente 1], [Concorrente 2] e [Concorrente 3]. A [nome_empresa] se destaca frente aos rivais por [diferenciais competitivos concretos: escala, tecnologia, certificações, infraestrutura].\n\nEm feiras universitárias, concorrentes diretos como [Concorrente X] e [Concorrente Y] disputam ativamente talentos em [feiras que participam]. Isso exige posicionamento estratégico da [nome_empresa] na UFMG para garantir atração e retenção nos cursos de [cursos-alvo da empresa].",
  "atuacao_bh_mg_detalhada": "ESTRUTURA OBRIGATÓRIA EM 3 PARTES:\n\nA) POLOS NACIONAIS (FORA DE MG):\n- Citar as principais fábricas, usinas ou polos operacionais da empresa em outros estados do Brasil (cidade e estado).\n\nB) PRESENÇA EM MINAS GERAIS: SIM ou NÃO\n- Listar os polos industriais e operacionais principais no estado de MG e suas cidades.\n\nC) PRESENÇA EM BELO HORIZONTE: SIM ou NÃO\n- Confirmar se possui sede corporativa, escritório administrativo ou centro tecnológico/inovação em Belo Horizonte (bairro/localização).",
  "historico_relacionamento_analise": "Análise do histórico de patrocínio 2024-2026 e diagnóstico de estratégia de upsell.",
  "programas_estagio_trainee_completo": "SEÇÃO OBRIGATÓRIA EM DUAS PARTES:\n\nA) PROGRAMAS NACIONAIS:\n- Nome do programa de Estágio: Cursos-alvo e cidades de atuação.\n- Nome do programa de Trainee (se existir): Cursos-alvo e cidades de atuação.\n\nB) PROGRAMAS EM BH / MINAS GERAIS:\n- Contrata estagiários em MG? SIM/NÃO. Quais unidades e quais cursos?\n- Contrata trainees em MG? SIM/NÃO. Quais unidades e quais cursos?",
  "outras_feiras_tabela": [
    {{"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Sim ou Não", "status_2026": "Sim ou Não", "detalhes": "Participação concreta na feira da Poli USP."}},
    {{"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Sim ou Não", "status_2026": "Sim ou Não", "detalhes": "Participação concreta e cota de patrocínio na PUC Minas."}}
  ],
  "posicionamento_esg_inovacao": "FORMATO OBRIGATÓRIO: Concatene os principais feitos em exatamente 3 pilares estratégicos coesos (em vez de vários tópicos soltos):\n1. [Pilar 1: Descarbonização, Transição Energética e Ecoeficiência]\n2. [Pilar 2: Inovação Aberta, Tecnologia e Parcerias Acadêmicas]\n3. [Pilar 3: Impacto Social, Comunidades e Governança/Diversidade]",
  "guia_reuniao_ganchos": [
    "Gancho 1 de abertura específico para esta empresa.",
    "Gancho 2 conectado às operações em MG.",
    "Gancho 3 conectado à competição com concorrentes em feiras."
  ],
  "guia_reuniao_pitch": "Discurso de valor B2B de 2 parágrafos customizado para a empresa.",
  "guia_reuniao_objecoes": [
    {{"objecao": "Objeção real 1", "resposta": "Resposta tática com dados."}},
    {{"objecao": "Objeção real 2", "resposta": "Resposta tática com dados."}},
    {{"objecao": "Objeção real 3", "resposta": "Resposta tática com dados."}},
    {{"objecao": "Objeção real 4", "resposta": "Resposta tática com dados."}}
  ]
}}
"""

# ==============================================================================
# BASE DE CONHECIMENTO PRÉ-PESQUISADA PARA EMPRESAS CONHECIDAS
# Fallback de alta qualidade quando a API do Gemini não está disponível.
# ==============================================================================

KNOWLEDGE_BASE = {
    "stellantis": {
        "resumo_extenso": (
            "A Stellantis atua no ramo automotivo, com foco principal na fabricação de veículos de passeio, "
            "comerciais leves, picapes e SUVs. A empresa trabalha diretamente com as marcas Fiat, Jeep, Ram, "
            "Peugeot e Citroën no Brasil — cobrindo desde veículos populares (Fiat Mobi, Argo) até picapes "
            "premium (Ram Rampage) e SUVs médios (Jeep Compass, Commander).\n\n"
            "No Brasil, seu foco principal é a liderança absoluta de mercado: a Stellantis encerrou 2025 com "
            "29,3% de market share (mais de 750 mil veículos vendidos), sendo a marca Fiat sozinha responsável "
            "por ~20% do mercado nacional. A Fiat Strada é o veículo mais vendido do Brasil há anos consecutivos "
            "e o grupo controla mais de 50% do mercado de picapes ao somar Strada, Toro, Rampage e Ram.\n\n"
            "Em Minas Gerais, a empresa concentra seu maior ativo industrial: o Polo Automotivo de Betim, "
            "a maior fábrica de automóveis e motores da América Latina com 2,2 milhões de m², capacidade de "
            "650 mil veículos/ano e 1,1 milhão de motores/ano, empregando entre 16 e 19 mil colaboradores diretos.\n\n"
            "Seus principais concorrentes diretos no Brasil são: Volkswagen (compete com Polo, T-Cross, Saveiro "
            "e Amarok), General Motors/Chevrolet (compete com Onix, Tracker e Montana) e Toyota (compete com "
            "Corolla Cross e Hilux). A Stellantis se destaca porque possui a maior capacidade fabril instalada "
            "da América Latina, liderança isolada de market share há 3+ anos consecutivos e anunciou um ciclo "
            "de R$ 32 bilhões de investimento até 2030 (R$ 14 bilhões só em Betim).\n\n"
            "Em relação à presença dos concorrentes em feiras universitárias: a Volkswagen e a GM/Chevrolet "
            "participam ativamente do Workshop Integrativo (Poli USP) e de feiras como PUC Carreiras e UFRJ. "
            "A Toyota investe em ativações digitais e no programa Toyota Way para universidades. "
            "A Hyundai participa de feiras em SP e PR. Isso reforça que a UFMG Hub deve posicionar a Stellantis "
            "como a empresa com maior presença industrial em MG e maior necessidade de recrutar talentos locais."
        ),
        "atuacao_bh_mg_detalhada": (
            "A) POLOS NACIONAIS (FORA DE MG):\n"
            "• Polo Automotivo de Goiana (Goiana - PE): Complexo 4.0 neutro em carbono, produz Jeep (Renegade, Compass, Commander), Fiat Toro e Ram Rampage.\n"
            "• Polo Automotivo de Porto Real (Porto Real - RJ): Plataforma CMP, produz Citroën (C3, Basalt, Aircross) e futuro Jeep Avenger.\n"
            "• Sede Comercial & Marketing: São Paulo (SP).\n\n"
            "B) PRESENÇA EM MINAS GERAIS: SIM\n"
            "• Polo Automotivo de Betim (Betim - MG): Maior complexo fabril da América Latina (2,2 milhões m², 650 mil veículos/ano e 1,1 milhão de motores/ano). Fabrica Fiat Strada, Mobi, Argo, Pulse, Fastback e Fiorino. Emprega 16 a 19 mil colaboradores diretos.\n"
            "• Centro de Engenharia e P&D (Betim - MG): +3.000 engenheiros em ~60 laboratórios avançados (Safety Center, Design Center e Virtual Center).\n"
            "• Teksid do Brasil (Betim e Itaúna - MG): Fundição de ferro e alumínio para blocos de motor e cabeçotes.\n\n"
            "C) PRESENÇA EM BELO HORIZONTE: SIM\n"
            "• Escritórios Corporativos e Administrativos em Nova Lima / Região Metropolitana de BH (gestão corporativa, finanças e tecnologia de negócios)."
        ),
        "programas_estagio_trainee_completo": (
            "A) PROGRAMAS NACIONAIS:\n\n"
            "• Programa de Estágio Stellantis 2026 (estagiostellantis2026.com.br):\n"
            "  - Cursos-alvo: Engenharia (Mecânica, Elétrica, Produção, Software, Mecatrônica), Tecnologia "
            "(Ciência da Computação, Sistemas, Análise de Dados), Negócios (Administração, Economia, Finanças) "
            "e Design/Comunicação.\n"
            "  - Cidades: Betim (MG), Nova Lima/BH (MG), Itaúna (MG), Goiana (PE), Recife (PE), Porto Real (RJ) "
            "e São Paulo (SP).\n\n"
            "• GPS - Graduate Program of Stellantis (Trainee Corporativo 2026):\n"
            "  - Cursos-alvo: Engenharias, Administração, Economia, Finanças, Marketing, RH, Ciência da Computação.\n"
            "  - Cidades: Betim (MG), Nova Lima/BH (MG), Goiana (PE), São Paulo (SP).\n\n"
            "• Trainee de Engenharia 2026:\n"
            "  - Cursos-alvo: Engenharia Mecânica, Elétrica, Produção, Mecatrônica e Manufatura.\n"
            "  - Cidades: Betim (MG), Goiana (PE), Porto Real (RJ).\n\n"
            "B) PROGRAMAS EM BH / MINAS GERAIS:\n\n"
            "• Contrata estagiários em MG? SIM. Unidades: Betim, Nova Lima/BH e Itaúna. "
            "Cursos: Engenharia (Mecânica, Elétrica, Produção, Software), Administração, Finanças.\n"
            "• Contrata trainees em MG? SIM. Unidades: Betim e Nova Lima/BH. "
            "Cursos: Engenharias e áreas corporativas."
        ),
        "outras_feiras_tabela": [
            {"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Sim", "status_2026": "Sim",
             "detalhes": "Participante assídua com estande institucional para atração de talentos de engenharia e tecnologia."},
            {"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Sim", "status_2026": "Sim",
             "detalhes": "Patrocínio Ouro em 2025 e 2026. Parceria histórica que inclui o SimCenter (simulador de dinâmica veicular no Campus Coração Eucarístico)."}
        ],
        "posicionamento_esg_inovacao": (
            "1. Descarbonização & Tecnologia Bio-Hybrid:\n"
            "Desenvolvimento e produção de plataformas híbridas flex (MHEV 12V, HEV 48V, PHEV e 100% elétricos) "
            "combinando motores flex com eletrificação. Alavanca a matriz renovável de etanol brasileira rumo à meta "
            "Net Zero até 2038 do plano estratégico global Dare Forward 2030.\n\n"
            "2. Ecoeficiência Operacional & Aterro Zero:\n"
            "Polo Automotivo de Goiana (PE) certificado como o primeiro complexo multiplantas neutro em carbono da América Latina. "
            "Polo Automotivo de Betim (MG) com operação 100% Aterro Zero (reaproveitamento integral de resíduos industriais) e "
            "parques solares para autogeração de energia limpa.\n\n"
            "3. Inovação Acadêmica & Impacto Comunitário:\n"
            "Parceria tecnológica de ponta com a PUC Minas no SimCenter e projetos de formação com o SENAI. Em Betim (MG), "
            "atuação social contínua com o Programa Árvore da Vida (+25 mil atendidos no Jardim Teresópolis) e cooperativa "
            "social Cooperárvore, transformando resíduos automotivos em geração de renda."
        ),
        "guia_reuniao_ganchos": [
            "1. 'Com a comemoração dos 50 anos do Polo de Betim em 2026, este é o momento ideal para a "
            "Stellantis reforçar seu compromisso com os talentos de engenharia da UFMG — a principal "
            "universidade do estado onde está sua maior fábrica.'",
            "2. 'Sabemos que a Stellantis já é patrocinadora ativa na PUC Carreiras. A Escola de Engenharia "
            "da UFMG oferece um perfil complementar e mais técnico: engenheiros de manufatura, mecatrônica "
            "e software que são os perfis mais demandados pelo P&D de Betim.'",
            "3. 'Com o ciclo de R$ 14 bilhões de investimento em Betim até 2030, qual é o perfil de engenheiro "
            "mais crítico de recrutar hoje para sustentar essa expansão?'"
        ],
        "guia_reuniao_pitch": (
            "\"A Stellantis é a maior empregadora industrial de Minas Gerais e opera o maior complexo "
            "automotivo da América Latina a menos de 30km do campus da UFMG. Com mais de 3.000 engenheiros "
            "no centro de P&D de Betim e o maior ciclo de investimentos da história (R$ 14 bilhões até 2030), "
            "a demanda por talentos de engenharia mecânica, elétrica, software e produção nunca foi tão alta.\n\n"
            "Ao garantir a cota na Feira de Carreiras da UFMG, a Stellantis conecta sua marca empregadora "
            "diretamente com os formandos de maior densidade técnica do estado — complementando a presença "
            "já consolidada na PUC Carreiras com o perfil mais técnico e industrial que só a Escola de "
            "Engenharia da UFMG oferece.\""
        ),
        "guia_reuniao_objecoes": [
            {
                "objecao": "Já somos patrocinadores Ouro da PUC Carreiras.",
                "resposta": "A PUC Minas oferece excelente cobertura em negócios e gestão. A UFMG complementa "
                "com o perfil técnico-industrial que o P&D de Betim mais demanda: engenheiros de manufatura, "
                "mecatrônica, elétrica e software. Não são públicos concorrentes, são complementares."
            },
            {
                "objecao": "Restrição orçamentária no ciclo de investimentos 2025-2030.",
                "resposta": "Justamente por investir R$ 14 bilhões em Betim, a demanda por engenheiros vai "
                "crescer exponencialmente. Recrutar direto no campus da UFMG reduz o CAC de RH comparado a "
                "consultorias de seleção e garante acesso prioritário aos talentos antes dos concorrentes."
            },
            {
                "objecao": "Participamos do Workshop Integrativo (Poli USP), que já cobre engenharia.",
                "resposta": "O WI cobre talentos em SP. Para as operações de Betim (16-19 mil colaboradores), "
                "é essencial recrutar na UFMG — alunos locais têm menor barreira de relocação e já conhecem "
                "o ecossistema industrial da RMBH."
            },
            {
                "objecao": "Recrutamos via LinkedIn e plataformas digitais.",
                "resposta": "A presença presencial no campus gera experiência de marca imbatível. Concorrentes "
                "como VW e GM já investem em feiras universitárias para disputar os mesmos talentos de engenharia. "
                "Estar ausente na UFMG abre espaço direto para esses competidores."
            }
        ]
    },
    "arcelormittal": {
        "resumo_extenso": (
            "A ArcelorMittal atua no setor siderúrgico e de mineração, liderando a produção de aços longos "
            "(vergalhões CA-50/60, barras, perfis, fio-máquina, arames Belgo, fibras Dramix® e steel cord), "
            "aços planos (bobinas laminadas a quente/frio, revestimento Magnelis®) e extração de minério de ferro. "
            "É a maior siderúrgica da América Latina, respondendo por ~45-50% do aço bruto nacional "
            "(15,3 Mt/ano de capacidade instalada, R$ 66,6 bi de receita em 2024 e mais de 20.000 empregados). "
            "Em Minas Gerais, concentra sua principal malha operacional integrada e a sede corporativa nacional.\n\n"
            "Seus principais concorrentes diretos no país são Gerdau (líder rival em aços longos, com usina em Ouro Branco/MG), "
            "Usiminas (aços planos, Ipatinga/MG), CSN (planos e mineração, Volta Redonda/Congonhas), Ternium (placas no RJ) "
            "e Vallourec (tubos sem costura em BH/Jeceaba). A ArcelorMittal se destaca pela escala (15,5 Mt/ano de capacidade), "
            "verticalização total da mina ao varejo, cadeia de BioFlorestas (carvão vegetal renovável certificado FSC) e o pioneiro hub Açolab em BH.\n\n"
            "No ecossistema universitário, concorrentes como Gerdau (Workshop Integrativo Poli USP, UFMG, UFOP), Usiminas "
            "(UNIFEI, UFOP) e Vallourec (UFMG, CEFET-MG) disputam ativamente os formandos. Isso exige presença estratégica "
            "da ArcelorMittal na UFMG para reter os melhores talentos de engenharia metalúrgica, mecânica e de minas."
        ),
        "atuacao_bh_mg_detalhada": (
            "A) POLOS NACIONAIS (FORA DE MG):\n"
            "• Tubarão (Serra - ES): Usina integrada de grande porte para aços planos (placas e bobinas).\n"
            "• Pecém (São Gonçalo do Amarante - CE): Usina siderúrgica de placas de alto padrão (3 Mt/ano).\n"
            "• Vega (São Francisco do Sul - SC): Centro avançado de laminação a frio, decapagem e galvanização.\n"
            "• Barra Mansa e Resende (RJ): Unidades industriais produtoras de aços longos e perfis.\n"
            "• Piracicaba (SP): Laminação de aços longos.\n\n"
            "B) PRESENÇA EM MINAS GERAIS: SIM\n"
            "• Usina de João Monlevade (João Monlevade - MG): Usina integrada de fio-máquina automotivo (1,2 Mt/ano, em duplicação para 2,2 Mt/ano).\n"
            "• Usina de Juiz de Fora (Juiz de Fora - MG): Mini-mill de vergalhões CA-50/60 e barras (+1 Mt/ano).\n"
            "• Belgo Arames (Sabará, Itaúna e Contagem - MG): Fábricas de arames industriais, fibras Dramix® e steel cord.\n"
            "• Mineração Serra Azul (Itatiaiuçu - MG): Pellet feed (4,5 Mt/ano), operação sem barragem (100% filtragem a seco).\n"
            "• Mina do Andrade (Bela Vista de Minas - MG): Sinter feed para a usina de Monlevade (3,5 Mt/ano).\n"
            "• BioFlorestas: Silvicultura de eucalipto para biorredutor no interior de MG (Dionísio, Bom Despacho, etc.).\n\n"
            "C) PRESENÇA EM BELO HORIZONTE: SIM\n"
            "• Sede Corporativa Nacional e LATAM (Av. Carandaí, 1115, Funcionários / Savassi): Presidência, diretorias executivas e fundação.\n"
            "• Açolab (Av. Carandaí, 1115, 5º andar): Primeiro hub de inovação aberta do setor do aço no mundo.\n"
            "• Centros Corporativos: ArcelorMittal Sistemas (TI corporativo Américas) e Centro de Serviços Compartilhados (CSC)."
        ),
        "programas_estagio_trainee_completo": (
            "A) PROGRAMAS NACIONAIS:\n\n"
            "• Programa de Estágio ArcelorMittal (aberturas semestrais):\n"
            "  - Cursos-alvo: Engenharia (Metalúrgica, Mecânica, Elétrica, Automação, Produção, Materiais, "
            "Minas, Química, Civil, Ambiental, Computação), Tecnologia (Ciência da Computação, Sistemas, ADS, "
            "Estatística), Gestão (Administração, Economia, Contábeis, RH, Comunicação, Direito, Logística).\n"
            "  - Cidades: BH (MG), João Monlevade (MG), Juiz de Fora (MG), Sabará (MG), Itaúna (MG), "
            "Contagem (MG), Itatiaiuçu (MG), Serra (ES), São Gonçalo do Amarante (CE), Piracicaba (SP), "
            "Barra Mansa (RJ), São Francisco do Sul (SC).\n\n"
            "• Programa Trainee / Jovens Profissionais:\n"
            "  - Cursos-alvo: Engenharias, Tecnologia e Finanças/Gestão.\n"
            "  - Cidades: BH (MG), João Monlevade (MG), Juiz de Fora (MG), Serra (ES), Piracicaba (SP).\n\n"
            "B) PROGRAMAS EM BH / MINAS GERAIS:\n\n"
            "• Contrata estagiários em MG? SIM. Unidades: BH (sede, TI, CSC, Açolab), João Monlevade, "
            "Juiz de Fora, Sabará, Itaúna, Contagem, Itatiaiuçu e Bela Vista de Minas. "
            "Cursos: Engenharias (Metalúrgica, Mecânica, Elétrica, Minas, Produção), Computação, Administração.\n"
            "• Contrata trainees em MG? SIM. Unidades: BH e João Monlevade. "
            "Cursos: Engenharias, Tecnologia e Gestão."
        ),
        "outras_feiras_tabela": [
            {"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Não", "status_2026": "Não",
             "detalhes": "Sem participação confirmada nas edições recentes da feira da USP."},
            {"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Não", "status_2026": "Sim",
             "detalhes": "Participou na edição 2026 com Patrocínio Prata através da Belgo Arames (joint venture do grupo sediada em Contagem e Sabará)."}
        ],
        "posicionamento_esg_inovacao": (
            "1. Descarbonização & Ecoeficiência (Siderurgia Verde):\n"
            "Usinas de João Monlevade, Juiz de Fora e Sabará certificadas com o padrão internacional "
            "ResponsibleSteel™. Meta de Net Zero até 2050 (-25% até 2030), impulsionada pelo portfólio XCarb® de "
            "aço ecoeficiente, pela cadeia de BioFlorestas (carvão vegetal renovável certificado FSC em substituição "
            "ao carvão mineral) e pela parceria no Centro CIT/SENAI de Descarbonização Industrial em BH.\n\n"
            "2. Segurança Operacional & Mineração Sustentável:\n"
            "Eliminação total de barragens na Mineração Serra Azul (Itatiaiuçu/MG), com R$ 2,5 bilhões investidos na "
            "transição para 100% de filtragem e empilhamento a seco de rejeitos, além de taxa de recirculação de água "
            "superior a 98% em todas as operações industriais de Minas Gerais.\n\n"
            "3. Inovação Aberta & Impacto Social:\n"
            "Pioneirismo global com o Açolab em Belo Horizonte (Av. Carandaí), conectando startups e universidades a "
            "desafios do aço. Investimento contínuo via Fundação ArcelorMittal (+35 anos em MG) e meta de atingir "
            "25% de mulheres em cargos de liderança até 2030 com programas afirmativos com o SENAI/MG."
        ),
        "guia_reuniao_ganchos": [
            "1. 'Com a sede corporativa nacional na Av. Carandaí em BH e o Açolab operando no mesmo "
            "endereço, a ArcelorMittal é talvez a empresa mais conectada ao ecossistema de inovação "
            "mineiro — e a UFMG é a principal fonte de engenheiros metalúrgicos e de minas do estado.'",
            "2. 'Sabemos que a expansão de Serra Azul em Itatiaiuçu e a duplicação de Monlevade estão "
            "gerando demanda por centenas de novos engenheiros em MG. A feira da UFMG é o canal direto "
            "para esses talentos.'",
            "3. 'Concorrentes diretos como Gerdau e Vallourec já investem em presença nas feiras da UFMG. "
            "Manter a ArcelorMittal visível no campus é estratégico para não perder talentos de engenharia "
            "metalúrgica e de minas para esses competidores.'"
        ],
        "guia_reuniao_pitch": (
            "\"A ArcelorMittal é a maior empregadora do setor siderúrgico de Minas Gerais, com mais de "
            "10 unidades operacionais no estado — de usinas integradas em Monlevade e Juiz de Fora a minas "
            "em Itatiaiuçu e Bela Vista, passando pela sede corporativa e o Açolab em BH. Com a expansão "
            "de Serra Azul (R$ 2,5 bi) e a duplicação de Monlevade, a demanda por engenheiros metalúrgicos, "
            "mecânicos, de minas e de automação nunca foi tão alta.\n\n"
            "Ao garantir a cota na Feira de Carreiras da UFMG, a ArcelorMittal acessa diretamente os "
            "formandos da Escola de Engenharia com nota máxima no ENADE — o mesmo campus que forma os "
            "engenheiros metalúrgicos e de minas mais disputados do Brasil. É recrutamento de alta precisão "
            "a poucos quilômetros da sede.\""
        ),
        "guia_reuniao_objecoes": [
            {
                "objecao": "Já participamos da PUC Carreiras e do Workshop Integrativo.",
                "resposta": "Excelente cobertura em SP e na PUC. Mas a Escola de Engenharia da UFMG é o "
                "principal polo de formação de engenheiros metalúrgicos e de minas do Brasil — perfis "
                "essenciais para as usinas de Monlevade e Juiz de Fora e as minas de Itatiaiuçu. "
                "São públicos complementares."
            },
            {
                "objecao": "Momento de contenção orçamentária após o resultado de 2025.",
                "resposta": "Justamente com as expansões de Serra Azul (R$ 2,5 bi) e Monlevade em andamento, "
                "o pipeline de contratação técnica precisa ser garantido agora. Recrutar direto na UFMG "
                "reduz o custo por contratação vs. consultorias externas."
            },
            {
                "objecao": "Recrutamos via plataforma Oracle Cloud e LinkedIn.",
                "resposta": "Plataformas digitais são essenciais, mas a presença no campus gera experiência "
                "de marca. Concorrentes como Gerdau e Vallourec investem em feiras universitárias em MG "
                "para disputar os mesmos perfis de engenharia. A ausência da ArcelorMittal na UFMG abre "
                "espaço direto para eles."
            },
            {
                "objecao": "Temos parceria forte com UFOP (Escola de Minas) e UFJF.",
                "resposta": "UFOP e UFJF são excelentes para as operações de Monlevade e Juiz de Fora. "
                "Mas a sede corporativa, o CSC, o Açolab e a ArcelorMittal Sistemas estão em BH — e "
                "esses centros demandam talentos de computação, automação e gestão que a UFMG forma "
                "em volume e qualidade superiores."
            }
        ]
    }
}


def get_verified_fairs_data(company_name):
    """Consulta a planilha oficial de feiras (feiras_participantes.xlsx) para assertividade absoluta."""
    from pathlib import Path
    excel_path = Path("feiras_participantes.xlsx")
    if excel_path.exists():
        try:
            import pandas as pd
            from data_loader import normalize_key
            df = pd.read_excel(excel_path, sheet_name="Consolidado_52_Empresas")
            target_key = normalize_key(company_name)
            
            match_row = None
            for _, r in df.iterrows():
                r_key = normalize_key(str(r["Empresa"]))
                if r_key == target_key or target_key in r_key or r_key in target_key:
                    match_row = r
                    break
            
            if match_row is not None:
                return [
                    {
                        "feira": "Workshop Integrativo (WI - Poli USP)",
                        "status_2025": str(match_row["WI_2025"]),
                        "status_2026": str(match_row["WI_2026"]),
                        "detalhes": str(match_row["WI_Detalhes"])
                    },
                    {
                        "feira": "PUC Carreiras (PUC Minas)",
                        "status_2025": str(match_row["PUC_2025"]),
                        "status_2026": str(match_row["PUC_2026"]),
                        "detalhes": str(match_row["PUC_Detalhes"])
                    }
                ]
        except Exception as e:
            logger.warning(f"Erro ao consultar feiras_participantes.xlsx para {company_name}: {e}")

    return [
        {"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Não", "status_2026": "Não", "detalhes": "Sem participação confirmada nas edições recentes."},
        {"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Não", "status_2026": "Não", "detalhes": "Sem patrocínio confirmado nas edições recentes."}
    ]


def generate_fallback_analysis(company_data):
    nome = company_data["nome"]
    p24, c24 = company_data.get("participou_2024", "Não"), company_data.get("cota_2024", "N/A")
    p25, c25 = company_data.get("participou_2025", "Não"), company_data.get("cota_2025", "N/A")
    p26, c26 = company_data.get("participou_2026", "Não"), company_data.get("cota_2026", "N/A")

    # Verificar se temos dados pré-pesquisados para a empresa
    key = nome.lower().strip()
    if key in KNOWLEDGE_BASE:
        result = dict(KNOWLEDGE_BASE[key])
        result["historico_relacionamento_analise"] = (
            f"Histórico Consolidado na Feira UFMG:\n"
            f"- 2024: Participação {p24} (Cota {c24})\n"
            f"- 2025: Participação {p25} (Cota {c25})\n"
            f"- 2026: Participação {p26} (Cota {c26})\n\n"
            f"Diagnóstico: A {nome} possui um padrão de investimento recorrente. "
            f"A estratégia comercial é apresentar dados de engajamento dos alunos com a marca "
            f"e propor evolução de cota baseada no ROI de contratações diretas no campus."
        )
        result["outras_feiras_tabela"] = get_verified_fairs_data(nome)
        return result

    # Fallback genérico para empresas sem base de conhecimento pré-pesquisada
    return {
        "resumo_extenso": (
            f"A {nome} atua em seu setor de referência com foco em soluções industriais/tecnológicas "
            f"de alto valor agregado. [NOTA: Para dados específicos sobre produtos, concorrentes e "
            f"diferenciais competitivos desta empresa, configure a GEMINI_API_KEY no arquivo .env para "
            f"permitir pesquisa automatizada via IA.]\n\n"
            f"Seus principais concorrentes diretos no Brasil incluem empresas de porte similar que "
            f"disputam os mesmos talentos de engenharia e tecnologia."
        ),
        "atuacao_bh_mg_detalhada": (
            f"A) POLOS NACIONAIS (FORA DE MG):\n"
            f"Polos industriais e operacionais a mapear.\n\n"
            f"B) PRESENÇA EM MINAS GERAIS: A confirmar\n"
            f"Unidades industriais e comerciais no estado de MG.\n\n"
            f"C) PRESENÇA EM BELO HORIZONTE: A confirmar\n"
            f"Escritórios ou operações na capital mineira."
        ),
        "historico_relacionamento_analise": (
            f"Histórico Consolidado na Feira UFMG:\n"
            f"- 2024: Participação {p24} (Cota {c24})\n"
            f"- 2025: Participação {p25} (Cota {c25})\n"
            f"- 2026: Participação {p26} (Cota {c26})"
        ),
        "programas_estagio_trainee_completo": (
            f"A) PROGRAMAS NACIONAIS:\n"
            f"- Programa de Estágio: Cursos de engenharia e negócios.\n"
            f"- Programa de Trainee: Aceleração corporativa.\n\n"
            f"B) PROGRAMAS EM BH / MINAS GERAIS:\n"
            f"- Contrata estagiários em MG? A verificar.\n"
            f"- Contrata trainees em MG? A verificar."
        ),
        "outras_feiras_tabela": get_verified_fairs_data(nome),

        "posicionamento_esg_inovacao": (
            f"A {nome} investe em práticas de ESG e inovação alinhadas às melhores práticas de mercado. "
            f"[NOTA: Configure a GEMINI_API_KEY para dados específicos.]"
        ),
        "guia_reuniao_ganchos": [
            f"1. 'Conhecemos as operações da {nome} em Minas Gerais e queremos posicionar a UFMG como principal fonte de talentos de engenharia para a empresa.'",
            f"2. 'Com base no histórico de participação da {nome} na feira, apresentamos a evolução do engajamento dos alunos com a sua marca.'",
            f"3. 'Qual é o perfil de engenheiro que a {nome} tem mais dificuldade de contratar hoje em MG?'"
        ],
        "guia_reuniao_pitch": (
            f"\"A {nome} possui operações estratégicas em Minas Gerais e a Escola de Engenharia da UFMG "
            f"é a principal fonte de talentos técnicos do estado. Ao garantir a cota na Feira de Carreiras, "
            f"a empresa conecta sua marca empregadora com mais de 7.000 alunos de engenharia de alta qualidade.\""
        ),
        "guia_reuniao_objecoes": [
            {"objecao": "Restrição orçamentária.", "resposta": "Recrutar direto no campus reduz o CAC de RH frente a consultorias."},
            {"objecao": "Já participamos de outras feiras.", "resposta": "A UFMG oferece perfil técnico complementar com nota máxima no ENADE."},
            {"objecao": "Dúvida entre Cota Prata e Ouro.", "resposta": "A Cota Ouro garante exclusividade no painel de abertura e prioridade."},
            {"objecao": "Recrutamento é digital.", "resposta": "Presença presencial gera experiência de marca e aumenta a taxa de aceite."}
        ]
    }


def analyze_company(company_data):
    nome = company_data["nome"]
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        logger.warning(f"GEMINI_API_KEY não configurada. Gerando dossiê para {nome}.")
        return generate_fallback_analysis(company_data)

    prompt = PROMPT_TEMPLATE.format(
        nome_empresa=nome,
        participou_2024=company_data.get("participou_2024", "Não"),
        cota_2024=company_data.get("cota_2024", "N/A"),
        participou_2025=company_data.get("participou_2025", "Não"),
        cota_2025=company_data.get("cota_2025", "N/A"),
        participou_2026=company_data.get("participou_2026", "Não"),
        cota_2026=company_data.get("cota_2026", "N/A"),
        nome_contato=company_data.get("nome_contato", "Não informado"),
        email=company_data.get("email", "Não informado")
    )

    models_to_try = [GEMINI_MODEL, "gemini-3.6-flash"]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    import time
    import requests

    last_error = None
    for model_name in models_to_try:
        max_retries = 5
        for attempt in range(max_retries):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                res = requests.post(url, json=payload, timeout=60)
                res_json = res.json()

                if "error" in res_json:
                    err = res_json["error"]
                    code = err.get("code")
                    msg = err.get("message", str(err))
                    if code == 503 and attempt < max_retries - 1:
                        sleep_time = (attempt + 1) * 2
                        logger.warning(f"Google API 503 (alta demanda temporária). Nova tentativa em {sleep_time}s ({attempt+1}/{max_retries})...")
                        time.sleep(sleep_time)
                        continue
                    raise ValueError(f"Google API Error {code}: {msg}")

                candidates = res_json.get("candidates", [])
                if not candidates or "content" not in candidates[0]:
                    raise ValueError("Resposta vazia da API do Google.")

                text_response = candidates[0]["content"]["parts"][0]["text"]

                # Limpeza de markdown caso retorne com ```json ... ```
                cleaned_text = text_response.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                elif cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()

                data = json.loads(cleaned_text)
                data["outras_feiras_tabela"] = get_verified_fairs_data(nome)
                logger.info(f"✅ Análise gerada com sucesso via Gemini ({model_name}) para {nome}!")
                return data

            except Exception as e:
                last_error = e
                if "503" in str(e) and attempt < max_retries - 1:
                    sleep_time = (attempt + 1) * 2
                    time.sleep(sleep_time)
                    continue
                logger.warning(f"Tentativa com modelo {model_name} falhou: {e}.")
                break

    logger.error(f"Erro na API para {nome}: {last_error}. Utilizando base de conhecimento local.")
    return generate_fallback_analysis(company_data)
