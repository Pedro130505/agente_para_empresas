# 🌐 Guia de Deploy em Servidor Próprio (VPS / Nuvem Própria)

Este guia ensina como hospedar a plataforma do **UFMG Hub** em um servidor próprio (Ubuntu/Debian) em qualquer provedor (DigitalOcean, AWS EC2, Hostinger, Hetzner, Oracle Cloud ou servidor da própria UFMG).

---

## ⚡ Método 1: Deploy com Docker (Recomendado — 1 Comando)

Se o seu servidor tiver Docker instalado, você só precisa de 2 minutos.

### 1. No servidor, clone o repositório:
```bash
git clone https://github.com/Pedro130505/agente_para_empresas.git
cd agente_para_empresas
```

### 2. Configure a Chave de IA no `.env`:
```bash
cp .env.example .env
nano .env
```
*(Cole sua chave GEMINI_API_KEY e salve com `Ctrl+O` e `Enter`, depois saia com `Ctrl+X`)*.

### 3. Inicie o container:
```bash
docker compose up --build -d
```

> ✅ **Pronto!** O site já estará no ar em: `http://SEU_IP_DO_SERVIDOR:8501`

---

## 🔒 Método 2: Colocar em um Domínio Próprio com SSL (HTTPS e Nginx)

Para acessar por um endereço bonito como `https://dossies.ufmghub.com.br` com cadeado verde (HTTPS):

### 1. Instale o Nginx e o Certbot:
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 2. Copie a configuração do Nginx:
```bash
sudo cp nginx.conf /etc/nginx/sites-available/dossies.ufmghub.com.br
```

Edite o arquivo para colocar seu domínio:
```bash
sudo nano /etc/nginx/sites-available/dossies.ufmghub.com.br
```
*(Altere `server_name` para o seu domínio real).*

### 3. Ative o site no Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/dossies.ufmghub.com.br /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Gere o certificado SSL gratuito com Certbot:
```bash
sudo certbot --nginx -d dossies.ufmghub.com.br
```

> 🎉 O Certbot configurará o HTTPS automaticamente com renovação automática!

---

## 🖥️ Método 3: Deploy Direto no Linux (Sem Docker, via Systemd)

Se preferir rodar direto no Python do servidor Ubuntu sem Docker:

### 1. Instale o Python e dependências do sistema:
```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Mova o projeto para `/var/www`:
```bash
sudo git clone https://github.com/Pedro130505/agente_para_empresas.git /var/www/agente_para_empresas
cd /var/www/agente_para_empresas
pip3 install -r requirements.txt
cp .env.example .env
nano .env  # Coloque a GEMINI_API_KEY
```

### 3. Ative o serviço contínuo com Systemd:
```bash
sudo cp ufmg_hub.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ufmg_hub
sudo systemctl start ufmg_hub
```

Para verificar se está rodando:
```bash
sudo systemctl status ufmg_hub
```
