# 🚀 Guia para Push no GitHub

## Repositório: https://github.com/ElaineMBarros/promoAgente_backup_local

## ⚠️ ANTES DE FAZER PUSH - CHECKLIST DE SEGURANÇA

### 1. Verificar .gitignore
Confirme que estes itens estão no `.gitignore`:
```
.env
.env.local
*.db
*.db-journal
.venv/
venv/
__pycache__/
node_modules/
frontend/node_modules/
frontend/dist/
*.pyc
agno.db
promoagente_local.db
```

### 2. Remover Arquivos Sensíveis (se existirem no git)
```bash
# Se .env foi commitado acidentalmente antes
git rm --cached .env
git rm --cached .env.local
git rm --cached *.db
```

## 📝 Passo-a-Passo para Push

### 1. Inicializar Git (se ainda não foi)
```bash
# Verificar se já tem git
git status

# Se não tiver, inicializar
git init
```

### 2. Configurar Remote do GitHub
```bash
# Adicionar remote (se ainda não foi)
git remote add origin https://github.com/ElaineMBarros/promoAgente_backup_local.git

# Verificar remote
git remote -v
```

### 3. Criar/Verificar .gitignore
```bash
# O arquivo .gitignore já existe, mas vamos verificar
cat .gitignore
```

### 4. Adicionar Arquivos
```bash
# Ver o que será adicionado
git status

# Adicionar todos os arquivos (exceto os no .gitignore)
git add .

# Verificar o que foi adicionado
git status
```

### 5. Fazer Commit
```bash
git commit -m "🎉 PromoAgente Sistema Completo - Backend + Frontend + IA

- Backend FastAPI com OpenAI GPT-4o-mini
- Frontend React + TypeScript + Vite
- Agentes de IA (Extractor, Validator, Summarizer)
- Sistema de histórico com auto-refresh
- Banco de dados SQLite
- Prompts otimizados e flexíveis
- Interface com logo GERA
- Sistema de backup automático
- Documentação completa"
```

### 6. Push para GitHub
```bash
# Se é o primeiro push
git branch -M main
git push -u origin main

# Se já existe o repositório
git push
```

## 🔒 Segurança - O que NÃO vai para o GitHub

✅ **Está no .gitignore (NÃO vai):**
- `.env` e `.env.local` (chaves de API)
- `*.db` (banco de dados)
- `.venv/` e `node_modules/` (dependências)
- `__pycache__/` (cache Python)

✅ **VAI para o GitHub:**
- Todo código fonte (src/, frontend/src/)
- Prompts de IA (prompts/)
- Documentação (README.md, etc)
- Configurações (requirements.txt, package.json)
- Scripts de backup
- `.env.example` (exemplo sem secrets)

## 📦 Arquivo .env.example

O `.env.example` vai para o GitHub como modelo:
```env
# OpenAI
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini

# AgentOS (Agno)
AGNO_API_KEY=sua_chave_agno_aqui

# Servidor
HOST=localhost
PORT=7000
ENVIRONMENT=development

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
EMAIL_TO=destino@example.com
```

## 🔄 Atualizações Futuras

### Fazer Pull (baixar mudanças)
```bash
git pull origin main
```

### Fazer Push (enviar mudanças)
```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

### Ver Histórico
```bash
git log --oneline
```

### Ver Diferenças
```bash
git diff
```

## 🛡️ Proteção Extra

### 1. Nunca Commitar Secrets
```bash
# Verificar antes de commit
git diff --cached

# Se ver algo sensível
git reset HEAD arquivo_sensivel.py
```

### 2. Usar GitHub Secrets (para CI/CD)
No GitHub, vá em:
- Settings → Secrets and variables → Actions
- Adicione: `OPENAI_API_KEY`, `AGNO_API_KEY`, etc.

### 3. Manter .env Local
```bash
# Criar .env local (não vai para GitHub)
cp .env.example .env
# Editar com suas chaves reais
```

## 🌿 Branches (Opcional)

### Criar Branch para Features
```bash
# Criar branch
git checkout -b feature/nova-funcionalidade

# Trabalhar na branch
git add .
git commit -m "Nova funcionalidade"

# Push da branch
git push -u origin feature/nova-funcionalidade

# Voltar para main
git checkout main

# Merge
git merge feature/nova-funcionalidade
```

## 📊 Status do Repositório

Após o push, verifique em:
https://github.com/ElaineMBarros/promoAgente_backup_local

✅ **Deve ter:**
- Código completo
- Documentação
- .gitignore correto
- README.md

❌ **NÃO deve ter:**
- Arquivo .env
- Bancos de dados (.db)
- node_modules/
- .venv/

## 🆘 Problemas Comuns

### Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/ElaineMBarros/promoAgente_backup_local.git
```

### Erro: "failed to push some refs"
```bash
# Pull primeiro
git pull origin main --allow-unrelated-histories
# Depois push
git push origin main
```

### Remover arquivo do histórico (se commitou secret)
```bash
# Usar git filter-branch ou BFG Repo-Cleaner
# Melhor: fazer repositório novo e re-upload limpo
```

## ✅ Checklist Final

Antes do push final, confirme:
- [ ] .env NÃO está na lista de arquivos (git status)
- [ ] .gitignore está correto
- [ ] README.md está atualizado
- [ ] Todos os arquivos importantes estão incluídos
- [ ] Nenhum secret ou senha no código
- [ ] Commit message é descritivo

---

💡 **Dica**: Sempre rode `git status` antes de fazer commit para ver exatamente o que será enviado!
