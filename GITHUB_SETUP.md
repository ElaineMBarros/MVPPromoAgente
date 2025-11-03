# 📝 Guia para Criar Repositório Privado no GitHub

## 🚀 Passos para Subir o PromoAgente para o GitHub

### 1. Criar Repositório no GitHub
1. Acesse [GitHub](https://github.com)
2. Clique no botão **"New"** (verde) ou no **"+"** no canto superior direito
3. Escolha **"New repository"**

### 2. Configurar o Repositório
- **Repository name**: `promoagente` (ou `PromoAgente`)
- **Description**: `🤖 Assistente Inteligente para Criação de Promoções Dinâmicas no Varejo B2B`
- **Visibility**: ✅ **Private** (importante!)
- **Initialize repository**: ❌ Deixe desmarcado (já temos os arquivos)
- Clique em **"Create repository"**

### 3. Conectar o Repositório Local ao GitHub
No terminal, dentro da pasta `PromoAgente_GitHub`, execute:

```bash
# Adicionar o remote do GitHub (substitua SEU_USUARIO pelo seu nome de usuário)
git remote add origin https://github.com/ElaineMBarros/promoagente.git

# Configurar a branch principal
git branch -M main

# Enviar os arquivos para o GitHub
git push -u origin main
```

### 4. Verificar Upload
1. Refresh na página do GitHub
2. Você deve ver todos os arquivos:
   - ✅ main.py
   - ✅ README.md
   - ✅ requirements.txt
   - ✅ .env.example
   - ✅ logo_gera.png
   - ✅ start.bat / start.sh
   - ✅ .gitignore

### 5. Configurar Colaboradores (Opcional)
1. Vá em **Settings** → **Manage access**
2. Clique em **"Invite a collaborator"**
3. Adicione pessoas da sua equipe

---

## 🔄 Depois de Criar o Repositório

### Para Clonar em Uma Nova Máquina:
```bash
git clone https://github.com/ElaineMBarros/promoagente.git
cd promoagente
cp .env.example .env
# Edite o .env com suas chaves
pip install -r requirements.txt
python main.py
```

### Para Fazer Updates:
```bash
git add .
git commit -m "Descrição da mudança"
git push origin main
```

### Para Baixar Updates:
```bash
git pull origin main
```

---

## 📂 Estrutura Final do Repositório

```
promoagente/                    # ← Nome do repositório no GitHub
├── .gitignore                 # Arquivos a ignorar
├── .env.example               # Configurações de exemplo
├── README.md                  # Documentação principal
├── main.py                    # Aplicação principal (1400+ linhas)
├── requirements.txt           # Dependências Python
├── logo_gera.png             # Logo da empresa
├── start.bat                 # Script Windows
├── start.sh                  # Script Linux/Mac
└── (arquivos gerados)
    ├── .env                  # Suas configurações (ignorado pelo Git)
    └── promoagente_local.db  # Database SQLite (ignorado pelo Git)
```

## ✅ Checklist de Verificação

- [ ] Repositório criado como **Private**
- [ ] Todos os arquivos foram enviados
- [ ] README.md está sendo exibido corretamente
- [ ] Arquivo .env.example está presente
- [ ] Logo está carregando
- [ ] Instruções de instalação estão claras

---

## 🎯 Próximos Passos Recomendados

1. **Teste de Instalação**: Clone o repo em outra pasta e teste a instalação
2. **Documentar Atualizações**: Use o README para manter histórico de versões
3. **Backup Regular**: Faça commits frequentes das mudanças
4. **Ambiente de Desenvolvimento**: Mantenha uma branch `dev` para testes

**Repositório está pronto para uso profissional! 🚀**