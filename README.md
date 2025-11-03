# 🤖 PromoAgente - Sistema de Criação Inteligente de Promoções B2B

**Assistente de IA para criação automática e inteligente de promoções dinâmicas no varejo B2B**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)
[![Agno](https://img.shields.io/badge/Agno-2.1.9-purple.svg)](https://github.com/agno-ai/agno)

## ✨ Características

- 🤖 **IA Conversacional**: Extrai informações através de diálogo natural
- 📊 **Validação Inteligente**: Valida promoções com regras de negócio B2B
- 📝 **Geração Automática**: Cria resumos profissionais e emails formatados
- 💾 **Persistência**: SQLite para armazenar histórico e estados
- 🔄 **Arquitetura Modular**: Agents especializados com Orchestrator
- 🎯 **Focado em B2B**: Templates específicos para varejo atacadista

---

## 📋 Índice

- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tipos de Promoções](#-tipos-de-promoções)
- [Desenvolvimento](#-desenvolvimento)

---

## 🏗️ Arquitetura

O PromoAgente utiliza uma arquitetura baseada em **agents especializados** orquestrados por um componente central:

```
┌─────────────────────────────────────────────────────────┐
│                    PromoAgente Local                     │
│                   (Agent Logic Layer)                    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │    Orchestrator      │
              │  (Coordination Layer) │
              └──────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Extractor   │ │  Validator   │ │  Summarizer  │
│    Agent     │ │    Agent     │ │    Agent     │
└──────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
              ┌──────────────────────┐
              │   Memory Manager     │
              │  (State Management)  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   SQLite Database    │
              │  - Promo States      │
              │  - Promotions        │
              │  - Messages          │
              └──────────────────────┘
```

### Componentes Principais

1. **ExtractorAgent**: Extrai informações estruturadas de texto natural
2. **ValidatorAgent**: Valida promoções com regras de negócio B2B
3. **SumarizerAgent**: Cria resumos e emails profissionais
4. **Orchestrator**: Coordena o fluxo entre agents
5. **MemoryManager**: Gerencia persistência de estados
6. **PromoState**: Modelo de dados da promoção

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.9 ou superior
- OpenAI API Key
- Git (opcional)

### Passo a Passo

1. **Clone o repositório** (ou baixe o ZIP)
```bash
git clone https://github.com/ElaineMBarros/promoagente.git
cd promoagente
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave da OpenAI:
```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
```

4. **Execute o sistema**
```bash
# Método 1: Python direto
python main.py

# Método 2: Script de inicialização
# Windows:
start.bat

# Linux/Mac:
chmod +x start.sh
./start.sh
```

5. **Acesse a aplicação**
- Interface: http://localhost:7000
- API Docs: http://localhost:7000/docs
- Status: http://localhost:7000/api/status

---

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão | Obrigatório |
|----------|-----------|--------|-------------|
| `OPENAI_API_KEY` | Chave da API OpenAI | - | ✅ Sim |
| `OPENAI_MODEL` | Modelo OpenAI | `gpt-4o-mini` | Não |
| `HOST` | Host do servidor | `localhost` | Não |
| `PORT` | Porta do servidor | `7000` | Não |
| `DEBUG` | Modo debug | `False` | Não |
| `ENVIRONMENT` | Ambiente | `development` | Não |
| `EMAIL_SENDER` | Email remetente | - | Para envio |
| `EMAIL_PASSWORD` | Senha do email | - | Para envio |
| `EMAIL_DESTINATION` | Email destino | `promocoes@gera.com` | Para envio |

### Configuração de Email (Opcional)

Para habilitar o envio automático de emails:

```env
EMAIL_SENDER=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app
EMAIL_DESTINATION=destino@empresa.com
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

---

## 💬 Uso

### Fluxo Básico

1. **Inicie uma conversa** com o agente
2. **Descreva a promoção** em linguagem natural
3. **Responda às perguntas** conforme solicitado
4. **Revise e confirme** a promoção gerada
5. **Envie por email** ou exporte

### Exemplo de Conversa

```
Usuário: Quero criar uma promoção progressiva de refrigerantes

Agente: ✅ Ótimo! Informações registradas:
• Mecânica: progressiva
• Categorias: refrigerantes

📊 Progresso: 25% completo

📝 Ainda preciso de:
• Título da promoção
• Descrição de como funciona
• Público-alvo/Segmentação
...

Usuário: Título: "Compre Mais, Ganhe Mais!"
Descrição: A cada 10 caixas, ganhe 5% de desconto. 
A partir de 20 caixas, 10% de desconto.
Público: Pequenos e médios varejistas
Período: 01/11/2025 a 30/11/2025

Agente: ✅ APROVADO
Promoção criada com sucesso!

# 🎯 Compre Mais, Ganhe Mais!
...
```

---

## 🔌 API Endpoints

### Chat

**POST** `/api/chat`
```json
{
  "message": "Quero criar uma promoção progressiva"
}
```

### Status do Sistema

**GET** `/api/status`
```json
{
  "system_ready": true,
  "openai": true,
  "orchestrator": true,
  "promotions_count": 15
}
```

### Promoções

**GET** `/api/promotions`
- Lista todas as promoções finalizadas

**GET** `/api/promotions/{promo_id}`
- Busca uma promoção específica

**GET** `/api/promotion-state/{session_id}`
- Obtém o estado atual de uma promoção em criação

**POST** `/api/promotion-state/{session_id}/validate`
- Valida uma promoção

**POST** `/api/promotion-state/{session_id}/summary`
- Cria um resumo da promoção

**POST** `/api/promotion-state/{session_id}/email`
- Gera o HTML do email

**POST** `/api/promotion-state/{session_id}/save`
- Salva uma promoção finalizada

**POST** `/api/promotion-state/{session_id}/send-email`
- Envia a promoção por email

**DELETE** `/api/promotion-state/{session_id}`
- Reseta o estado de uma promoção

---

## 📁 Estrutura do Projeto

```
PromoAgente_FINAL/
├── main.py                      # Ponto de entrada da aplicação
├── requirements.txt             # Dependências Python
├── .env                         # Configurações locais (não versionado)
├── .env.example                 # Template de configurações
├── README.md                    # Esta documentação
│
├── src/                         # Código-fonte principal
│   ├── app.py                   # Configuração FastAPI
│   │
│   ├── core/                    # Núcleo do sistema
│   │   ├── agent_logic.py       # Lógica principal integrada
│   │   ├── orchestrator.py      # Orquestração de agents
│   │   ├── promo_state.py       # Modelo de estado da promoção
│   │   ├── memory_manager.py    # Gerenciamento de memória
│   │   └── config.py            # Configurações do sistema
│   │
│   ├── agents/                  # Agents especializados
│   │   ├── extractor.py         # Extração de informações
│   │   ├── validator.py         # Validação de promoções
│   │   └── sumarizer.py         # Geração de resumos
│   │
│   ├── api/                     # Camada de API
│   │   ├── endpoints.py         # Endpoints REST
│   │   └── models.py            # Modelos Pydantic
│   │
│   └── services/                # Serviços auxiliares
│       ├── database.py          # Acesso ao SQLite
│       └── email_service.py     # Envio de emails
│
├── prompts/                     # Templates de prompts
│   ├── extraction.md            # Prompt de extração
│   ├── validation.md            # Prompt de validação
│   ├── summarization.md         # Prompt de sumarização
│   └── persona.md               # Persona do agente
│
└── frontend/                    # Interface React (opcional)
    └── src/
        ├── components/
        ├── services/
        └── styles/
```

---

## 🎯 Tipos de Promoções

O PromoAgente suporta diversos tipos de mecânicas promocionais:

### 1. 📈 Promoção Progressiva
Descontos que aumentam conforme o volume de compra
```
Exemplo: 10 caixas = 5%, 20 caixas = 10%, 30+ caixas = 15%
```

### 2. 🎁 Promoção Casada
Combos inteligentes de produtos complementares
```
Exemplo: Compre 1 detergente + 1 amaciante = 20% de desconto
```

### 3. 🏆 Sistema de Pontos
Acúmulo e resgate automático de pontos
```
Exemplo: A cada R$100 em compras = 10 pontos, 100 pontos = R$50 de desconto
```

### 4. ⚡ Promoção Relâmpago
Urgência com contadores regressivos e estoque limitado
```
Exemplo: 48h - 30% OFF em bebidas (estoque limitado)
```

### 5. 📊 Desconto Escalonado
Faixas automáticas por perfil de cliente
```
Exemplo: Bronze (0-5k/mês) = 5%, Prata (5-15k) = 10%, Ouro (15k+) = 15%
```

### 6. 💎 Fidelização VIP
Níveis de benefícios por histórico de compras
```
Exemplo: Clientes com 6+ meses = Frete grátis + 10% desconto
```

---

## 🛠️ Desenvolvimento

### Estrutura de Classes Principais

#### PromoState
```python
@dataclass
class PromoState:
    titulo: str
    mecanica: str
    descricao: str
    segmentacao: str
    periodo_inicio: str
    periodo_fim: str
    condicoes: str
    recompensas: str
    # ... campos opcionais
```

#### ExtractorAgent
```python
class ExtractorAgent:
    async def extract(self, text: str, state: PromoState) -> PromoState:
        # Extrai informações estruturadas do texto
```

#### ValidatorAgent
```python
class ValidatorAgent:
    async def validate(self, state: PromoState) -> str:
        # Valida com regras de negócio B2B
```

#### SumarizerAgent
```python
class SumarizerAgent:
    async def summarize(self, state: PromoState) -> str:
        # Cria resumo profissional
    
    async def create_email_body(self, state: PromoState) -> str:
        # Gera HTML para email
```

### Adicionando Novos Agents

1. Crie um novo arquivo em `src/agents/`
2. Herde de uma classe base ou implemente interface similar
3. Registre no `Orchestrator`
4. Atualize `src/agents/__init__.py`

### Customizando Prompts

Edite os arquivos em `/prompts/` para ajustar o comportamento dos agents:
- `extraction.md`: Lógica de extração
- `validation.md`: Regras de validação
- `summarization.md`: Formato de resumos
- `persona.md`: Personalidade do agente

---

## 🧪 Testando

### Teste Manual

```bash
# Inicie o servidor
python main.py

# Em outro terminal, teste o endpoint de chat
curl -X POST http://localhost:7000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quero criar uma promoção progressiva"}'
```

### Teste de Status

```bash
curl http://localhost:7000/api/status
```

### Scripts de Teste

O projeto inclui scripts de teste:
- `test_connection.py`: Testa conectividade
- `test_openai.py`: Testa integração OpenAI
- `test_agno.py`: Testa framework Agno

---

## 📊 Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

### `promo_states`
Armazena estados temporários de promoções em criação
```sql
- session_id (PK)
- promo_id
- state_data (JSON)
- status
- created_at
- updated_at
```

### `promotions`
Armazena promoções finalizadas
```sql
- id (PK)
- promo_id (UNIQUE)
- titulo
- mecanica
- descricao
- segmentacao
- periodo_inicio
- periodo_fim
- condicoes
- recompensas
- produtos (JSON)
- categorias (JSON)
- status
- created_at
- sent_at
```

### `messages`
Histórico de conversas
```sql
- id (PK)
- session_id
- user_message
- ai_response
- timestamp
```

---

## 🔐 Segurança

- ✅ API Keys armazenadas em variáveis de ambiente
- ✅ Validação de entrada em todos os endpoints
- ✅ Logs de auditoria para todas as operações
- ⚠️ **IMPORTANTE**: Nunca commite o arquivo `.env` no Git

---

## 🚀 Deploy em Produção

### Configurações Recomendadas

```env
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=7000
```

### Usando Docker (Futuro)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

---

## 📝 Changelog

### v2.0.0 (2025-10-29) - Refatoração Completa
- ✨ Arquitetura modular com Agents especializados
- ✨ Orchestrator para coordenação de fluxo
- ✨ PromoState para gerenciamento de estado
- ✨ MemoryManager com persistência SQLite
- ✨ Novos endpoints REST para CRUD de promoções
- ✨ Validação inteligente com IA
- ✨ Geração automática de emails HTML
- 🔧 Integração com Agno + OpenAI
- 📚 Documentação completa

### v1.0.0 (2025-10-27) - Versão Inicial
- 🎉 Lançamento inicial do PromoAgente

---

## 🤝 Contribuindo

Este é um projeto privado da Gera Sales Ecosystem. Para contribuições:

1. Entre em contato com a equipe de desenvolvimento
2. Siga os padrões de código estabelecidos
3. Documente todas as mudanças
4. Teste extensivamente antes de commit

---

## 📞 Suporte

- **Email**: promocoes@gera.com
- **Desenvolvido por**: Elaine Barros
- **Empresa**: Gera Sales Ecosystem
- **Versão**: 2.0.0

---

## 📄 Licença

Este projeto é propriedade privada da Gera Sales Ecosystem.
Todos os direitos reservados © 2025

---

## 🙏 Agradecimentos

- OpenAI pela API GPT-4
- Agno pelo framework de agents
- FastAPI pela excelente framework web
- Comunidade Python pelo suporte

---

**PromoAgente** - Transformando a criação de promoções com Inteligência Artificial 🤖✨
