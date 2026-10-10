# 🎯 UFMG Hub — Gerador de Dossiês Comerciais

> **Escola de Engenharia da UFMG · Feira de Carreiras**  
> Plataforma de inteligência comercial B2B para geração sob demanda de **Dossiês Estratégicos Executivos (3 páginas em Word `.docx`)** para reuniões de patrocínio.

---

## ⚡ Como Usar no Windows (Super Simples — 1 Clique)

Você **não precisa** abrir terminal, digitar comandos ou configurar pastas.

### 1️⃣ Iniciar o Programa
Dê **dois cliques** no arquivo:  
👉 **`INICIAR.bat`**

* O sistema verifica tudo sozinho. Se for sua primeira vez, ele instala automaticamente as bibliotecas necessárias em menos de 1 minuto.
* A interface visual abrirá automaticamente no seu navegador padrão (**Chrome, Edge, etc.**).

---

### 2️⃣ Primeiro Uso (Cadastro da Chave de IA)
Na barra lateral esquerda do site:
1. Acesse o link gratuito: [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Clique em **"Create API key"** com sua conta Google.
3. Cole a chave no campo da barra lateral.  
> ✅ **Pronto!** O sistema salva a chave no seu computador e você **nunca mais precisará digitá-la**.

---

### 3️⃣ Escolher o Tipo de Dossiê & Gerar
O sistema conta com dois modos especializados de inteligência comercial:
* **🎯 Dossiê Pré-Reunião (Prospecção Comercial — 3 Páginas):** Raio-X completo para prospecção ativa, presença em MG/BH, concorrentes diretos, feiras disputadas (Poli USP e PUC Minas), ganchos de abertura e quebra de objeções.
* **📊 Dossiê Pós-Reunião (Público-Alvo, Pipeline & Iniciativas UFMG):** Cruza os cursos da empresa com a base real de **7.842 alunos da UFMG** (`base_email_marketing.xlsx`). Traz quantitativo exato de alunos no perfil, taxa de abertura a propostas, distribuição por curso, funil temporal de formatura (2025 a 2029+), duração do estágio e trainee, ciclos seletivos, atuação prévia na UFMG (PETs, laboratórios) e equipes de extensão que mais agregam (Fórmula SAE, Baja, Milhagem, etc.).

1. **Escolha a empresa:** Selecione uma das 52 empresas mapeadas ou digite qualquer outra empresa do mercado.
2. Selecione a modalidade desejada: **Pré-Reunião** ou **Pós-Reunião**.
3. Clique em **`🚀 Gerar Dossiê`**. O documento Word (.docx) é gerado e uma cópia é enviada automaticamente para sua **Área de Trabalho (Desktop)**!

---

## 📊 Estrutura dos Dossiês no Word (.docx):

### 🎯 1. Dossiê Pré-Reunião (3 Páginas Executivas)
* **Cabeçalho Institucional:** Identificação, confidencialidade e dados de contato.
* **1.0 Visão Geral Institucional & Mercado:** Core business, produtos, concorrentes e diferenciais.
* **2.0 Presença Física, Fábricas e Localização:** Polos nacionais, cidades em MG e sede em BH.
* **3.0 Histórico de Relacionamento (2024 - 2026):** Status de participação na Feira UFMG e cota.
* **4.0 Programas de Atração:** Estágio, trainee e áreas de contratação.
* **5.0 Inteligência Competitiva de Feiras:** Workshop Integrativo (Poli USP) e PUC Carreiras.
* **6.0 ESG & Inovação:** 3 pilares corporativos essenciais.
* **7.0 Playbook Comercial:** Ganchos de reunião, pitch B2B e matriz de quebra de objeções.

### 📊 2. Dossiê Pós-Reunião (Inteligência de Público & Pipeline)
* **01. Dimensão do Público-Alvo na Base UFMG:** Total de alunos filtrados, % da base universitária e volume abertos a propostas.
* **02. Detalhamento por Curso Prioritário:** Tabela completa com alunos inscritos, % abertos a propostas e relevância técnica por curso.
* **03. Pipeline de Formatura & Estrutura dos Programas:**
  * Funil temporal (2025/2026, 2027, 2028, 2029+).
  * Duração e formato do Estágio (1 a 2 anos, carga horária).
  * Duração e formato do Trainee (12 a 24 meses, aceleração).
  * Ciclos e meses de abertura dos processos seletivos.
* **04. Atuação Prévia na UFMG:** Parcerias existentes, doação de equipamentos, projetos com PETs e laboratórios.
* **05. Iniciativas que Mais Agregam:** Equipes de competição (Fórmula SAE, Baja SAE, Milhagem UFMG, Tesla), Empresas Juniores e Grupos de Pesquisa.
* **06. Inteligência de Marca & Top of Mind:** Como a empresa é percebida pelos alunos do campus.
* **07. Roteiro Tático de Fechamento:** Discurso e números para fechamento de cotas de patrocínio.
* **08. Matriz de Objeções de Pós-Reunião:** Respostas para "já temos parceiros", "orçamento fechado" e "preferimos ações virtuais".

---

## 📁 Arquivos do Projeto

```text
ufmg-hub-dossies/
├── INICIAR.bat                   # 🚀 CLIQUE AQUI PARA ABRIR O PROGRAMA NO WINDOWS
├── Gerar_Dossie.bat              # Atalho alternativo
├── app_web.py                    # Interface visual oficial (Streamlit)
├── student_analyzer.py           # Filtro e estatísticas da base universitária da UFMG
├── base_email_marketing.xlsx     # Base com 7.842 alunos cadastrados da UFMG
├── ai_analyzer.py                # Motor de inteligência (Gemini 2.5 Flash + Knowledge Base)
├── data_loader.py                # Leitor e unificador de planilhas de feiras
├── docx_generator.py             # Montador dos documentos Word Pré e Pós-Reunião
├── config.py                     # Configurações do sistema
├── requirements.txt              # Dependências Python
├── dados (2).xlsx                # Base histórica das 52 empresas da Feira UFMG
├── feiras_participantes.xlsx     # Base de feiras Poli USP e PUC Minas
├── output_dossies/               # Pasta de salvamento dos arquivos Word
└── .env.example                  # Modelo de configuração de ambiente
```

---

## 🔒 Privacidade e Segurança

O arquivo `.env` com a sua chave pessoal do Gemini **está no `.gitignore`** e nunca é enviado para a internet. Cada membro da equipe cadastra sua própria chave de forma segura e local.
