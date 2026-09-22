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

### 3️⃣ Gerar o Dossiê
1. **Escolha a empresa:** Selecione uma das **52 empresas da base histórica da UFMG** ou digite o nome de **qualquer outra empresa** do mercado (ex: `Gerdau`, `Localiza`, `Vale`, `Nubank`, `Embraer`...).
2. Clique no botão azul: **`🚀 Gerar Dossiê Estratégico (3 Páginas em Word)`**.
3. Em 15 a 25 segundos, clique em **`📥 Baixar Dossiê (.docx)`** para salvar o arquivo Word formatado e pronto para a reunião!

---

## 📊 O Que Contém Cada Dossiê (3 Páginas no Word):

* **Cabeçalho Institucional:** Identificação da empresa, data e aviso de confidencialidade comercial.
* **1.0 Visão Geral Institucional & Mercado:** Core business, produtos principais, escala no Brasil, concorrentes diretos e feiras disputadas.
* **2.0 Presença Física, Fábricas e Localização:**
  * **A) Polos Nacionais:** Plantas industriais fora de Minas Gerais.
  * **B) Presença em Minas Gerais:** SIM/NÃO com lista de cidades e unidades.
  * **C) Presença em Belo Horizonte:** SIM/NÃO com localização de sede corporativa ou centro de tecnologia.
* **3.0 Histórico de Relacionamento & Análise de Patrocínio (2024 - 2026):** Status de participação, histórico de cotas na UFMG e diagnóstico tático de renovação ou aumento de cota (*upsell*).
* **4.0 Programas de Atração de Talentos:** Vagas de Estágio e Trainee, cursos-alvo de engenharia e cidades de atuação (Nacional e MG).
* **5.0 Inteligência Competitiva de Feiras:** Tabela factual com dados oficiais do **Workshop Integrativo (Poli USP)** e **PUC Carreiras (PUC Minas)**.
* **6.0 ESG & Inovação:** 3 pilares estratégicos coesos (Descarbonização, Segurança Operacional e Inovação Aberta).
* **7.0 Playbook de Abordagem Comercial:** 3 ganchos de abertura, Discurso de Valor B2B (Pitch) e Matriz de Quebra de Objeções com respostas táticas baseadas em dados.

---

## 📁 Arquivos do Projeto

```text
agente_para_empresas/
├── INICIAR.bat                   # 🚀 CLIQUE AQUI PARA ABRIR O PROGRAMA
├── Gerar_Dossie.bat              # Atalho alternativo para iniciar
├── app_web.py                    # Interface visual oficial do UFMG Hub
├── ai_analyzer.py                # Motor de inteligência artificial (Gemini)
├── data_loader.py                # Leitor e unificador de planilhas
├── docx_generator.py             # Montador do documento executivo Word (.docx)
├── config.py                     # Configurações do sistema
├── requirements.txt              # Bibliotecas necessárias
├── dados (2).xlsx                # Base histórica das 52 empresas da Feira UFMG
├── feiras_participantes.xlsx     # Base verificada Poli USP e PUC Minas
├── Inauguracao_Anual_...docx     # Template institucional com cabeçalho
├── output_dossies/               # Pasta onde os arquivos Word são salvos
├── .env.example                  # Modelo de configuração de ambiente
└── .gitignore                    # Garante que sua chave privada nunca suba para a web
```

---

## 🔒 Privacidade e Segurança

O arquivo `.env` com a sua chave pessoal do Gemini **está no `.gitignore`** e nunca é enviado para a internet. Cada membro da equipe cadastra sua própria chave de forma segura e local.
