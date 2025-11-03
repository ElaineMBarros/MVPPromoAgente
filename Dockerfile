# Usar imagem Python oficial
FROM python:3.10-slim

# Instalar Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (cache de layers)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip list && \
    echo "=== VERIFICANDO INSTALAÇÃO ===" && \
    python3 -c "import openai; print(f'OpenAI version: {openai.__version__}')"

# Copiar package.json do frontend
COPY frontend/package*.json ./frontend/

# Instalar dependências do frontend
WORKDIR /app/frontend
RUN npm ci

# Voltar para /app e copiar todo o resto
WORKDIR /app
COPY . .

# Build do frontend
WORKDIR /app/frontend
RUN npm run build

# Voltar para /app
WORKDIR /app

# Verificar se start.py foi copiado e torná-lo executável
RUN ls -la && \
    chmod +x start.py && \
    cat start.py

# Forçar variáveis de ambiente (Railway passa variáveis de ambiente)
ENV ENVIRONMENT=production
ENV OPENAI_MODEL=gpt-4o-mini

# Expor porta (Railway define $PORT)
EXPOSE 8000

# Comando para iniciar o servidor usando script Python
CMD ["python3", "start.py"]
