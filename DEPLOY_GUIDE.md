# 🚀 Guia de Deploy - PromoAgente

## 📊 Comparação de Plataformas (Mais em Conta)

### 🥇 **Railway** (RECOMENDADO) ⭐
- **Custo**: $5/mês (500 horas de execução) ou Pay-as-you-go
- **Free Trial**: $5 de crédito grátis no primeiro mês
- **Deploy**: Backend + Frontend juntos
- **Banco de dados**: SQLite funciona, ou PostgreSQL grátis
- **Vantagens**: Mais fácil, deploy automático do GitHub, suporta Python + Node.js
- **Site**: https://railway.app

### 🥈 **Render** (Alternativa Boa)
- **Custo**: Grátis (com limitações) ou $7/mês
- **Free Tier**: Backend + Frontend grátis (mas com sleep após inatividade)
- **Banco de dados**: PostgreSQL grátis (90 dias)
- **Vantagens**: Bom free tier, fácil de usar
- **Site**: https://render.com

### 🥉 **Vercel + Python Anywhere**
- **Custo**: Frontend grátis + Backend $5/mês
- **Frontend**: Vercel (grátis ilimitado)
- **Backend**: PythonAnywhere (free tier limitado ou $5/mês)
- **Vantagens**: Frontend sempre rápido e grátis
- **Sites**: https://vercel.com + https://www.pythonanywhere.com

### 💰 **Fly.io**
- **Custo**: ~$5-10/mês dependendo uso
- **Free Tier**: 3 VMs shared-cpu grátis
- **Vantagens**: Muito flexível, ótimo para apps fullstack
- **Site**: https://fly.io

---

## 🎯 RECOMENDAÇÃO: Railway (Deploy Completo)

### Por que Railway?
1. ✅ Deploy automático do GitHub
2. ✅ Suporta Python + Node.js no mesmo projeto
3. ✅ Fácil configuração de variáveis de ambiente
4. ✅ Domínio gratuito (.railway.app)
5. ✅ Logs em tempo real
6. ✅ $5 de crédito grátis no primeiro mês

---

## 📋 Contas Necessárias para Railway

### 1. **GitHub** (Já tem ✅)
- https://github.com
- Seu repositório: https://github.com/ElaineMBarros/promoAgente_backup_local

### 2. **Railway**
- https://railway.app
- Cadastro: Pode usar conta do GitHub (login social)
- Não precisa cartão de crédito no início (tem $5 grátis)

### 3. **OpenAI** (Já tem a API key ✅)
- https://platform.openai.com
- Você já tem sua chave API funcionando

### 4. **Agno/AgentOS** (Opcional - se usar)
- Se você usa o Agno, já deve ter a conta
- Caso contrário, pode remover essa dependência

---

## 🛠️ Passo-a-Passo: Deploy no Railway

### 📦 Preparação do Projeto

#### 1. Criar arquivo `railway.json` (Configuração do Railway)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && uvicorn src.app:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. Criar/Atualizar `Procfile` (Alternativa)
```
web: uvicorn src.app:app --host 0.0.0.0 --port $PORT
```

#### 3. Criar `nixpacks.toml` (Configuração de Build)
```toml
[phases.setup]
nixPkgs = ["python310", "nodejs-18_x"]

[phases.install]
cmds = [
    "pip install -r requirements.txt",
    "cd frontend && npm install && npm run build"
]

[phases.build]
cmds = ["echo Build completo"]

[start]
cmd = "uvicorn src.app:app --host 0.0.0.0 --port $PORT"
```

#### 4. Atualizar `requirements.txt` (se necessário)
Adicione as versões fixas:
```txt
fastapi==0.115.4
uvicorn[standard]==0.32.0
openai==1.54.3
python-dotenv==1.0.0
pydantic==2.9.2
sqlalchemy==2.0.36
python-multipart==0.0.12
```

#### 5. Criar script de inicialização `start.sh`
```bash
#!/bin/bash
# Instalar dependências Python
pip install -r requirements.txt

# Build do frontend
cd frontend
npm install
npm run build
cd ..

# Iniciar servidor
uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 🚀 Deploy no Railway

#### Passo 1: Criar Conta
1. Acesse https://railway.app
2. Clique em "Login" → "Login with GitHub"
3. Autorize o Railway a acessar seu GitHub

#### Passo 2: Novo Projeto
1. No dashboard, clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha: `ElaineMBarros/promoAgente_backup_local`
4. Clique em "Deploy Now"

#### Passo 3: Configurar Variáveis de Ambiente
1. No projeto, clique em "Variables"
2. Adicione as variáveis:

```env
# OpenAI
OPENAI_API_KEY=sua_chave_openai_aqui
OPENAI_MODEL=gpt-4o-mini

