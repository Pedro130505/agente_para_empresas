# ==============================================================================
# DOCKERFILE - AGENTE UFMG HUB (PRODUCAO)
# ==============================================================================
FROM python:3.11-slim

# Evita geracao de arquivos .pyc e buffer de stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

WORKDIR /app

# Instala dependencias basicas do sistema para compilacao e curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia todo o codigo da aplicacao
COPY . .

# Garante permissao e diretorios necessarios
RUN mkdir -p output_dossies && chmod -R 755 /app

# Porta padrao do Streamlit
EXPOSE 8501

# Healthcheck para monitorar saude do container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de inicializacao
CMD ["streamlit", "run", "app_web.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
