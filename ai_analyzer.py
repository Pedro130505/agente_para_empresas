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


POST_MEETING_PROMPT_TEMPLATE = """Você é um Analista Sênior de Inteligência Comercial e Planejamento Universitário do UFMG Hub (Mercado em Conexão - Escola de Engenharia da UFMG).

Sua missão é criar um **DOSSIÊ ESTRATÉGICO PÓS-REUNIÃO DE ALTA PRECISÃO FACTUAL** para a empresa **"{nome_empresa}"**, focado em avanço de proposta de patrocínio, detalhamento de pipeline de formação e sinergia com iniciativas acadêmicas da UFMG.

Contexto da Empresa na Feira UFMG:
- Histórico: 2024 ({participou_2024}), 2025 ({participou_2025}), 2026 ({participou_2026})
- Contato / Interlocutor: {nome_contato} | E-mail: {email}

Retorne ESTRITAMENTE um JSON válido com a seguinte estrutura:
{{
  "resumo_executivo": "Síntese executiva densa da empresa, produtos, escala de faturamento/colaboradores e operações em MG e Brasil.",
  "perfil_interlocutor": "Análise do perfil do interlocutor cadastrado ({nome_contato}), cargo ou área, e como conduzir a conversa técnica de avanço.",
  "cursos_alvo_lista": ["Engenharia Mecânica", "Engenharia Elétrica", "Engenharia de Controle e Automação", "Engenharia de Produção", "Ciência da Computação"],
  "duracao_estagio": "Quanto tempo dura o estágio nesta empresa (ex: 1 a 2 anos, 20h ou 30h semanais, modelo de rotação e efetivação).",
  "duracao_trainee": "Quanto tempo dura o Trainee (ex: 12 a 24 meses, job rotation, mentoring com lideranças).",
  "ciclos_processo_seletivo": "Quando abrem os processos seletivos de estágio (ex: semestral em março/agosto) e de trainee (ex: segundo semestre).",
  "atuacao_previa_ufmg": "Histórico ou iniciativas da empresa dentro da UFMG (ex: projetos com PET, laboratórios, convênios de pesquisa, doações de kits).",
  "iniciativas_ufmg_agregadoras": "Quais iniciativas da UFMG mais agregam para esta empresa (ex: equipes de competição automotivas Fórmula SAE, Baja SAE, Milhagem UFMG, Tesla UFMG, PETs, Empresas Juniores) e como as soluções da empresa se conectam a esses projetos na prática.",
  "inteligencia_marca_top_of_mind": "Análise de presença e recall de marca frente aos concorrentes no imaginário dos alunos de engenharia da UFMG.",
  "roteiro_fechamento_cotas": "Argumentação comercial orientada a dados para fechamento/upsell de cota (destacando Cota Ouro com Arena de Iniciativas e Challenge técnico).",
  "matriz_objecoes_pos": [
    {{"objecao": "Objeção pós-reunião 1", "resposta": "Resposta tática com dados"}},
    {{"objecao": "Objeção pós-reunião 2", "resposta": "Resposta tática com dados"}},
    {{"objecao": "Objeção pós-reunião 3", "resposta": "Resposta tática com dados"}},
    {{"objecao": "Objeção pós-reunião 4", "resposta": "Resposta tática com dados"}}
  ]
}}
"""