# Agno (se usar)
AGNO_API_KEY=sua_chave_agno_aqui

# Servidor
ENVIRONMENT=production
PORT=8000

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
EMAIL_TO=destino@example.com
```

#### Passo 4: Configurar Build
1. Na aba "Settings"
2. Em "Build Command", deixe vazio (usará nixpacks.toml)
3. Em "Start Command": 
   ```
   uvicorn src.app:app --host 0.0.0.0 --port $PORT
   ```

#### Passo 5: Deploy
1. Railway fará deploy automático
2. Aguarde o build completar (2-5 minutos)
3. Acesse a URL gerada (algo como: `promoagente-production.railway.app`)

### 🔄 Deploy Automático (CI/CD)
Após configurado, cada `git push` fará deploy automático! 🎉

---

## 💾 Banco de Dados no Railway

### Opção 1: SQLite (Mais Simples)
- **Vantagem**: Já está funcionando, sem config extra
- **Limitação**: Dados podem ser perdidos ao redeploy
- **Solução**: Usar Railway Volumes para persistência

**Adicionar Volume no Railway:**
1. Settings → Volumes → Add Volume
2. Mount Path: `/app/data`
3. Atualizar código para salvar DB em `/app/data/promoagente.db`

### Opção 2: PostgreSQL (Recomendado para Produção)
1. No Railway, clique em "New" → "Database" → "PostgreSQL"
2. Railway cria automaticamente
3. Variável `DATABASE_URL` é adicionada automaticamente
4. Atualizar código para usar PostgreSQL:

```python
# Em src/services/database.py
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./promoagente.db")

# Railway usa postgres://, SQLAlchemy precisa postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
```

---

## 🎨 Frontend no Railway

O Railway pode servir o frontend junto com o backend. Duas opções:

### Opção 1: Build Estático (Incluído no Backend)
```python
# Em src/app.py, adicionar:
from fastapi.staticfiles import StaticFiles

# Servir frontend buildado
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

### Opção 2: Deploy Separado (Avançado)
- Frontend em serviço separado no Railway
- Backend em outro serviço
- Configurar CORS corretamente

---

## 💰 Custos Estimados

### Railway (Opção Completa)
- **Primeiro Mês**: GRÁTIS ($5 de crédito)
- **Após trial**: $5-10/mês
  - Backend + Frontend: ~$5/mês
  - PostgreSQL: Incluído
  - Uso leve: ~500 horas/mês

### Considerações de Custo
- **OpenAI API**: 
  - GPT-4o-mini: $0.15/1M tokens (entrada) + $0.60/1M tokens (saída)
  - ~1000 mensagens/mês ≈ $2-5
- **Total Mensal Estimado**: $7-15/mês

---

## 🔒 Checklist de Segurança para Deploy

- [ ] Variáveis de ambiente configuradas (não hardcoded)
- [ ] .env não está no repositório (verificar .gitignore)
- [ ] OPENAI_API_KEY configurada no Railway
- [ ] CORS configurado corretamente para domínio do Railway
- [ ] Logs habilitados para debug
- [ ] Backup do banco de dados configurado (se usar PostgreSQL)
- [ ] SSL/HTTPS automático (Railway fornece)

---

## 🆘 Troubleshooting

### Build falha
```bash
# Verificar logs no Railway
# Comum: dependências faltando
# Solução: Atualizar requirements.txt ou package.json
```

### App não inicia
```bash
# Verificar:
1. PORT está sendo lido do ambiente ($PORT)
2. Variáveis de ambiente estão configuradas
3. Start command está correto
```

### Frontend não carrega
```bash
# Verificar:
1. npm run build foi executado
2. Caminho do dist está correto
3. CORS configurado (se frontend separado)
```

### Banco de dados não persiste
```bash
# Solução:
1. Usar Railway Volumes para SQLite
2. Ou migrar para PostgreSQL
```

---

## 📚 Recursos Úteis

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [FastAPI Deploy Docs](https://fastapi.tiangolo.com/deployment/)
- [Nixpacks](https://nixpacks.com/)

---

## 🎯 Próximos Passos

1. [ ] Criar conta no Railway
2. [ ] Adicionar arquivos de configuração (railway.json, nixpacks.toml)
3. [ ] Fazer commit e push
4. [ ] Conectar repositório no Railway
5. [ ] Configurar variáveis de ambiente
6. [ ] Deploy! 🚀

---

💡 **Dica**: Comece com o free trial do Railway para testar. Se funcionar bem, vale o investimento de $5/mês!
