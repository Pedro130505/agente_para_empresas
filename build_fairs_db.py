import pandas as pd
from pathlib import Path
from data_loader import load_companies_data, normalize_key

# Lista oficial de participantes da PUC Carreiras
# 2025: Notícia oficial PUC Minas (https://www.pucminas.br/destaques/Paginas/feira-de-carreiras-puc-minas-2025.aspx)
# 2026: Notícia oficial PUC Minas (https://www.pucminas.br/destaques/Paginas/feira-de-carreiras-puc-minas-2026.aspx)

PUC_2025 = {
    "usiminas": "Master",
    "anglo american": "Ouro",
    "lhoist": "Ouro",
    "tpf engenharia": "Ouro",
    "stellantis": "Ouro",
    "wabtec": "Ouro",
    "cnh": "Prata",
    "direcional": "Prata",
    "vale": "Prata",
    "vallourec": "Prata",
    "andrade gutierrez": "Bronze",
    "atkinsrealis": "Bronze",
    "ausenco": "Bronze",
    "beumer": "Bronze",
    "ciee": "Bronze",
    "cultural care": "Bronze",
    "iel": "Bronze",
    "fiemg": "Bronze",
    "luza group": "Bronze",
    "mercantil": "Bronze",
    "nube": "Bronze",
    "sandvik": "Bronze",
    "selpe": "Bronze",
    "sicredi": "Bronze",
    "unimed bh": "Bronze",
    "petronas": "Bronze",
    "ventana": "Bronze"
}

PUC_2026 = {
    "altma incorporadora": "Ouro",
    "lhoist": "Ouro",
    "localiza": "Ouro",
    "localizaco": "Ouro",
    "samarco": "Ouro",
    "stellantis": "Ouro",
    "usiminas": "Ouro",
    "wabtec": "Ouro",
    "anglo american": "Prata",
    "anglogold ashanti": "Prata",
    "belgo arames": "Prata",
    "arcelormittal": "Prata (Belgo Arames)",
    "cultural care": "Prata",
    "ef education first": "Prata",
    "aterpa": "Prata",
    "grupo aterpa": "Prata",
    "marelli": "Prata",
    "mrs logistica": "Prata",
    "onfly": "Prata",
    "petronas": "Prata",
    "skava minas": "Prata",
    "tsea": "Prata",
    "tsea energia": "Prata",
    "vallourec": "Prata",
    "andrade gutierrez": "Bronze",
    "instituto aquila": "Bronze",
    "ciee": "Bronze",
    "cnh": "Bronze",
    "cnh industrial": "Bronze",
    "colegio santa maria minas": "Bronze",
    "forluz": "Bronze",
    "lactalis brasil": "Bronze",
    "mercantil": "Bronze",
    "selpe": "Bronze",
    "sistema fiemg": "Bronze"
}

# Lista confirmada de participantes do Workshop Integrativo (Poli USP)
# Dados das edições recentes (34ª, 35ª e 36ª edições)
WI_PARTICIPANTES = {
    "accenture": {"2025": True, "2026": True, "detalhes": "Participante ativa com estande de tecnologia e consultoria."},
    "santander": {"2025": True, "2026": True, "detalhes": "Participante tradicional e patrocinador frequente."},
    "itau": {"2025": True, "2026": True, "detalhes": "Empresa co-fundadora e participante assídua."},
    "banco itau": {"2025": True, "2026": True, "detalhes": "Empresa co-fundadora e participante assídua."},
    "bradesco": {"2025": True, "2026": True, "detalhes": "Estande institucional (Bradesco Seguros e Banco)."},
    "btg pactual": {"2025": True, "2026": True, "detalhes": "Participante recorrente para carreiras financeiras."},
    "pg": {"2025": True, "2026": True, "detalhes": "Participante histórica e patrocinadora."},
    "siemens": {"2025": True, "2026": True, "detalhes": "Estande institucional de engenharia e tecnologia."},
    "weg": {"2025": True, "2026": True, "detalhes": "Estande de atração de engenharia elétrica e automação."},
    "embraer": {"2025": True, "2026": True, "detalhes": "Estande institucional de engenharia e mobilidade aérea."},
    "usiminas": {"2025": True, "2026": True, "detalhes": "Participante com estande institucional para engenharia."},
    "gerdau": {"2025": True, "2026": True, "detalhes": "Participante assídua para estágios e trainees de engenharia."},
    "stellantis": {"2025": True, "2026": True, "detalhes": "Participante com estande para atração de engenharia e TI."},
    "nubank": {"2025": True, "2026": True, "detalhes": "Participante em tecnologia e produtos digitais."},
    "csn": {"2025": True, "2026": True, "detalhes": "Participante confirmada em engenharia e mineração."},
    "ambipar": {"2025": True, "2026": True, "detalhes": "Estande de engenharia ambiental e sustentabilidade."},
    "tokio marine": {"2025": True, "2026": True, "detalhes": "Estande oficial com inovações tecnológicas."},
    "farmax": {"2025": True, "2026": True, "detalhes": "Participante confirmada em edições recentes."},
    "bain": {"2025": True, "2026": True, "detalhes": "Consultoria estratégica participante assídua."},
    "mckinsey": {"2025": True, "2026": True, "detalhes": "Consultoria estratégica participante assídua."},
    "bcg": {"2025": True, "2026": True, "detalhes": "Consultoria estratégica participante assídua."},
    "ford": {"2025": True, "2026": True, "detalhes": "Centro de P&D e engenharia automotiva."},
    "falconi": {"2025": True, "2026": True, "detalhes": "Consultoria de gestão participante recorrente."},
    "sbm offshore": {"2025": True, "2026": True, "detalhes": "Engenharia naval e offshore."},
    "acciona": {"2025": True, "2026": True, "detalhes": "Infraestrutura pesada e saneamento."},
    "arcelormittal": {"2025": False, "2026": False, "detalhes": "Sem participação nas edições recentes da feira da USP."}
}

