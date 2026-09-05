# 🎯 Agente de Inteligência Comercial — UFMG Hub / Feira de Carreiras

Gerador automatizado sob demanda de **Dossiês Estratégicos Executivos (3 páginas em formato Word `.docx`)** para suporte em reuniões de prospecção e vendas de cotas de patrocínio para a Feira de Carreiras da Escola de Engenharia da UFMG.

---

## ⚡ Como Usar (Para Qualquer Membro da Equipe)

O agente foi desenhado para ser **100% plug-and-play** tanto no **Windows** quanto no **Mac (macOS)**. Você não precisa digitar comandos no terminal nem configurar arquivos manualmente.

---

### 💻 No Windows:
1. **Instalar Dependências (apenas na 1ª vez):**
   * Dê dois cliques em: 👉 **`Instalar_Dependencias.bat`**
2. **Gerar Dossiês:**
   * Dê dois cliques em: 👉 **`Gerar_Dossie.bat`**

---

### 🍏 No Mac (macOS):
1. **Instalar Dependências (apenas na 1ª vez):**
   * Dê dois cliques em: 👉 **`Instalar_Dependencias_MAC.command`**
2. **Gerar Dossiês:**
   * Dê dois cliques em: 👉 **`Gerar_Dossie_MAC.command`**
   *(Se o Mac exibir aviso de segurança na primeira vez, basta ir em Preferências do Sistema > Segurança e Privacidade > Permitir).*

---

### 🔑 Primeiro Uso (Cadastro da Chave de IA - Ambos os Sistemas)
No seu primeiro acesso, a janela solicitará a sua chave gratuita do Google Gemini:
1. Acesse: [Google AI Studio - Chave de API](https://aistudio.google.com/app/apikey)
2. Faça login com sua conta Google e clique em **"Create API key"**
3. Cole a chave no terminal e tecle **ENTER**.
> ✅ **Pronto!** A chave fica salva no seu computador e você **nunca mais precisará digitá-la**.

### 🏢 Digite o Nome da Empresa
Basta digitar o nome de qualquer empresa (ex: `Gerdau`, `Localiza`, `Vale`, `Nubank`, `Embraer`, `Seedz`...) e tecle **ENTER**.
* Em **15 a 25 segundos**, o dossiê completo de 3 páginas será gerado na pasta `output_dossies` e abrirá automaticamente no Word!

---

## 📊 Estrutura do Dossiê Estratégico (3 Páginas)

Cada dossiê gerado contém exatamente a estrutura executiva aprovada pelo time:

* **Cabeçalho Institucional:** Identificação da empresa, data e aviso de confidencialidade comercial.
* **1.0 Visão Geral Institucional & Foco de Mercado (Brasil & MG):**
  * Core business, produtos principais e escala/porte no Brasil.
  * Concorrentes diretos e diferenciais competitivos concretos.
  * Disputa por talentos de engenharia em feiras universitárias.
* **2.0 Presença Física, Fábricas e Localização de Operações em BH & MG:**
  * **A) Polos Nacionais:** Principais plantas e polos fora de MG.
  * **B) Presença em Minas Gerais:** SIM/NÃO com lista de cidades e unidades.
  * **C) Presença em Belo Horizonte:** SIM/NÃO com localização de sede corporativa ou centro de inovação.
* **3.0 Histórico de Relacionamento & Análise de Patrocínios (2024 - 2026):**
  * Histórico consolidado de participação e cotas fechadas na Feira UFMG.
  * Diagnóstico tático de renovação ou aumento de cota (*upsell* para Ouro/Diamante).
* **4.0 Programas de Atração de Talentos em BH & MG (Estágio & Trainee):**
  * Programas Nacionais e Programas específicos em MG/BH (cursos-alvo e cidades de atuação).
* **5.0 Presença em Outras Feiras Universitárias de Engenharia:**
  * Tabela factual comparativa cruzada com dados oficiais do **Workshop Integrativo (Poli USP)** e **PUC Carreiras (PUC Minas)**.
* **6.0 Posicionamento de Sustentabilidade, ESG & Inovação Tecnológica:**
  * Estruturado em 3 pilares estratégicos coesos: Descarbonização/Ecoeficiência, Inovação Aberta/Tecnologia e Impacto Social/Governança.
* **7.0 Playbook de Abordagem para Reunião Comercial:**
  * **3 Ganchos de Abertura:** Conectados a MG, aos concorrentes e ao momento da empresa.
  * **Discurso de Valor (Pitch B2B):** 2 parágrafos customizados para a reunião.
  * **Matriz de Quebra de Objeções:** Tabela com 4 objeções reais e respostas táticas baseadas em dados.

---

## 📁 Estrutura de Arquivos

```text
agente_para_empresas/
├── Gerar_Dossie.bat                 # Atalho de 2 cliques para Windows
├── Instalar_Dependencias.bat        # Instalador de dependências para Windows
├── Gerar_Dossie_MAC.command         # Atalho de 2 cliques para Mac (macOS)
├── Instalar_Dependencias_MAC.command # Instalador de dependências para Mac (macOS)
├── main.py                          # Ponto de entrada interativo do agente
├── ai_analyzer.py                   # Integração de IA com Google Gemini (REST)
├── data_loader.py                   # Leitor e unificador de bases de dados (Excel)
├── docx_generator.py                # Montador do documento Word estilizado (3 páginas)
├── config.py                        # Configurações globais e modelos
├── requirements.txt                 # Lista de dependências Python
├── dados (2).xlsx                   # Base histórica das edições 2024-2026 da Feira UFMG
├── feiras_participantes.xlsx        # Base verificada das feiras Poli USP e PUC Minas
├── Inauguracao_Anual_...docx        # Template institucional de cabeçalho
├── output_dossies/                  # Pasta de saída dos arquivos Word gerados
├── .env.example                     # Modelo de configuração da chave de API
└── .gitignore                       # Segurança: impede o envio do .env e arquivos locais
```

---

## 🔒 Segurança e Privacidade

O arquivo `.env` contendo sua chave de API **está listado no `.gitignore`** e nunca é enviado para o repositório do GitHub. Cada membro da equipe possui e cadastra sua própria chave de forma segura no seu computador.