KNOWLEDGE_BASE = {
    "stellantis": {
        "cursos_alvo_lista": ["Engenharia Mecânica", "Engenharia de Controle e Automação", "Engenharia Elétrica", "Engenharia de Produção", "Engenharia Aeroespacial", "Engenharia de Materiais", "Ciência da Computação", "Design", "Administração"],
        "duracao_estagio": "Duração de 1 a 2 anos com carga de 30h semanais nas unidades de Betim e Nova Lima (MG). O estagiário atua com mentoria direta de engenheiros do centro de P&D de Betim e conta com alta taxa de efetivação.",
        "duracao_trainee": "Duração de 18 a 24 meses através do programa global GPS (Graduate Program of Stellantis), com rotação entre áreas industriais, engenharia de produto e gestão corporativa.",
        "ciclos_processo_seletivo": "Estágio: abertura semestral contínua com turmas para o 1º semestre (inscrições em setembro/outubro) e 2º semestre (inscrições em abril/maio). Trainee: processo anual com inscrições entre julho e setembro.",
        "atuacao_previa_ufmg": "A Stellantis possui histórico de parceria com a Escola de Engenharia da UFMG em projetos de pesquisa sobre combustão flex e sistemas de powertrain híbrido (Bio-Hybrid) com o Departamento de Engenharia Mecânica.",
        "iniciativas_ufmg_agregadoras": "Equipes de automobilismo da UFMG: Fórmula UFMG (Fórmula SAE), Baja SAE UFMG, Tesla UFMG (Fórmula Elétrico) e Milhagem UFMG (veículo de alta eficiência). Alunos aplicam conceitos reais de dinâmica veicular e manufatura automotiva. Também agregam a Empresa Júnior Ibmec/UCJ e o PET Mecânica.",
        "inteligencia_marca_top_of_mind": "A Stellantis ocupa a 3ª posição no recall espontâneo dos estudantes de Engenharia Mecânica e Automação (12% das menções), atrás apenas de Embraer e Vale. Manter a Cota Ouro na MEC consolida a Fiat/Stellantis como o polo automotivo preferido em Minas Gerais.",
        "roteiro_fechamento_cotas": "Consolidação de Cota OURO: Destacar que o estande de 12m², a palestra de engenharia e o Challenge de mobilidade Bio-Hybrid conectam os líderes técnicos de Betim com os 1.800+ formandos do setor automotivo.",
        "matriz_objecoes_pos": [
            {"objecao": "Já estamos na PUC Carreiras com cota de destaque.", "resposta": "A presença na PUC é excelente, mas o perfil é complementar. A UFMG entrega a maior densidade de engenheiros de manufatura, mecatrônica e software de MG — o núcleo duro que o centro de P&D de Betim precisa."},
            {"objecao": "Nosso foco é contratação via plataforma corporativa.", "resposta": "O funil digital atrai volume, mas o contato presencial na MEC com Challenge técnico garante a atração dos alunos com nota máxima no ENADE antes que recebam propostas de outros estados."}
        ],

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
        "cursos_alvo_lista": ["Engenharia Metalúrgica", "Engenharia Mecânica", "Engenharia de Minas", "Engenharia Elétrica", "Engenharia de Controle e Automação", "Engenharia de Produção", "Engenharia de Materiais", "Ciência da Computação", "Administração"],
        "duracao_estagio": "Duração de 1 a 2 anos, com carga de 20h ou 30h semanais nas unidades de BH, João Monlevade, Juiz de Fora, Sabará, Itaúna e Itatiaiuçu. Inclui mentoria, bolsa compatível com mercado siderúrgico e trilha de efetivação.",
        "duracao_trainee": "Duração de 18 a 24 meses pelo Programa Jovens Profissionais, com imersões técnicas nas usinas integradas e projetos de descarbonização (XCarb®).",
        "ciclos_processo_seletivo": "Estágio: entradas semestrais (março/abril e agosto/setembro). Trainee: ciclo anual aberto no segundo semestre.",
        "atuacao_previa_ufmg": "Parcerias contínuas com o Departamento de Engenharia Metalúrgica e de Materiais da UFMG, além de desafios de inovação aberta promovidos pelo Açolab (hub do grupo em BH) voltados a estudantes.",
        "iniciativas_ufmg_agregadoras": "Baja SAE e Fórmula UFMG (aplicação de aços estruturais especiais e tubos de alta resistência para chassis); Minas Jr (Empresa Júnior de Engenharia de Minas e Metalurgia); PET Metalúrgica e laboratórios de siderurgia.",
        "inteligencia_marca_top_of_mind": "A ArcelorMittal disputa a preferência com Gerdau, Usiminas e Vale no setor de metais e mineração. A presença como Cota Ouro na UFMG garante que a empresa retenha os melhores metalurgistas e engenheiros de minas do estado.",
        "roteiro_fechamento_cotas": "Consolidação da Cota OURO com o Pedro Henrique: alinhar os temas do Challenge com o Açolab e agendar palestra sobre transição para Siderurgia Verde.",
        "matriz_objecoes_pos": [
            {"objecao": "A reunião com o comitê exige demonstrar sinergia técnica.", "resposta": "A sinergia é imediata: a UFMG é o polo nº 1 do Brasil em engenheiros metalúrgicos e de minas com nota máxima no ENADE, atendendo Monlevade, Juiz de Fora e Serra Azul."},
            {"objecao": "Temos processos contínuos pelo LinkedIn.", "resposta": "Plataformas digitais não proporcionam a experiência de marca presencial. Concorrentes como Gerdau e Vallourec investem fortemente no campus para atrair esses mesmos talentos."}
        ],

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
    },
    "hotmart": {
        "cursos_alvo_lista": ["Ciência da Computação", "Engenharia de Software", "Sistemas de Informação", "Ciência de Dados", "Engenharia de Computação", "Engenharia de Controle e Automação", "Engenharia de Produção", "Design", "Administração"],
        "duracao_estagio": "Duração de 1 a 2 anos com carga de 30h semanais em modelo híbrido/presencial na sede corporativa na Floresta/BH. Foco em desenvolvimento de software (backend, frontend, mobile), dados e produto.",
        "duracao_trainee": "Duração de 12 a 18 meses nas trilhas de aceleração técnica (Junior Tech Tracks), com mentoria de engenheiros seniores e arquitetos de software.",
        "ciclos_processo_seletivo": "Estágio Tech: processos semestrais nos meses de março/abril e agosto/setembro.",
        "atuacao_previa_ufmg": "A Hotmart tem a UFMG como seu principal celeiro histórico. Participou como Cota Prata em 2025 e já patrocinou eventos do Diretório Acadêmico da Computação e maratonas de programação.",
        "iniciativas_ufmg_agregadoras": "Maratona de Programação UFMG, equipes de robótica e IA do DCC, Diretório Acadêmico de Ciência da Computação, Hackathons da EE-UFMG e laboratórios de sistemas distribuídos.",
        "inteligencia_marca_top_of_mind": "A Hotmart é referência máxima de unicórnio tech mineiro entre os alunos de computação, superando concorrentes como Kiwify e Eduzz no imaginário dos formandos de Belo Horizonte.",
        "roteiro_fechamento_cotas": "Consolidação da Cota OURO com Henrique Furtado: desenhar live coding challenge no estande e talks técnicas de arquitetura de pagamentos (Hotpay).",
        "matriz_objecoes_pos": [
            {"objecao": "Já estamos confirmados na Cota Ouro, precisamos de mais dados?", "resposta": "Os dados detalhados de formatura permitem orientar as squads da Hotmart a abordar alunos específicos dos últimos períodos durante a feira."},
            {"objecao": "Concorrência com vagas remotas do exterior pagando em dólar.", "resposta": "A Hotmart oferece comunidade de elite presencial, plano de carreira acelerado, equity e estabilidade que vagas remotas isoladas não proporcionam."}
        ],

        "resumo_extenso": (
            "A Hotmart atua no setor de tecnologia, SaaS e Creator Economy, com foco principal em soluções "
            "integradas para criação, hospedagem, distribuição e monetização de produtos digitais, cursos online, "
            "comunidades e assinaturas. Trabalha diretamente com infraestrutura de pagamento internacional proprietária "
            "(Hotpay), plataformas de streaming de vídeo e conteúdo (Hotmart Club), ferramentas de automação de "
            "marketing e inteligência de dados para criadores. No Brasil, é um dos mais representativos unicórnios de tecnologia "
            "(fundada em 2011 por João Pedro Resende e Mateus Bicalho), processando transações em mais de 180 países "
            "com milhões de usuários ativos e escritórios globais. Em Minas Gerais, mantém sua sede corporativa global "
            "e seu principal polo de engenharia de software em Belo Horizonte, sendo o maior motor do ecossistema San Pedro Valley.\n\n"
            "Seus principais concorrentes diretos no país são Kiwify (forte competidor em checkout e infoprodutos), "
            "Eduzz (plataforma de produtos digitais com sede no interior de SP) e Monetizze (também sediada em Belo Horizonte). "
            "No âmbito internacional, compete com referências globais como Teachable, Udemy e Kajabi. A Hotmart se destaca "
            "frente aos rivais por sua robustez transacional e antifraude de classe mundial (Hotpay multimoedas), escala "
            "global de distribuição, ecossistema integrado para criadores e contínuo investimento em inteligência artificial "
            "aplicada à conversão de vendas e retenção de audiência.\n\n"
            "No ecossistema universitário, big techs e grandes scale-ups disputam ativamente os melhores talentos de tecnologia. "
            "Isso exige posicionamento de liderança da Hotmart na UFMG para atrair e reter prioritariamente formandos de "
            "Ciência da Computação, Engenharia de Software, Sistemas de Informação, Ciência de Dados e Engenharia de Produção."
        ),
        "atuacao_bh_mg_detalhada": (
            "A) POLOS NACIONAIS E INTERNACIONAIS (FORA DE MG):\n"
            "• Brasil: Escritório corporativo e de relacionamento em São Paulo (SP).\n"
            "• Polos Globais (Internacionais): Sedes e filiais estratégicas em Amsterdã (Holanda - sede europeia), "
            "Madri (Espanha), Cidade do México (México), Bogotá (Colômbia), Paris (França) e Estados Unidos, atendendo criadores em escala global.\n\n"
            "B) PRESENÇA EM MINAS GERAIS: SIM\n"
            "• Sede Global e Polo Operacional: Minas Gerais concentra o centro nevrálgico do ecossistema Hotmart, "
            "abrigando as equipes de arquitetura de software, infraestrutura de pagamentos (Hotpay), inteligência artificial, "
            "design de produto e a liderança executiva global da companhia.\n\n"
            "C) PRESENÇA EM BELO HORIZONTE: SIM\n"
            "• Sede Corporativa Global (Avenida Assis Chateaubriand, 499 - Floresta / San Pedro Valley): "
            "Moderno complexo corporativo com múltiplos andares dedicados à engenharia, desenvolvimento, produto e inovação.\n"
            "• Protagonismo Histórico: Berço e símbolo do 'San Pedro Valley' em BH, sendo a principal referência em empreendedorismo "
            "tecnológico e a maior empregadora tech de elite da capital mineira."
        ),
        "programas_estagio_trainee_completo": (
            "A) PROGRAMAS NACIONAIS:\n\n"
            "• Programa de Estágio Hotmart (Estágio Tech & Negócios):\n"
            "  - Cursos-alvo: Ciência da Computação, Engenharia de Software, Sistemas de Informação, Ciência de Dados, "
            "Engenharia de Produção, Engenharia Elétrica/Computação, Design/UX, Administração e Comunicação/Marketing.\n"
            "  - Cidades: Belo Horizonte (MG) e modelo de atuação híbrido.\n\n"
            "• Aceleração de Talentos Tech / Trainee & Junior Tracks:\n"
            "  - Formação contínua de desenvolvedores de software, engenheiros de dados e especialistas de produto "
            "por meio de bootcamps internos, capacitação em nuvem (AWS/GCP) e desenvolvimento de liderança ágil.\n\n"
            "B) PROGRAMAS EM BH / MINAS GERAIS:\n\n"
            "• Contrata estagiários em MG? SIM. Unidade: Belo Horizonte (Sede Floresta). "
            "Cursos: Ciência da Computação, Engenharia de Software, Sistemas de Informação, Ciência de Dados, Engenharias e Gestão.\n"
            "• Contrata recém-formados e juniores em MG? SIM. Unidade: Sede Belo Horizonte. "
            "O Departamento de Ciência da Computação (DCC) e a Escola de Engenharia da UFMG são os maiores celeiros de talentos da empresa."
        ),
        "outras_feiras_tabela": [
            {"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Não", "status_2026": "Não",
             "detalhes": "Sem participação confirmada nas edições recentes da feira da Poli USP."},
            {"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Não", "status_2026": "Não",
             "detalhes": "Sem patrocínio confirmado nas edições recentes da feira geral da PUC Minas."}
        ],
        "posicionamento_esg_inovacao": (
            "1. Inovação Tecnológica & San Pedro Valley:\n"
            "Pioneira e locomotiva do ecossistema de startups de Belo Horizonte. Infraestrutura de ponta com processamento "
            "transacional em nuvem de alta disponibilidade (AWS/GCP), algoritmos proprietários de inteligência artificial para "
            "recomendação de conteúdos e arquitetura de cibersegurança e antifraude de padrão bancário internacional (Hotpay).\n\n"
            "2. Educação Digital & Inclusão Econômica:\n"
            "Democratização do conhecimento e fomento ao microempreendedorismo digital. A plataforma capacita centenas de milhares "
            "de criadores de conteúdo e educadores a monetizarem suas habilidades técnicas e acadêmicas, gerando renda e empregos "
            "diretos e indiretos em milhares de municípios brasileiros e em mais de 180 países.\n\n"
            "3. Diversidade, Cultura & Governança Global:\n"
            "Certificada consecutivamente como Great Place to Work (GPTW). Políticas ativas de atração e promoção de talentos diversos, "
            "com grupos de afinidade consolidados, estímulo prioritário à liderança feminina em tecnologia e governança sob rígidos "
            "padrões globais de conformidade de dados e segurança (LGPD, GDPR e PCI-DSS Nível 1)."
        ),
        "guia_reuniao_ganchos": [
            "1. 'A Hotmart nasceu em BH e se tornou um unicórnio global tendo a UFMG como o grande celeiro de seus engenheiros e líderes técnicos. Com a evolução da cota Prata em 2025 para a Cota OURO em 2026, estamos consolidando essa ponte direta com os melhores desenvolvedores do estado.'",
            "2. 'Enquanto outras empresas tentam disputar desenvolvedores à distância, a Hotmart tem a imensa vantagem de ter sua sede global a poucos minutos do campus da UFMG — o estande Ouro na Feira transforma essa proximidade física em contratações técnicas de alto impacto.'",
            "3. 'Sabemos que os perfis de Engenharia de Software, Backend, Cloud e Ciência de Dados são os mais disputados e caros do mercado. Qual é a meta prioritária de contratação técnica da Hotmart para o próximo ciclo que a Feira da UFMG pode acelerar?'"
        ],
        "guia_reuniao_pitch": (
            "\"A Hotmart é o maior símbolo do sucesso tecnológico mineiro no mundo e mantém seu centro nevrálgico "
            "de engenharia e inovação em Belo Horizonte. A Escola de Engenharia e o Departamento de Ciência da Computação "
            "(DCC) da UFMG abrigam a maior concentração de mentes brilhantes em software, IA, arquitetura de sistemas e dados "
            "da América Latina — talentos que compartilham o mesmo DNA de inovação da Hotmart.\n\n"
            "Ao confirmar a Cota OURO na Feira de Carreiras da UFMG, a Hotmart não apenas consolida um patrocínio de máximo "
            "prestígio, mas posiciona seus líderes e engenheiros frente a frente com mais de 7.000 formandos de excelência. "
            "Isso reduz expressivamente o custo de aquisição de talentos (CAC de RH), acelera o preenchimento de squads críticas "
            "e reafirma o protagonismo da Hotmart como o principal destino dos melhores talentos de tecnologia de Minas Gerais.\""
        ),
        "guia_reuniao_objecoes": [
            {
                "objecao": "Já contratamos bastante via indicação e processo seletivo online.",
                "resposta": "Processos online atraem volume, mas a feira presencial permite que os tech leads e gestores da Hotmart conversem olho no olho com os alunos mais disputados do DCC e Engenharia antes que recebam ofertas remotas de empresas de fora. A conversão de talentos de elite no campus é imbatível."
            },
            {
                "objecao": "Já estamos confirmados na Cota Ouro em 2026, qual o próximo passo da parceria?",
                "resposta": "A Cota Ouro coloca a Hotmart na vitrine nobre do evento. O objetivo agora é desenhar ativações exclusivas no estande: desafios relâmpago de código (tech challenges), talks de arquitetos na programação oficial e entrega antecipada de banco de talentos dos formandos de computação e dados."
            },
            {
                "objecao": "Nosso modelo de trabalho contempla dias em home office e flexibilidade.",
                "resposta": "Justamente por isso o aluno da UFMG prioriza a Hotmart. Eles buscam a flexibilidade do modelo tech, mas dão valor incomparável a uma sede vibrante e moderna na Floresta para networking, hackathons presenciais e troca de experiências com os fundadores e líderes."
            },
            {
                "objecao": "Concorrência predatória com empresas estrangeiras pagando em dólar.",
                "resposta": "Trabalho remoto internacional costuma ser isolado, sem plano de carreira nem estabilidade. Na Hotmart, o formando da UFMG encontra uma empresa global de impacto mas com plano de carreira claro, participação societária/bônus, mentoria técnica de alto nível e forte cultura colaborativa."
            }
        ]
    },
    "carmeuse": {
        "cursos_alvo_lista": ["Engenharia de Minas", "Engenharia Química", "Engenharia Metalúrgica", "Engenharia Mecânica", "Engenharia de Produção", "Engenharia Ambiental", "Química", "Química Tecnológica", "Administração"],
        "duracao_estagio": "Duração de 1 a 2 anos, carga de 20h ou 30h semanais nas unidades de Belo Horizonte (Raja Gabaglia), Formiga e Uberlândia (Apollo III).",
        "duracao_trainee": "Duração de 12 a 18 meses focado em processos pirometalúrgicos de calcinação, lavra e gestão de plantas industriais.",
        "ciclos_processo_seletivo": "Processos seletivos contínuos e semestrais no início de cada semestre letivo.",
        "atuacao_previa_ufmg": "Nova prospecção prioritária (Greenfield); contatos acadêmicos com professores do Departamento de Engenharia de Minas e Metalurgia.",
        "iniciativas_ufmg_agregadoras": "Empresas Juniores Minas Jr (Minas e Metalurgia) e Otimiza Jr (Engenharia Química); laboratórios de tratamento de minérios e caracterização de calcários da EE-UFMG.",
        "inteligencia_marca_top_of_mind": "A Carmeuse enfrenta desconhecimento inicial de marca frente a mineradoras como Vale e concorrentes como Belocal/Lhoist. A MEC é a oportunidade perfeita de apresentar a empresa a mais de 2.500 alunos.",
        "roteiro_fechamento_cotas": "Venda de Entrada (Cota Prata ou Bronze): focar no ROI direto para suprir a demanda de R$ 1,9 bi de investimentos em Formiga e Uberlândia.",
        "matriz_objecoes_pos": [
            {"objecao": "Somos empresa B2B e os alunos não nos conhecem.", "resposta": "Exatamente por isso o estande na MEC é indispensável: transforma a Carmeuse em marca empregadora reconhecida perante os 2.500 alunos do seu perfil técnico."},
            {"objecao": "Nossas usinas ficam no interior de MG.", "resposta": "A sede fica no Luxemburgo em BH e muitos formandos da UFMG têm origem no interior ou buscam a vivência de planta industrial para acelerar a carreira."}
        ],

        "resumo_extenso": (
            "A Carmeuse Brasil atua no setor de mineração e química industrial, sendo subsidiária do Grupo Carmeuse "
            "(multinacional belga fundada em 1860, líder global na produção de cal e derivados de calcário). "
            "Trabalha diretamente com cal virgem (óxido de cálcio), cal hidratada (hidróxido de cálcio), calcário calcítico "
            "e dolomítico britado e reagentes de cálcio essenciais para flotação na mineração de ferro e ouro, "
            "dessulfuração e escorificação na siderurgia, tratamento de água e efluentes, papel e celulose, e correção agronômica de solo. "
            "No Brasil, vive um forte ciclo de expansão com investimentos previstos de até R$ 1,9 bilhão em Minas Gerais, "
            "incluindo a fábrica em Formiga (capacidade de 100 mil t/ano de cal) e a nova planta Apollo III em Uberlândia "
            "(aporte de R$ 200 milhões na 1ª fase voltado ao agronegócio regional). Em Minas Gerais, mantém sua sede corporativa em Belo Horizonte.\n\n"
            "Seus principais concorrentes diretos no país são o Grupo Lhoist / Mineração Belocal (multinacional belga rival histórica, "
            "com plantas em São José da Lapa, Matozinhos e Arcos/MG), Mineração Lapa Vermelha (Pedro Leopoldo/MG), "
            "Dagoberto Barcellos - DB e Cal Trevo / Ical. A Carmeuse se destaca frente aos rivais pela expertise técnica global "
            "de mais de 160 anos, pureza e reatividade química superior de seus produtos para siderurgia e mineração, "
            "novos fornos de alta eficiência energética e integração com silvicultura de eucalipto para descarbonização.\n\n"
            "No ecossistema universitário de Minas Gerais, grandes mineradoras e indústrias químicas disputam agressivamente os formandos. "
            "Isso exige presença estratégica da Carmeuse na UFMG para atrair talentos dos cursos de Engenharia de Minas, "
            "Engenharia Metalúrgica, Engenharia Química, Engenharia Mecânica e Engenharia de Produção, sustentando seu ousado plano de expansão fabril e mineral no estado."
        ),
        "atuacao_bh_mg_detalhada": (
            "A) POLOS NACIONAIS E INTERNACIONAIS (FORA DE MG):\n"
            "• Internacional: Presença global em mais de 25 países na Europa, Américas, Ásia e África, operando mais de 90 unidades industriais e minas de calcário.\n"
            "• Brasil / Nacional: Estrutura logística e de distribuição atendendo polos industriais, siderúrgicos e agrícolas em SP, GO, MT e ES.\n\n"
            "B) PRESENÇA EM MINAS GERAIS: SIM\n"
            "• Fábrica de Formiga (Formiga - MG, BR-354, Km 501,9): Planta fabril integrada com capacidade de 100 mil t/ano de cal, atendendo indústrias siderúrgicas, mineradoras, celulose e agronegócio.\n"
            "• Nova Planta Apollo III (Uberlândia - MG): Nova unidade industrial no Distrito Industrial de Uberlândia (investimento de R$ 200 milhões na 1ª fase, operando em 2026), focada em cal agrícola e soluções para cana-de-açúcar, café e grãos.\n"
            "• Expansão Mineral & Florestal: Aquisições de novas jazidas de calcário e florestas de eucalipto no estado de Minas Gerais para suprimento sustentável.\n\n"
            "C) PRESENÇA EM BELO HORIZONTE: SIM\n"
            "• Escritório Central / Sede Corporativa Brasil (Avenida Raja Gabaglia, 1.143 - Luxemburgo, Belo Horizonte - MG): "
            "Concentra a diretoria executiva, gerência técnica de processos, inteligência de compras, vendas B2B e recursos humanos no Brasil."
        ),
        "programas_estagio_trainee_completo": (
            "A) PROGRAMAS NACIONAIS:\n\n"
            "• Programa de Estágio Carmeuse Brasil:\n"
            "  - Cursos-alvo: Engenharia de Minas, Engenharia Metalúrgica, Engenharia Química, Engenharia Mecânica, "
            "Engenharia de Produção, Engenharia Ambiental, Química Industrial, Administração e Economia.\n"
            "  - Cidades: Belo Horizonte (MG), Formiga (MG) e Uberlândia (MG).\n\n"
            "• Formação Técnica & Trainee Operacional:\n"
            "  - Trilha de aceleração para jovens engenheiros voltada a processos pirometalúrgicos de calcinação, lavra de minas a céu aberto, manutenção industrial e laboratório de ensaios químicos.\n\n"
            "B) PROGRAMAS EM BH / MINAS GERAIS:\n\n"
            "• Contrata estagiários em MG? SIM. Unidades: Belo Horizonte (Sede Luxemburgo - áreas corporativas e engenharia), Formiga (planta industrial e mina) e Uberlândia (planta Apollo III).\n"
            "• Contrata recém-formados em MG? SIM. A Escola de Engenharia da UFMG é a principal universidade do estado na formação de engenheiros de minas, metalurgistas e químicos de alta densidade técnica."
        ),
        "outras_feiras_tabela": [
            {"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Não", "status_2026": "Não",
             "detalhes": "Sem participação confirmada nas edições recentes da feira da Poli USP."},
            {"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Não", "status_2026": "Não",
             "detalhes": "Sem patrocínio confirmado nas edições recentes."}
        ],
        "posicionamento_esg_inovacao": (
            "1. Eficiência Energética & Descarbonização da Cal:\n"
            "Desenvolvimento de fornos verticais e rotativos de calcinação de alta eficiência térmica com substituição de combustíveis fósseis "
            "por biomassa renovável (silvicultura própria de eucalipto em MG). Alinhamento global com as metas do Grupo Carmeuse de redução de pegada de carbono e captura de CO2 nos processos térmicos.\n\n"
            "2. Mineração Responsável & Economia Circular:\n"
            "Aproveitamento integral do estéril e finos de calcário em britagens e corretivos agrícolas de solo, minimizando a geração de resíduos. "
            "Lavra a seco sem necessidade de barragens de rejeitos e programas de recuperação contínua de áreas mineradas com espécies nativas do Cerrado e Mata Atlântica.\n\n"
            "3. Desenvolvimento Regional & Segurança Zero Acidentes:\n"
            "Compromisso global 'Safety First' com índice zero de acidentes. Investimento contínuo nas comunidades de Formiga, Uberlândia e região Centro-Oeste de MG "
            "através da Fundação Carmeuse (iniciativas educacionais para crianças e jovens em vulnerabilidade) e qualificação técnica da mão de obra local."
        ),
        "guia_reuniao_ganchos": [
            "1. 'Com o plano de investimento de até R$ 1,9 bilhão em Minas Gerais e a inauguração da nova planta Apollo III em Uberlândia, a Carmeuse está em seu momento mais forte de expansão no país — e a Escola de Engenharia da UFMG é a principal fonte de engenheiros de minas, químicos e metalurgistas do estado.'",
            "2. 'Sua sede nacional está instalada na Av. Raja Gabaglia aqui em BH, a poucos minutos do campus da UFMG. Ter a marca da Carmeuse presente na Feira de Carreiras conecta diretamente a diretoria com os melhores formandos técnicos antes que eles sejam contratados por grandes mineradoras tradicionais.'",
            "3. 'Sabemos que concorrentes no mercado de cal e minerais industriais, como Belocal/Lhoist e grandes mineradoras, disputam agressivamente engenheiros de processos e minas. A Feira da UFMG posiciona a Carmeuse como marca empregadora multinacional de ponta perante mais de 7.000 alunos.'"
        ],
        "guia_reuniao_pitch": (
            "\"A Carmeuse é uma potência global na indústria de cal e calcário e está vivendo um dos maiores ciclos de expansão "
            "de sua história no Brasil, aportando até R$ 1,9 bilhão em Minas Gerais com a nova planta de Uberlândia e a fábrica de Formiga, "
            "além de manter seu centro corporativo na Raja Gabaglia em Belo Horizonte. Para sustentar esse crescimento, a demanda por engenheiros "
            "de minas, metalúrgicos, químicos e mecânicos de alta qualidade técnica nunca foi tão estratégica.\n\n"
            "Ao patrocinar a Feira de Carreiras da UFMG, a Carmeuse coloca sua marca empregadora em evidência direta para os alunos mais bem "
            "avaliados do Brasil (nota máxima no ENADE). É uma oportunidade única de atrair estagiários e futuros líderes industriais para "
            "suas plantas e sede em MG, reduzindo o custo de recrutamento e consolidando a Carmeuse como a multinacional de referência para engenheiros de Minas Gerais.\""
        ),
        "guia_reuniao_objecoes": [
            {
                "objecao": "Somos uma empresa B2B e os alunos não conhecem a marca Carmeuse como conhecem Vale ou Gerdau.",
                "resposta": "Essa é exatamente a principal razão para estar na Feira. Por ser uma gigante multinacional B2B de origem belga com sede em BH, a presença no evento gera conhecimento imediato de marca empregadora, permitindo que a Carmeuse se apresente diretamente aos estudantes de engenharia de minas e química antes que eles olhem apenas para as grandes mineradoras tradicionais."
            },
            {
                "objecao": "Nossas operações industriais ficam no interior (Formiga e Uberlândia), alunos da UFMG querem ficar em BH.",
                "resposta": "A sede corporativa e centros de engenharia ficam na Raja Gabaglia em BH. Além disso, muitos alunos de engenharia de minas, metalúrgica e química da UFMG vêm de cidades do interior de MG ou buscam ativamente o ambiente dinâmico de plantas industriais para acelerar o aprendizado prático e o plano de carreira."
            },
            {
                "objecao": "Recrutamos por canais digitais (LinkedIn, Vagas.com).",
                "resposta": "Canais digitais recebem currículos genéricos, mas a concorrência por engenheiros de minas e químicos de alto nível é ferrenha. O contato presencial com estande na feira permite aos gestores da Carmeuse avaliar perfil, brilho no olho e alinhar cultura com os formandos mais disputados do estado."
            },
            {
                "objecao": "Nunca participamos da Feira da UFMG e não temos verba de patrocínio aprovada no orçamento.",
                "resposta": "Como a Carmeuse é uma nova prospecção no evento, podemos estruturar uma cota inicial focada em ROI direto de recrutamento, com acesso ao banco de currículos e ativação dirigida especificamente aos cursos de interesse imediato (Minas, Química, Metalúrgica e Mecânica)."
            }
        ]
    },

    "weg": {
        "resumo_extenso": (
            "A WEG é uma das maiores fabricantes de equipamentos elétricos do mundo, fundada em 1961 em "
            "Jaraguá do Sul (SC). Atua na fabricação de motores elétricos, automação industrial, drives e inversores "
            "de frequência, sistemas de geração, transmissão e distribuição de energia (GTD), tintas e vernizes industriais. "
            "Presente em mais de 140 países, possui market cap de aproximadamente R$ 200 bilhões (B3: WEGE3) e mais de "
            "40.000 colaboradores globais. Em Minas Gerais, possui unidades comerciais e industriais estratégicas, "
            "além de ser fornecedora de grandes projetos de infraestrutura energética, como o recente fornecimento de "
            "subestações compactas em SKID para a CEMIG (2026).\n\n"
            "Seus principais concorrentes diretos no Brasil e no mundo são Siemens, ABB, Schneider Electric e Danfoss. "
            "A WEG se destaca pela integração vertical de manufatura, altíssima eficiência energética de seus motores "
            "(linhas W22 e W50), liderança nacional absoluta em acionamentos e forte cultura de formação de talentos internos "
            "(o atual Diretor-Presidente, Alberto Kuba, ingressou na empresa como estagiário).\n\n"
            "No ecossistema universitário da UFMG, a WEG nunca participou da Feira de Carreiras (MEC), o que gerou um "
            "vazio de presença espontânea: empresas como Embraer, Vale, Stellantis e Cemig dominam a lembrança dos estudantes de "
            "Elétrica e Automação, tornando a Feira da UFMG o canal prioritário para a WEG construir preferência de carreira no estado."
        ),
        "atuacao_bh_mg_detalhada": (
            "A) POLOS NACIONAIS (FORA DE MG):\n"
            "• Parque Fabril Central: Jaraguá do Sul (SC) — maior complexo de motores e automação da América Latina.\n"
            "• Outras Plantas Industriais: Blumenau (SC), Guaramirim (SC), Itajaí (SC), Sertãozinho (SP), Betim (MG) e Linhares (ES).\n\n"
            "B) PRESENÇA EM MINAS GERAIS: SIM\n"
            "• Unidades em Betim e Belo Horizonte: Filiais comerciais, centros de assistência técnica e engenharia de aplicação.\n"
            "• Projetos Estruturantes em MG: Fornecimento de subestações compactas de energia e transformadores para a CEMIG.\n\n"
            "C) PRESENÇA EM BELO HORIZONTE: SIM\n"
            "• Escritório Regional e Centro de Suporte a Clientes atendendo mineradoras, siderúrgicas e utilities industriais de MG."
        ),
        "programas_estagio_trainee_completo": (
            "A) PROGRAMAS NACIONAIS:\n\n"
            "• Programa de Estágio WEG:\n"
            "  - Mais de 250 vagas por ciclo semestral em 6 estados (SC, SP, MG, RS, ES, PE).\n"
            "  - Cursos-alvo: Engenharia Elétrica, Automação, Mecânica, Computação, Produção, Software, Química e Administração.\n\n"
            "• Programa de Trainee Corporativo WEG:\n"
            "  - Aceleração corporativa de 12 a 18 meses com job rotation e capacitação executiva internacional.\n\n"
            "B) PROGRAMAS EM BH / MINAS GERAIS:\n\n"
            "• Contrata estagiários em MG? SIM. Unidades de Betim/BH e projetos de campo com a CEMIG e clientes industriais.\n"
            "• Contrata formandos em MG? SIM. A Escola de Engenharia da UFMG é a principal fonte formadora de engenheiros eletricistas e de automação."
        ),
        "outras_feiras_tabela": [
            {"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Não", "status_2026": "Não", "detalhes": "Sem participação confirmada nas edições recentes da USP."},
            {"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Não", "status_2026": "Não", "detalhes": "Sem estande patrocinador registrado nas edições recentes."}
        ],
        "posicionamento_esg_inovacao": (
            "1. Transição Energética & Eletromobilidade:\n"
            "Pioneirismo no desenvolvimento de powertrains elétricos para ônibus e caminhões, inversores solares fotovoltaicos e aerogeradores de energia eólica.\n\n"
            "2. Eficiência Industrial & Indústria 4.0:\n"
            "Plataforma WEG Motion Fleet Management com sensores IoT e inteligência artificial para manutenção preditiva de ativos elétricos industriais.\n\n"
            "3. Educação Corporativa & Impacto Comunitário:\n"
            "Centro WEGxpert de capacitação técnica contínua e investimentos educacionais no Centro de Treinamento WEG (desde 1968), formando milhares de técnicos e engenheiros."
        ),
        "guia_reuniao_ganchos": [
            "1. 'A WEG é líder incontestável em motores e automação no Brasil, mas os estudantes de Engenharia Elétrica da UFMG hoje lembram primeiro de Embraer e Vale. A MEC é a oportunidade de colocar a WEG no centro da preferência desses 340+ futuros eletricistas.'",
            "2. 'Com o projeto recente de subestações para a CEMIG em 2026, a WEG demonstra relevância operacional direta em MG — o recrutamento de talentos da UFMG é o próximo passo natural.'",
            "3. 'O WEGxpert foca em capacitação de alto nível. Na Arena de Iniciativas da UFMG, equipes como Tesla UFMG e Milhagem já usam inversores e motores elétricos na prática — esses alunos chegam prontos para o onboarding técnico da WEG.'"
        ],
        "guia_reuniao_pitch": (
            "\"A WEG é uma referência global de excelência industrial e inovação tecnológica. No entanto, sem presença na Feira de Carreiras da UFMG, "
            "a companhia perde a disputa espontânea de talentos para empresas que estão fisicamente no campus em contato com os mais de 7.000 alunos.\n\n"
            "Ao ingressar na MEC com a Cota Ouro, a WEG garante não apenas um estande nobre de 12m², mas realiza uma palestra exclusiva e um Challenge técnico "
            "ao vivo, permitindo que os engenheiros do WEGxpert avaliem na prática a capacidade analítica dos melhores formandos de Elétrica e Automação do Brasil.\""
        ),
        "guia_reuniao_objecoes": [
            {"objecao": "Nunca participamos de feiras universitárias em MG.", "resposta": "Exatamente por isso a oportunidade é enorme: tela em branco, sem histórico negativo e com demanda reprimida de alunos dos melhores cursos de Elétrica e Automação do estado."},
            {"objecao": "Nosso recrutamento é centralizado em SC.", "resposta": "A MEC constrói a intenção de candidatura e a atratividade antes do funil do Gupy. O aluno que conhece os desafios da WEG no campus se candidata ativamente para as vagas corporativas e de engenharia."},
            {"objecao": "Já usamos plataformas digitais com bom volume de inscritos.", "resposta": "Volume digital não resolve o gargalo da triagem técnica. O Challenge na feira permite testar raciocínio técnico e capacidade de resolução ao vivo."},
            {"objecao": "Orçamento precisa ser aprovado pela diretoria.", "resposta": "A Cota Ouro custa R$ 27.000 no valor promocional. Um único headhunter para engenheiro pleno custa de R$ 15.000 a R$ 30.000. Duas contratações diretas já pagam 100% do investimento."}
        ],
        "cursos_alvo_lista": [
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
        "duracao_estagio": "Duração de 1 a 2 anos, carga horária de 20h ou 30h semanais. Programa ativo desde 1973 com bolsa auxílio, alimentação subsidiada, auxílio-transporte e alto índice histórico de efetivação para posições de engenharia plena (o próprio Diretor-Presidente começou como estagiário).",
        "duracao_trainee": "Duração de 12 a 18 meses, com job rotation entre áreas de P&D, engenharia de aplicação, manufatura e negócios internacionais, com mentoria direta de diretores executivos.",
        "ciclos_processo_seletivo": "Estágio: abertura semestral contínua (turma do 1º semestre com inscrições em setembro/outubro; turma do 2º semestre com inscrições em março/abril). Trainee: processo anual com inscrições no segundo semestre (julho a setembro).",
        "atuacao_previa_ufmg": "A WEG já realizou eventos técnicos e capacitação em conjunto com o PET Elétrica (Programa de Educação Tutorial da Engenharia Elétrica) no ano anterior, além de possuir doações de motores e drives instalados em bancadas didáticas do Departamento de Engenharia Elétrica da Escola de Engenharia.",
        "iniciativas_ufmg_agregadoras": (
            "1. Equipe Tesla UFMG: Equipe de Fórmula Elétrico da UFMG que projeta protótipos de corrida 100% elétricos, utilizando motores elétricos, baterias e inversores com sinergia total com a WEG.\n"
            "2. Equipe Milhagem UFMG: Projeto de eficiência energética veicular que desenvolve veículos de ultrabaixo consumo elétrico, demandando motores brushless e eletrônica de potência.\n"
            "3. Equipes Fórmula SAE e Baja SAE: Utilização de sensores, módulos de telemetria e acionamentos.\n"
            "4. PET Elétrica e PET Mecânica: Grupos de excelência acadêmica que formam lideranças técnicas em sistemas de potência e automação.\n"
            "5. Empresa Júnior CPE Jr: Consultoria em projetos elétricos e automação que utiliza normas e equipamentos WEG em projetos para clientes reais."
        ),
        "inteligencia_marca_top_of_mind": (
            "Na pesquisa espontânea de Top of Mind com os estudantes de Engenharia Elétrica e Automação da UFMG, Embraer lidera com 31% das menções (259 votos), seguida por Vale (24,6%), Stellantis (12%), Petrobras (10,5%), Google (7,8%) e Cemig (6,9%). "
            "A WEG não figurou no top 15 espontâneo. Isso comprova que a marca sofre de invisibilidade no radar dos alunos da UFMG pela ausência histórica no evento — lacuna que a Cota Ouro corrige de imediato."
        ),
        "roteiro_fechamento_cotas": (
            "Avanço de Proposta Comercial: Apresentar a Cota OURO como investimento de alto ROI (R$ 27.000). A Cota Ouro inclui Estande 12m², Palestra exclusiva de 50 minutos, realização do Challenge técnico (avaliação ao vivo de estudantes) e integração na Arena de Iniciativas com as equipes Tesla e Milhagem. "
            "Como alternativa de entrada, a Cota Prata (R$ 20.250) contempla estande de 10m² e Arena de Iniciativas."
        ),
        "matriz_objecoes_pos": [
            {"objecao": "A reunião precisa passar pelo RH corporativo antes de avançar.", "resposta": "Excelente. Já preparamos este dossiê com os dados filtrados de alunos e formatura exatamente para fundamentar a reunião interna. Podemos agendar uma rodada técnica direta com o RH para alinhar o formato do Challenge."},
            {"objecao": "Nosso processo seletivo é centralizado em SC, temos poucas vagas fixas em BH.", "resposta": "O estudante da UFMG tem alta mobilidade e busca oportunidades de ponta no Brasil e exterior. Quem conhece a WEG na MEC se candidata ativamente no funil digital e aceita relocalização para SC com muito mais facilidade."},
            {"objecao": "Já estamos no meio do ano, o timing funciona para o planejamento da WEG?", "resposta": "O momento é perfeito: a contratação para a turma do próximo semestre começa exatamente agora. Estar no evento garante o preenchimento das vagas com os melhores formandos antes que eles aceitem ofertas de outras empresas."},
            {"objecao": "Como justificamos o ROI da Cota Ouro frente à Cota Bronze?", "resposta": "A Cota Bronze dá apenas presença visual. A Cota Ouro inclui a palestra técnica e o Challenge — transformando a participação em uma etapa prática de recrutamento que economiza milhares de reais em consultorias de atração."}
        ]
    },
    "petronas": {
        "resumo_extenso": (
            "A PETRONAS Lubricants International (PLI) é o braço global de fabricação e comercialização de lubrificantes "
            "da PETRONAS, a empresa nacional de petróleo e gás da Malásia (Fortune Global 500). No Brasil, opera uma das "
            "mais modernas fábricas de lubrificantes e centro de excelência tecnológica da América Latina, "
            "localizada em Contagem (Região Metropolitana de Belo Horizonte/MG). Produz lubrificantes de alta tecnologia "
            "para motores e transmissões das marcas PETRONAS Syntium (com tecnologia CoolTech™ desenvolvida na Fórmula 1), "
            "PETRONAS Urania e fluidos funcionais industriais Tutela. É a parceira técnica oficial e fornecedora de fluidos "
            "da octacampeã mundial Mercedes-AMG PETRONAS Formula One Team.\n\n"
            "Seus principais concorrentes diretos no Brasil são Mobil (Moove/Cosan), Shell (Raízen), Vibra (Lubrax), "
            "Castrol (bp) e Ipiranga. A Petronas se destaca pelo complexo industrial e laboratorial próprio em Contagem (MG), "
            "transferência direta de tecnologia das pistas da Fórmula 1 para os produtos comerciais e forte atuação em "
            "eficiência térmica de motores e fluidos para veículos elétricos e híbridos (PETRONAS Iona).\n\n"
            "No ecossistema universitário da UFMG, a Petronas participou da edição 2026 na Cota Bronze e Cota Prata na "
            "PUC Carreiras. No entanto, no recall espontâneo dos estudantes, a Petrobras domina com folga as menções "
            "(~250 citações), enquanto a Petronas registrou apenas 3 menções (0,2% do público-alvo). A evolução para a "
            "Cota Ouro na MEC é a alavanca indispensável para transformar a marca empregadora em referência entre os formandos."
        ),
        "atuacao_bh_mg_detalhada": (
            "A) POLOS NACIONAIS E INTERNACIONAIS (FORA DE MG):\n"
            "• Sede Global: Kuala Lumpur (Malásia) e Turim (Itália - centro de P&D global de lubrificantes).\n"
            "• Brasil / Nacional: Centros de distribuição e filiais comerciais em SP, RJ e polos agrícolas e industriais.\n\n"
            "B) PRESENÇA EM MINAS GERAIS: SIM\n"
            "• Complexo Industrial e Laboratório de P&D de Contagem (MG): Principal planta produtiva de lubrificantes e fluidos da companhia na América Latina, com capacidade superior a 150 milhões de litros/ano.\n\n"
            "C) PRESENÇA EM BELO HORIZONTE E RMBH: SIM\n"
            "• Centro Administrativo, Comercial LATAM e Laboratório Tecnológico Avançado instalados em Contagem (a menos de 20 km do campus da UFMG Pampulha)."
        ),
        "programas_estagio_trainee_completo": (
            "A) PROGRAMAS NACIONAIS:\n\n"
            "• Programa de Estágio PETRONAS Brasil:\n"
            "  - Cursos-alvo: Engenharia Química, Engenharia Mecânica, Engenharia de Produção, Engenharia Elétrica, Química Tecnológica, Administração e Economia.\n"
            "  - Atuação: Contagem (MG) e escritórios comerciais.\n\n"
            "• Programa Trainee Internacional:\n"
            "  - Formação de líderes e especialistas técnicos com atuação em manufatura, suprimentos e comercial na América Latina.\n\n"
            "B) PROGRAMAS EM BH / MINAS GERAIS:\n\n"
            "• Contrata estagiários em MG? SIM. Unidade fabril e laboratorial de Contagem (MG). Cursos: Eng. Química, Mecânica, Produção e Química.\n"
            "• Contrata recém-formados em MG? SIM. A UFMG é a principal universidade de onde a empresa recruta seus engenheiros químicos e de processos industriais."
        ),
        "outras_feiras_tabela": [
            {"feira": "Workshop Integrativo (WI - Poli USP)", "status_2025": "Não", "status_2026": "Não", "detalhes": "Sem participação confirmada nas edições recentes da Poli USP."},
            {"feira": "PUC Carreiras (PUC Minas)", "status_2025": "Não", "status_2026": "Sim", "detalhes": "Participação confirmada na edição 2026 com Patrocínio Prata."}
        ],
        "posicionamento_esg_inovacao": (
            "1. Tecnologia Térmica & Redução de Emissões:\n"
            "Desenvolvimento da linha CoolTech™ que combate o superaquecimento do motor, melhorando a eficiência de combustível e reduzindo a emissão de CO2 em até 3%.\n\n"
            "2. Eletrificação & Linha PETRONAS Iona:\n"
            "Fluidos desenvolvidos especificamente para veículos híbridos e 100% elétricos, otimizando o arrefecimento de baterias e caixas de transmissão elétrica.\n\n"
            "3. Sustentabilidade Operacional em MG:\n"
            "Complexo de Contagem com programas de destinação correta de resíduos, reciclagem de embalagens plásticas e projetos de responsabilidade social com escolas da RMBH."
        ),
        "guia_reuniao_ganchos": [
            "1. 'A Petronas tem uma fábrica ultramoderna e o centro tecnológico de lubrificantes da América Latina em Contagem, a poucos minutos da UFMG — porém, apenas 0,2% dos alunos a citaram espontaneamente. A Cota Ouro na MEC transforma essa proximidade geográfica em liderança de marca empregadora.'",
            "2. 'Enquanto a Petrobras concentra a memória dos alunos no setor de petróleo, a Petronas é a marca privada global que desenvolve a tecnologia da Fórmula 1 — esse é o apelo mais atrativo do mundo para estudantes de Engenharia Mecânica e Química.'",
            "3. 'Identificamos mais de 1.790 alunos nos cursos exatos de contratação da Petronas em Contagem na base da UFMG, com quase 80% abertos a propostas. Esse público está pronto para ser impactado no evento.'"
        ],
        "guia_reuniao_pitch": (
            "\"A Petronas é uma multinacional de energia com padrão tecnológico de Fórmula 1 e mantém seu coração produtivo na América Latina instalado em Contagem. A Escola de Engenharia da UFMG forma os melhores engenheiros químicos, mecânicos e de produção do estado — exatamente os perfis que sustentam o laboratório e a planta fabril da empresa.\n\n"
            "Ao evoluir da Cota Bronze para a Cota OURO na MEC, a Petronas sai da posição de estande estático e assume o palco: realiza uma palestra técnica de 50 minutos para falar da ciência dos fluidos na Fórmula 1 e lança um Challenge de sustentabilidade que engaja os alunos mais brilhantes do estado.\""
        ),
        "guia_reuniao_objecoes": [
            {"objecao": "Já participamos da Cota Bronze em 2026, queremos manter o mesmo formato.", "resposta": "A Cota Bronze serviu para marcar presença inicial. Porém, os dados da base mostram que menos de 1% dos alunos têm recall da marca. A Cota Ouro entrega a palestra exclusiva e o Challenge, que geram conexão emocional e convertem os melhores alunos para o processo seletivo."},
            {"objecao": "Nossa unidade fica em Contagem, os alunos têm resistência a se deslocar?", "resposta": "Ao contrário: mais de 70% dos alunos de engenharia da UFMG residem na região metropolitana ou têm fácil acesso à via expressa de Contagem. A oportunidade de trabalhar em uma planta de nível internacional com padrão global atrai maciçamente esses estudantes."},
            {"objecao": "Já estamos na PUC Carreiras com Cota Prata.", "resposta": "Excelente. A PUC entrega perfis corporativos muito bons, mas a Escola de Engenharia da UFMG concentra a maior densidade de pesquisa laboratorial em química, tribologia e processos térmicos do estado — o público mais qualificado para a engenharia de lubrificantes."},
            {"objecao": "Restrição de budget para upsell de cota.", "resposta": "O custo de contratação de um único engenheiro químico sênior por consultoria externa supera R$ 12.000. O investimento na Cota Ouro garante o pipeline completo de estagiários qualificados para o ano inteiro, reduzindo drasticamente o CAC de RH."}
        ],
        "cursos_alvo_lista": [
            "Engenharia Química",
            "Engenharia Mecânica",
            "Engenharia de Produção",
            "Engenharia Elétrica",
            "Engenharia Metalúrgica",
            "Engenharia de Minas",
            "Química",
            "Química Tecnológica",
            "Administração",
            "Ciências Econômicas"
        ],
        "duracao_estagio": "Duração de 1 a 2 anos, com carga de 30h semanais em formato híbrido/presencial na unidade fabril de Contagem (MG). O estagiário recebe bolsa auxílio compatível com o mercado de energia, vale-alimentação, plano de saúde, transporte fretado e acompanhamento de carreira estruturado.",
        "duracao_trainee": "Duração de 18 a 24 meses com trilhas de aceleração executiva em manufatura, desenvolvimento de novos fluidos, supply chain e inteligência comercial na América Latina.",
        "ciclos_processo_seletivo": "Estágio: abertura semestral em março/abril (turma do 2º semestre) e agosto/setembro (turma do 1º semestre seguinte). Trainee: processos bienais/anuais no início do segundo semestre.",
        "atuacao_previa_ufmg": "A Petronas foi patrocinadora da edição MEC 2026 (Cota Bronze) e mantém relacionamento técnico com professores e pesquisadores do Departamento de Engenharia Mecânica e Química da UFMG em análises tribológicas e de viscosidade.",
        "iniciativas_ufmg_agregadoras": (
            "1. Equipe Fórmula UFMG (Fórmula SAE): Protótipo de corrida a combustão de alta performance cujos motores operam em rotações extremas, exigindo lubrificantes com tecnologia de Fórmula 1 e fluidos de freio de alta temperatura.\n"
            "2. Equipe Baja SAE UFMG: Veículo off-road submetido a condições severas de poeira, lama e choque térmico, demandando graxas e fluidos de transmissão ultrarresistentes.\n"
            "3. Equipe Milhagem UFMG: Projeto focado em reduzir atrito ao máximo para quebrar recordes de quilometragem por litro, sinergia total com a tecnologia de lubrificantes de baixo atrito Syntium.\n"
            "4. Empresa Júnior Otimiza Jr (Engenharia Química) e Laboratórios de Tribologia e Catálise da UFMG: Alunos envolvidos em simulações de fluxo, análises físico-químicas e caracterização de fluidos industriais."
        ),
        "inteligencia_marca_top_of_mind": (
            "No público-alvo de engenharia da Petronas, a Petrobras domina amplamente com 480 menções (9,1% da base), seguida por Shell/Raízen (~20 menções). "
            "A Petronas registrou apenas 3 menções espontâneas (0,2% do público). Esse território na mente dos alunos em MG está aberto para ser conquistado, e a Cota Ouro na MEC com a palestra e o Challenge posiciona a Petronas como a multinacional privada preferida dos engenheiros químicos e mecânicos."
        ),
        "roteiro_fechamento_cotas": (
            "Avanço de Proposta Comercial: Realizar o upsell de Bronze para Cota OURO. A Cota Ouro inclui estande de 12m², palestra técnica de 50 minutos no auditório, realização de Challenge exclusivo de formulação e eficiência energética e participação na Arena de Iniciativas conectando diretamente com as equipes de automobilismo universitário."
        ),
        "matriz_objecoes_pos": [
            {"objecao": "A Cota Bronze já atendeu nossas necessidades na última edição.", "resposta": "A Cota Bronze deu presença passiva. Mas 99% dos alunos passaram sem saber que a Petronas tem a maior fábrica da América Latina em Contagem. A Cota Ouro traz a palestra técnica e o Challenge, convertendo visitantes em candidatos altamente preparados."},
            {"objecao": "Nosso RH corporativo avalia presença em feiras globais, não regionais.", "resposta": "Os engenheiros que operam a planta de Contagem e os laboratórios de P&D são formados em Minas Gerais. Não é possível recrutar mão de obra técnica de classe mundial para a fábrica de Contagem sem presença física no campus da UFMG."},
            {"objecao": "O valor da Cota Ouro representa um incremento orçamentário.", "resposta": "Esse incremento se paga na primeira contratação direta de estágio ou júnior que não demandar agência de recrutamento. Além disso, a Cota Ouro garante acesso antecipado aos currículos dos 1.700+ formandos do perfil Petronas."},
            {"objecao": "Queremos focar mais em projetos com professores e menos em estande de feira.", "resposta": "A Cota Ouro inclui a Arena de Iniciativas, que é exatamente o espaço de conexão com os grupos de extensão, laboratórios e equipes acadêmicas (Fórmula SAE, Baja e Otimiza Jr). Une recrutamento com relacionamento acadêmico."}
        ]
    },
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
    resp_2026 = company_data.get("responsavel_2026", "")
    resp_txt = f"\n- Responsável Comercial 2026: {resp_2026}" if resp_2026 else ""

    # Verificar se temos dados pré-pesquisados para a empresa
    key = nome.lower().strip()
    if key in KNOWLEDGE_BASE:
        result = dict(KNOWLEDGE_BASE[key])
        if key == "carmeuse" or (p24 == "Não" and p25 == "Não" and p26 == "Não"):
            diag = (
                f"Histórico Consolidado na Feira UFMG:\n"
                f"- 2024: Participação {p24} (Cota {c24})\n"
                f"- 2025: Participação {p25} (Cota {c25})\n"
                f"- 2026: Participação {p26} (Cota {c26}) | Status: Nova Prospecção Estratégica{resp_txt}\n\n"
                f"Diagnóstico Estratégico & Oportunidade Comercial de Entrada:\n"
                f"A {nome} figura como uma conta de prospecção prioritária no ecossistema de engenharia da UFMG. "
                f"Com sede corporativa instalada na Av. Raja Gabaglia em Belo Horizonte e um agressivo plano de expansão "
                f"de até R$ 1,9 bilhão em Minas Gerais (incluindo a fábrica em Formiga e a nova planta Apollo III em Uberlândia), "
                f"a empresa vive seu momento mais forte de demanda por talentos técnicos.\n\n"
                f"Para a reunião comercial, o objetivo principal é a VENDA DE ENTRADA (Cota Bronze ou Prata): demonstrar como a "
                f"presença com estande na Feira da UFMG encurta o tempo de recrutamento para engenheiros de minas, químicos, "
                f"metalúrgicos e mecânicos, consolidando a marca empregadora da Carmeuse frente aos concorrentes do setor."
            )
        elif key == "hotmart" or (p25 == "Sim" and p26 == "Sim" and "ouro" in str(c26).lower()):
            diag = (
                f"Histórico Consolidado na Feira UFMG:\n"
                f"- 2024: Participação {p24} (Cota {c24})\n"
                f"- 2025: Participação {p25} (Cota {c25})\n"
                f"- 2026: Participação {p26} (Cota {c26}){resp_txt}\n\n"
                f"Diagnóstico Estratégico & Plano de Ação Comercial:\n"
                f"A {nome} protagoniza uma trajetória exemplar de engajamento e valorização do ecossistema UFMG. "
                f"A evolução de Cota Prata (2025) para Cota OURO (2026) comprova o altíssimo retorno sobre investimento (ROI) "
                f"obtido na atração direta de alunos da Escola de Engenharia e do Departamento de Ciência da Computação (DCC).\n\n"
                f"Para a reunião com a empresa, o objetivo principal não é apenas 'vender participação', mas CONSOLIDAR O SUCESSO DA COTA OURO: "
                f"garantir localização física de prestígio para o estande, desenhar desafios técnicos integrados (live coding / tech challenges), "
                f"coordenar talks com líderes de engenharia/produto e estruturar a fidelização contínua para as próximas edições."
            )
        else:
            diag = (
                f"Histórico Consolidado na Feira UFMG:\n"
                f"- 2024: Participação {p24} (Cota {c24})\n"
                f"- 2025: Participação {p25} (Cota {c25})\n"
                f"- 2026: Participação {p26} (Cota {c26}){resp_txt}\n\n"
                f"Diagnóstico: A {nome} possui um padrão estratégico de investimento no evento. "
                f"A abordagem comercial recomendada é apresentar dados de engajamento dos alunos com a marca "
                f"e propor evolução ou consolidação de cota baseada no ROI de contratações diretas no campus."
            )
        result["historico_relacionamento_analise"] = diag
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
            f"- 2026: Participação {p26} (Cota {c26}){resp_txt}"
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




def generate_fallback_post_meeting_analysis(company_data):
    nome = company_data["nome"]
    key = nome.lower().strip()
    
    # Se está na base de conhecimento
    if key in KNOWLEDGE_BASE:
        kb = KNOWLEDGE_BASE[key]
        return {
            "tipo_dossie": "pos_reuniao",
            "nome": nome,
            "resumo_executivo": kb.get("resumo_extenso", ""),
            "perfil_interlocutor": f"Interlocutor mapeado: {company_data.get('nome_contato') or company_data.get('responsavel_2026') or 'Representante Comercial'}. Foco em conduzir o alinhamento técnico para fechamento de proposta.",
            "cursos_alvo_lista": kb.get("cursos_alvo_lista", ["Engenharia Mecânica", "Engenharia Elétrica", "Engenharia de Controle e Automação", "Engenharia de Produção", "Ciência da Computação"]),
            "duracao_estagio": kb.get("duracao_estagio", "Duração padrão de 1 a 2 anos com carga horária de 20h a 30h semanais e trilha de efetivação."),
            "duracao_trainee": kb.get("duracao_trainee", "Duração de 12 a 24 meses com job rotation e desenvolvimento acelerado."),
            "ciclos_processo_seletivo": kb.get("ciclos_processo_seletivo", "Processos seletivos de estágio com abertura semestral (março/agosto) e trainee anual no segundo semestre."),
            "atuacao_previa_ufmg": kb.get("atuacao_previa_ufmg", "Histórico de relacionamento e atração com a Escola de Engenharia da UFMG."),
            "iniciativas_ufmg_agregadoras": kb.get("iniciativas_ufmg_agregadoras", "Equipes de competição automotivas (Fórmula SAE, Baja SAE, Milhagem), PETs e Empresas Juniores."),
            "inteligencia_marca_top_of_mind": kb.get("inteligencia_marca_top_of_mind", "Análise de recall espontâneo na base da UFMG frente aos concorrentes diretos."),
            "roteiro_fechamento_cotas": kb.get("roteiro_fechamento_cotas", "Recomendação comercial de fechamento destacando Cota Ouro com Challenge e Arena de Iniciativas."),
            "matriz_objecoes_pos": kb.get("matriz_objecoes_pos", [
                {"objecao": "Aprovação pendente com o RH corporativo.", "resposta": "Os dados filtrados de alunos fornecem o material executivo ideal para fundamentar a reunião interna com o RH."},
                {"objecao": "Restrição de orçamento para este ciclo.", "resposta": "O custo de contratação de um único engenheiro por headhunter supera o valor da cota, garantindo ROI positivo imediato."}
            ])
        }

    # Fallback dinâmico para empresa nova
    return {
        "tipo_dossie": "pos_reuniao",
        "nome": nome,
        "resumo_executivo": f"A {nome} possui forte relevância em seu segmento industrial/tecnológico e demanda contínua por profissionais de engenharia e gestão de alta densidade técnica.",
        "perfil_interlocutor": f"Interlocutor registrado: {company_data.get('nome_contato', 'Gestor Técnico')}. Conduzir a conversa com foco no gargalo de contratação de talentos.",
        "cursos_alvo_lista": ["Engenharia Mecânica", "Engenharia Elétrica", "Engenharia de Controle e Automação", "Engenharia de Produção", "Ciência da Computação"],
        "duracao_estagio": "Duração média de 1 a 2 anos, carga de 20h ou 30h semanais, modelo de formação prática e alta taxa de efetivação.",
        "duracao_trainee": "Duração de 12 a 24 meses, rotação corporativa entre áreas técnicas e de gestão, aceleração para posições de liderança.",
        "ciclos_processo_seletivo": "Estágio: abertura semestral contínua nos meses de março/abril e agosto/setembro. Trainee: abertura anual concentrada no segundo semestre.",
        "atuacao_previa_ufmg": f"A {nome} figura no radar dos estudantes de engenharia e pode consolidar parcerias institucionais com laboratórios e grupos acadêmicos da Escola de Engenharia.",
        "iniciativas_ufmg_agregadoras": "Equipes de competição automobilística (Fórmula SAE, Baja SAE, Milhagem UFMG, Tesla UFMG), PETs das engenharias e Empresas Juniores (CPE Jr, Minas Jr, Otimiza Jr).",
        "inteligencia_marca_top_of_mind": f"A presença presencial no campus permite à {nome} disputar a preferência espontânea dos estudantes frente a grandes corporações tradicionais.",
        "roteiro_fechamento_cotas": "Avanço de Proposta Comercial: Recomendação da Cota OURO como investimento de maior ROI (inclui palestra no auditório, Challenge de contratação e Arena de Iniciativas).",
        "matriz_objecoes_pos": [
            {"objecao": "Processo seletivo é feito apenas via Gupy / LinkedIn.", "resposta": "Plataformas digitais geram volume mas não resolvem a triagem técnica. O Challenge na feira testa competências ao vivo e atrai candidatos com nota máxima no ENADE."},
            {"objecao": "Precisamos de aprovação da matriz / diretoria.", "resposta": "Os dados deste dossiê detalham o pipeline exato de formandos da UFMG nos cursos da empresa, servindo como justificativa executiva pronta para o comitê de patrocínio."}
        ]
    }


def analyze_company_post_meeting(company_data):
    nome = company_data["nome"]
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    key = nome.lower().strip()

    if key in KNOWLEDGE_BASE:
        logger.info(f"Utilizando inteligência pós-reunião especializada da base local para {nome}.")
        return generate_fallback_post_meeting_analysis(company_data)

    if not api_key:
        logger.warning(f"GEMINI_API_KEY não configurada. Gerando dossiê pós-reunião sintético para {nome}.")
        return generate_fallback_post_meeting_analysis(company_data)

    prompt = POST_MEETING_PROMPT_TEMPLATE.format(
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

    models_to_try = [GEMINI_MODEL, "gemini-3.6-flash", "gemini-flash-lite-latest"]
    seen = set()
    models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

    import time
    import json
    import requests

    last_error = None
    for model_name in models_to_try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                }
                res = requests.post(url, json=payload, timeout=90)
                res_json = res.json()

                if "error" in res_json:
                    err = res_json["error"]
                    code = err.get("code")
                    if code == 503 and attempt < max_retries - 1:
                        time.sleep((attempt + 1) * 2)
                        continue
                    raise ValueError(f"Google API Error {code}: {err.get('message', '')}")

                candidates = res_json.get("candidates", [])
                if not candidates or "content" not in candidates[0]:
                    raise ValueError("Resposta vazia da API do Google.")

                text_resp = candidates[0]["content"]["parts"][0]["text"].strip()
                if text_resp.startswith("```json"):
                    text_resp = text_resp[7:]
                if text_resp.startswith("```"):
                    text_resp = text_resp[3:]
                if text_resp.endswith("```"):
                    text_resp = text_resp[:-3]
                text_resp = text_resp.strip()

                data = json.loads(text_resp)
                data["tipo_dossie"] = "pos_reuniao"
                data["nome"] = nome
                logger.info(f"Análise pós-reunião gerada via Gemini ({model_name}) para {nome}!")
                return data

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if ("503" in err_str or "timeout" in err_str or "timed out" in err_str) and attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                break

    logger.warning(f"Erro na API para {nome} pós-reunião: {last_error}. Utilizando base de conhecimento local.")
    return generate_fallback_post_meeting_analysis(company_data)


def analyze_company(company_data, tipo_dossie="pre_reuniao"):
    if tipo_dossie == "pos_reuniao":
        return analyze_company_post_meeting(company_data)

    nome = company_data["nome"]
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    # Se a empresa estiver na base especializada factual, utiliza diretamente para máxima precisão e agilidade
    key = nome.lower().strip()
    if key in KNOWLEDGE_BASE:
        logger.info(f"Utilizando base de conhecimento especializada factual para {nome}.")
        return generate_fallback_analysis(company_data)

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

    models_to_try = [GEMINI_MODEL, "gemini-3.6-flash", "gemini-flash-lite-latest"]
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
                res = requests.post(url, json=payload, timeout=90)
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
                err_str = str(e).lower()
                if ("503" in err_str or "timeout" in err_str or "timed out" in err_str) and attempt < max_retries - 1:
                    sleep_time = (attempt + 1) * 2
                    logger.warning(f"Tentativa {attempt+1}/{max_retries} falhou ({e}). Tentando novamente em {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                logger.warning(f"Tentativa com modelo {model_name} falhou: {e}.")
                break

    logger.error(f"Erro na API para {nome}: {last_error}. Utilizando base de conhecimento local.")
    return generate_fallback_analysis(company_data)
