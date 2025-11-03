# 📦 Guia de Backup do PromoAgente

## Como Criar Backup

### Opção 1: Executar o Script Python
```bash
python backup_project.py
```

O script irá:
1. ✅ Copiar todos os arquivos essenciais
2. ✅ Excluir automaticamente node_modules, .venv, __pycache__
3. ✅ Criar pasta com timestamp: `PromoAgente_Backup_YYYYMMDD_HHMMSS`
4. ✅ Perguntar se quer criar arquivo ZIP
5. ✅ Criar arquivo `BACKUP_INFO.txt` com instruções de restauração

### Opção 2: Backup Manual Simples

Copie para um local seguro:
- ✅ Pasta `src/` (todo o backend)
- ✅ Pasta `prompts/` (prompts de IA)
- ✅ Pasta `frontend/src/` e `frontend/public/` (frontend)
- ✅ Arquivos: `main.py`, `requirements.txt`
- ✅ Arquivos: `frontend/package.json`, `frontend/vite.config.ts`
- ✅ Banco de dados: `promoagente_local.db`
- ✅ Logo: `logo_gera.png`
- ✅ Documentação: `README.md`

## Como Restaurar Backup

### 1. Extrair Backup
```bash
# Se for ZIP
unzip PromoAgente_Backup_YYYYMMDD_HHMMSS.zip

# Se for pasta
# Apenas copie todos os arquivos para novo diretório
```

### 2. Restaurar Backend
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Restaurar Frontend
```bash
cd frontend
npm install
cd ..
```

### 4. Configurar Variáveis de Ambiente
Copie `.env.example` para `.env` e configure:
```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
# ... outras configurações
```

### 5. Executar Sistema
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## Locais Seguros para Backup

### ☁️ Nuvem
- **OneDrive**: Pasta sincronizada automaticamente
- **Google Drive**: Upload manual ou backup automático
- **Dropbox**: Sincronização automática
- **GitHub**: Repositório privado (mas NÃO commitar .env!)

### 💾 Local
- **Disco Externo**: Cópia física segura
- **Pen Drive**: Para backups rápidos
- **NAS**: Se disponível na rede

### 📅 Recomendações
- ✅ Fazer backup ANTES de mudanças grandes
- ✅ Backup semanal do banco de dados
- ✅ Backup diário em desenvolvimento ativo
- ✅ Manter pelo menos 3 versões anteriores
- ✅ Testar restauração periodicamente

## Arquivos Críticos (Prioritários)

Se espaço for limitado, priorize:
1. 🔴 **CRÍTICO**: `src/`, `prompts/`, `promoagente_local.db`
2. 🟡 **IMPORTANTE**: `frontend/src/`, `requirements.txt`, `package.json`
3. 🟢 **ÚTIL**: Documentação, configs, `.env.example`

## Verificação de Integridade

Após backup, verifique:
```bash
# Contar arquivos Python
find . -name "*.py" | wc -l

# Tamanho do banco
ls -lh promoagente_local.db

# Verificar estrutura frontend
ls frontend/src/components/
```

## Automação (Opcional)

### Windows - Task Scheduler
Crie tarefa agendada para executar:
```batch
cd C:\caminho\para\projeto
python backup_project.py
```

### Linux/Mac - Cron
```bash
# Editar crontab
crontab -e

# Adicionar backup diário às 23h
0 23 * * * cd /caminho/para/projeto && python backup_project.py
```

## Suporte

Em caso de problemas com backup/restauração:
1. Verifique se todos os arquivos foram copiados
2. Confirme versões: Python 3.11+, Node 18+
3. Reinstale dependências se necessário
4. Verifique logs de erro

---

💡 **Dica**: Sempre teste a restauração em outro diretório antes de sobrescrever o projeto original!
