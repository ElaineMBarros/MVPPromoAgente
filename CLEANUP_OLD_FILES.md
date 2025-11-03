# 🧹 Limpeza de Arquivos Duplicados - PromoAgente

## Arquivos/Pastas para Remover

### ❌ Pastas Antigas Duplicadas
- `/agents/` - Substituída por `/src/agents/`
- `/core/` - Substituída por `/src/core/`

### ❌ Arquivos Python Antigos
- `main_old.py` - Versão antiga
- `main_old2.py` - Versão antiga  
- `test_chat.db` - Database de teste

### ✅ Manter (não remover)
- `/src/` - **Nova estrutura refatorada**
- `main.py` - Versão atual
- `test_chat.html` - Interface de teste criada
- Arquivos de teste (`test_*.py`) - Úteis para debug

---

## 🔧 Como Executar a Limpeza

### Opção 1: Manual (Windows)
```cmd
# Remover pastas antigas
rmdir /s /q agents
rmdir /s /q core

# Remover arquivos antigos
del main_old.py
del main_old2.py
del test_chat.db
```

### Opção 2: Manual (Linux/Mac)
```bash
# Remover pastas antigas
rm -rf agents/
rm -rf core/

# Remover arquivos antigos
rm main_old.py
rm main_old2.py  
rm test_chat.db
```

### Opção 3: Via Python
Execute o script de limpeza:
```bash
python cleanup_old_files.py
```

---

## ⚠️ IMPORTANTE

**ANTES DE REMOVER:**
1. Certifique-se de que o sistema está funcionando com `/src/`
2. Faça backup se necessário (já tem!)
3. O servidor deve estar usando apenas arquivos de `/src/`

**VERIFICAÇÃO:**
- O servidor está usando: `from src.core.agent_logic import promo_agente` ✅
- As pastas antigas (`/agents/`, `/core/`) não estão sendo importadas ✅

---

## 📊 Espaço Liberado Estimado

- Pastas antigas: ~50KB
- Arquivos antigos: ~30KB
- Total: ~80KB

---

**Após a limpeza, seu projeto ficará mais organizado e profissional! 🎉**