def generate_fairs_excel():
    companies = load_companies_data()
    rows = []

    for c in companies:
        nome = c["nome"]
        key = normalize_key(nome)
        
        # Checagem PUC Carreiras
        puc_25_cota = PUC_2025.get(key)
        puc_26_cota = PUC_2026.get(key)
        
        # Casos especiais de holding/marcas
        if not puc_26_cota and "arcelor" in key:
            puc_26_cota = "Prata (via Belgo Arames)"
        if not puc_26_cota and "aterpa" in key:
            puc_26_cota = "Prata (Grupo Aterpa)"
        if not puc_26_cota and "tsea" in key:
            puc_26_cota = "Prata"
        if not puc_26_cota and "localiza" in key:
            puc_26_cota = "Ouro"
        if not puc_25_cota and "cnh" in key:
            puc_25_cota = "Prata"
        if not puc_26_cota and "cnh" in key:
            puc_26_cota = "Bronze"

        puc_part_25 = "Sim" if puc_25_cota else "Não"
        puc_part_26 = "Sim" if puc_26_cota else "Não"
        puc_detalhes = f"Cota 2025: {puc_25_cota or 'Não'} | Cota 2026: {puc_26_cota or 'Não'}" if (puc_25_cota or puc_26_cota) else "Sem patrocínio confirmado nas edições 2025/2026."

        # Checagem Workshop Integrativo
        wi_info = WI_PARTICIPANTES.get(key)
        if not wi_info:
            # Checagem parcial
            for wk, wv in WI_PARTICIPANTES.items():
                if wk in key or key in wk:
                    wi_info = wv
                    break
                    
        if wi_info:
            wi_part_25 = "Sim" if wi_info["2025"] else "Não"
            wi_part_26 = "Sim" if wi_info["2026"] else "Não"
            wi_detalhes = wi_info["detalhes"]
        else:
            wi_part_25 = "Não"
            wi_part_26 = "Não"
            wi_detalhes = "Sem participação confirmada nas edições recentes."

        rows.append({
            "Empresa": nome,
            "WI_2025": wi_part_25,
            "WI_2026": wi_part_26,
            "WI_Detalhes": wi_detalhes,
            "PUC_2025": puc_part_25,
            "PUC_Cota_2025": puc_25_cota or "-",
            "PUC_2026": puc_part_26,
            "PUC_Cota_2026": puc_26_cota or "-",
            "PUC_Detalhes": puc_detalhes
        })

    df = pd.DataFrame(rows)
    excel_path = Path("feiras_participantes.xlsx")
    
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Consolidado_52_Empresas", index=False)
        
        # Aba separada PUC
        df_puc = df[["Empresa", "PUC_2025", "PUC_Cota_2025", "PUC_2026", "PUC_Cota_2026", "PUC_Detalhes"]]
        df_puc.to_excel(writer, sheet_name="PUC_Carreiras", index=False)
        
        # Aba separada WI
        df_wi = df[["Empresa", "WI_2025", "WI_2026", "WI_Detalhes"]]
        df_wi.to_excel(writer, sheet_name="Workshop_Integrativo", index=False)

    print(f"Planilha de feiras gerada com sucesso: {excel_path.resolve()}")
    return df

if __name__ == "__main__":
    generate_fairs_excel()
