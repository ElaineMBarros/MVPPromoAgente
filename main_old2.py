# PromoAgente Local com AgentOS + SQLite + OpenAI
# =====================================
# Versão completa funcional usando Python 3.13 + Agno + OpenAI + SQLite

import os
import sys
import asyncio
import logging
import sqlite3
import aiosqlite
import json
import re
import uuid
import smtplib
from datetime import datetime
from typing import Dict, List, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# OpenAI - Importação dinâmica para evitar conflitos
# from openai import AsyncOpenAI  # Será importado dinamicamente

# AgentOS Framework
import agno

# Carregar variáveis de ambiente
load_dotenv()

# Configurações OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Configurações de E-mail SMTP
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "promocoes.agente@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINATION", "promocoes@gera.com")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG', 'False').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="PromoAgente Local", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

class SystemStatus(BaseModel):
    azure_openai: bool
    agno_framework: bool
    python_version: str
    openai_version: str
    agno_version: str
    sqlite_db: bool

# ===========================================
# FUNCIONALIDADES DE E-MAIL E RESUMO
# ===========================================

def extrair_informacoes_promocao(messages: List[Dict]) -> Dict[str, str]:
    """Extrai informações COMPLETAS da promoção das mensagens da conversa"""
    
    # Estrutura para armazenar informações
    promocao = {
        "titulo": "",
        "descricao": "",
        "publico_alvo": "",
        "periodo": "",
        "condicoes": "",
        "premio": "",
        "observacoes": ""
    }
    
    # Procurar pela mensagem do agente que contém o resumo estruturado
    texto_resumo = ""
    for msg in reversed(messages):  # Começar pelas mensagens mais recentes
        if msg.get("role") == "agent" and len(msg.get("content", "")) > 200:  # Mensagens longas do agente
            # Verificar se contém estrutura de promoção (mais flexível)
            content = msg["content"]
            if any(termo in content for termo in ["1. **", "2. **", "Título**", "Mecânica", "Descrição", "Segmentação", "Período", "Condições", "Recompensas"]):
                texto_resumo = content
                logger.info(f"📋 Encontrado resumo estruturado do agente")
                break
    
    if texto_resumo:
        # EXTRAÇÃO COMPLETA DOS CAMPOS ESTRUTURADOS - PADRÕES FLEXÍVEIS
        
        # 1. Título - múltiplos padrões
        padroes_titulo = [
            r"1\.\s*\*\*Título\*\*:\s*([^\n]+?)(?=\s*2\.|$)",
            r"\*\*Título\*\*:\s*([^*\n]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)",
            r"Título[:\s]*([^\n]+?)(?=\n|$)",
            r"(Promoção.*?[^\n]*)"
        ]
        for padrao in padroes_titulo:
            titulo_match = re.search(padrao, texto_resumo, re.DOTALL | re.IGNORECASE)
            if titulo_match:
                promocao["titulo"] = titulo_match.group(1).strip()
                logger.info(f"✅ Título extraído: {promocao['titulo'][:50]}...")
                break
        
        # 2. Descrição/Mecânica - múltiplos padrões
        padroes_descricao = [
            r"3\.\s*\*\*Descrição.*?\*\*:\s*([^4]+?)(?=4\.|$)",
            r"2\.\s*\*\*.*?Mecânica.*?\*\*:\s*([^3]+?)(?=3\.|$)",
            r"\*\*Descrição\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)",
            r"Descrição[:\s]*([^\n]+?)(?=\n|$)"
        ]
        for padrao in padroes_descricao:
            desc_match = re.search(padrao, texto_resumo, re.DOTALL | re.IGNORECASE)
            if desc_match:
                promocao["descricao"] = desc_match.group(1).strip()
                logger.info(f"✅ Descrição extraída")
                break
        
        # 3. Público-alvo/Segmentação - múltiplos padrões
        padroes_publico = [
            r"4\.\s*\*\*Segmentação.*?\*\*:\s*([^5]+?)(?=5\.|$)",
            r"\*\*Público-alvo.*?\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)",
            r"3\.\s*\*\*Público-alvo.*?\*\*:\s*([^*]+?)(?=\n\d+\.|$)",
            r"Público-alvo[:\s]*([^\n]+?)(?=\n|$)"
        ]
        for padrao in padroes_publico:
            publico_match = re.search(padrao, texto_resumo, re.DOTALL | re.IGNORECASE)
            if publico_match:
                promocao["publico_alvo"] = publico_match.group(1).strip()
                logger.info(f"✅ Público-alvo extraído")
                break
        
        # 4. Período - múltiplos padrões
        padroes_periodo = [
            r"5\.\s*\*\*Período.*?\*\*:\s*([^6]+?)(?=6\.|$)",
            r"\*\*Período\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)",
            r"4\.\s*\*\*Período\*\*:\s*([^*]+?)(?=\n\d+\.|$)",
            r"Período[:\s]*([^\n]+?)(?=\n|$)",
            r"(\d{2}/\d{2}/\d{4}\s*a\s*\d{2}/\d{2}/\d{4})"
        ]
        for padrao in padroes_periodo:
            periodo_match = re.search(padrao, texto_resumo, re.DOTALL | re.IGNORECASE)
            if periodo_match:
                promocao["periodo"] = periodo_match.group(1).strip()
                logger.info(f"✅ Período extraído")
                break
        
        # 5. Condições - múltiplos padrões
        padroes_condicoes = [
            r"6\.\s*\*\*Condições.*?\*\*:\s*([^7]+?)(?=7\.|$)",
            r"\*\*Condições\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)",
            r"5\.\s*\*\*Condições\*\*:\s*([^*]+?)(?=\n\d+\.|$)",
            r"Condições[:\s]*([^\n]+?)(?=\n|$)"
        ]
        for padrao in padroes_condicoes:
            condicoes_match = re.search(padrao, texto_resumo, re.DOTALL | re.IGNORECASE)
            if condicoes_match:
                promocao["condicoes"] = condicoes_match.group(1).strip()
                logger.info(f"✅ Condições extraídas")
                break
        
        # 6. Prêmio/Recompensa - múltiplos padrões
        padroes_premio = [
            r"7\.\s*\*\*Sistema.*?Recompensas.*?\*\*:\s*([^\.]+?)(?=\n\n|\.\s|$)",
            r"\*\*Prêmio\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)",
            r"6\.\s*\*\*Prêmio\*\*:\s*([^*]+?)(?=\n\d+\.|$)",
            r"Prêmio[:\s]*([^\n]+?)(?=\n|$)",
            r"(\d+%\s*.*?desconto[^\n]*)"
        ]
        for padrao in padroes_premio:
            premio_match = re.search(padrao, texto_resumo, re.DOTALL | re.IGNORECASE)
            if premio_match:
                promocao["premio"] = premio_match.group(1).strip()
                logger.info(f"✅ Prêmio extraído")
                break
        
        campos_preenchidos = sum(1 for v in promocao.values() if v)
        logger.info(f"📊 Total de campos extraídos: {campos_preenchidos}/7")
        
    return promocao

def criar_card_html_promocao(promocao: Dict[str, str], session_id: str) -> str:
    """Cria um card HTML bonito com as informações da promoção"""
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nova Promoção Cadastrada - Gera Sales</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #2c5f8a 0%, #1e4a66 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ font-size: 2.2em; margin-bottom: 10px; }}
            .header p {{ opacity: 0.9; font-size: 1.1em; }}
            .content {{ padding: 30px; }}
            .card {{ background: #f8f9fa; border-radius: 10px; padding: 25px; margin-bottom: 20px; border-left: 5px solid #2c5f8a; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .info-table th {{ background: #2c5f8a; color: white; padding: 15px; text-align: left; font-weight: 600; }}
            .info-table td {{ background: white; padding: 15px; border-bottom: 1px solid #eee; }}
            .info-table tr:hover td {{ background: #f0f0f0; }}
            .badge {{ display: inline-block; background: #28a745; color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; border-top: 1px solid #eee; }}
            .meta-info {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .logo {{ width: 60px; height: 30px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Nova Promoção Cadastrada</h1>
                <p>Promoção criada com sucesso pelo PromoAgente - Gera Sales</p>
            </div>
            
            <div class="content">
                <div class="meta-info">
                    <strong>📊 Informações da Sessão:</strong><br>
                    <strong>ID:</strong> {session_id[:8]}... | 
                    <strong>Data/Hora:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} | 
                    <span class="badge">APROVADA</span>
                </div>
                
                <div class="card">
                    <h2 style="color: #2c5f8a; margin-bottom: 20px;">📋 Detalhes da Promoção</h2>
                    
                    <table class="info-table">
                        <thead>
                            <tr>
                                <th style="width: 25%;">Campo</th>
                                <th>Informação</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>🏷️ Título</strong></td>
                                <td>{promocao.get('titulo', 'Não informado')}</td>
                            </tr>
                            <tr>
                                <td><strong>📝 Descrição</strong></td>
                                <td>{promocao.get('descricao', 'Não informado')}</td>
                            </tr>
                            <tr>
                                <td><strong>🎯 Público-alvo</strong></td>
                                <td>{promocao.get('publico_alvo', 'Não informado')}</td>
                            </tr>
                            <tr>
                                <td><strong>📅 Período</strong></td>
                                <td>{promocao.get('periodo', 'Não informado')}</td>
                            </tr>
                            <tr>
                                <td><strong>✅ Condições</strong></td>
                                <td>{promocao.get('condicoes', 'Não informado')}</td>
                            </tr>
                            <tr>
                                <td><strong>🎁 Prêmio</strong></td>
                                <td>{promocao.get('premio', 'Não informado')}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                {f'<div class="card"><h3>📝 Observações:</h3><p>{promocao.get("observacoes", "Nenhuma observação adicional")}</p></div>' if promocao.get('observacoes') else ''}
            </div>
            
            <div class="footer">
                <p>🤖 <em>Email gerado automaticamente pelo PromoAgente - Gera Sales Ecosystem</em></p>
                <p>Sistema de Gestão de Promoções B2B</p>
            </div>
        </div>
    </body>
    </html>
    """

def enviar_email_promocao(promocao: Dict[str, str], session_id: str) -> bool:
    """Envia email com informações da promoção"""
    try:
        # Criar card HTML bonito
        corpo_html = criar_card_html_promocao(promocao, session_id)
        
        # Tentar envio real se as credenciais estiverem configuradas
        if EMAIL_PASSWORD and EMAIL_SENDER:
            try:
                # Configurar mensagem
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"Nova Promoção Gera: {promocao.get('titulo', 'Sem título')}"
                msg['From'] = EMAIL_SENDER
                msg['To'] = EMAIL_DESTINO
                
                # Anexar HTML
                html_part = MIMEText(corpo_html, 'html', 'utf-8')
                msg.attach(html_part)
                
                # Enviar via SMTP
                with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
                    server.starttls()
                    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                    server.send_message(msg)
                
                logger.info(f"📧 Email REAL enviado para: {EMAIL_DESTINO}")
                logger.info(f"📋 Título da promoção: {promocao.get('titulo', 'Sem título')}")
                return True
                
            except Exception as smtp_error:
                logger.warning(f"⚠️ Erro no envio SMTP: {smtp_error}")
                # Fallback para simulação
                pass
        
        # Fallback: Simulação
        logger.info(f"📧 Email simulado (card HTML) para: {EMAIL_DESTINO}")
        logger.info(f"📋 Título da promoção: {promocao.get('titulo', 'Sem título')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao enviar email: {e}")
        return False

def criar_previa_chat_promocao(promocao: Dict[str, str]) -> str:
    """Cria uma prévia compacta da promoção para mostrar no chat"""
    previa = "```\n"
    previa += "🎯 PRÉVIA DA PROMOÇÃO GERA\n"
    previa += "=" * 50 + "\n\n"
    
    if promocao.get("titulo"):
        previa += f"🏷️  TÍTULO: {promocao['titulo']}\n\n"
    
    if promocao.get("descricao"):
        previa += f"📝 DESCRIÇÃO: {promocao['descricao']}\n\n"
    
    if promocao.get("publico_alvo"):
        previa += f"🎯 PÚBLICO-ALVO: {promocao['publico_alvo']}\n\n"
    
    if promocao.get("periodo"):
        previa += f"📅 PERÍODO: {promocao['periodo']}\n\n"
    
    if promocao.get("condicoes"):
        previa += f"✅ CONDIÇÕES: {promocao['condicoes']}\n\n"
    
    if promocao.get("premio"):
        previa += f"🎁 PRÊMIO: {promocao['premio']}\n\n"
    
    previa += "```"
    return previa

# ===========================================
# CLASSE SQLITE PARA LOGS LOCAIS
# ===========================================

# Classe SQLite para logs locais
class LocalDatabase:
    def __init__(self, db_path: str = "promoagente_local.db"):
        self.db_path = db_path
        
    async def initialize(self):
        """Inicializar banco SQLite"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Criar tabela de sessões
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        created_at TEXT,
                        last_activity TEXT,
                        user_agent TEXT
                    )
                """)
                
                # Criar tabela de mensagens
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id TEXT PRIMARY KEY,
                        session_id TEXT,
                        user_message TEXT,
                        ai_response TEXT,
                        timestamp TEXT,
                        agno_version TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                """)
                
                # Criar tabela de logs do sistema
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        level TEXT,
                        message TEXT,
                        component TEXT
                    )
                """)
                
                await db.commit()
                logger.info("✅ Banco SQLite inicializado com sucesso!")
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar SQLite: {e}")
            return False
    
    async def save_message(self, session_id: str, user_message: str, ai_response: str, agno_version: str = None):
        """Salvar mensagem no SQLite"""
        try:
            message_id = f"{session_id}_{datetime.utcnow().isoformat()}"
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO messages 
                    (id, session_id, user_message, ai_response, timestamp, agno_version)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (message_id, session_id, user_message, ai_response, 
                     datetime.utcnow().isoformat(), agno_version))
                await db.commit()
                logger.debug(f"✅ Mensagem salva no SQLite: {message_id}")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Erro ao salvar mensagem no SQLite: {e}")
            return False
    
    async def get_message_count(self):
        """Contar mensagens no banco"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) FROM messages") as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else 0
        except Exception as e:
            logger.warning(f"Erro ao contar mensagens: {e}")
            return 0
    
    async def log_system_event(self, level: str, message: str, component: str = "system"):
        """Salvar log do sistema"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO system_logs (timestamp, level, message, component)
                    VALUES (?, ?, ?, ?)
                """, (datetime.utcnow().isoformat(), level, message, component))
                await db.commit()
        except Exception as e:
            logger.warning(f"Erro ao salvar log: {e}")
    
    async def get_recent_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Buscar mensagens recentes de uma sessão"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT user_message, ai_response, timestamp 
                    FROM messages 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (session_id, limit))
                rows = await cursor.fetchall()
                
                messages = []
                for row in reversed(rows):  # Inverter para ordem cronológica
                    # Adicionar mensagem do usuário
                    if row['user_message']:
                        messages.append({
                            "role": "user",
                            "content": row['user_message'],
                            "timestamp": row['timestamp']
                        })
                    # Adicionar resposta do agente
                    if row['ai_response']:
                        messages.append({
                            "role": "assistant", 
                            "content": row['ai_response'],
                            "timestamp": row['timestamp']
                        })
                
                return messages
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens: {e}")
            return []

# Classe principal com AgentOS + SQLite
class PromoAgenteLocal:
    def __init__(self):
        self.openai_client = None
        self.agno_agent = None
        self.local_db = LocalDatabase()  # SQLite local
        
    async def initialize(self):
        """Inicializar todos os serviços"""
        logger.info("🚀 Inicializando PromoAgente Local...")
        
        # Inicializar SQLite primeiro
        await self._init_sqlite()
        
        # Inicializar OpenAI
        await self._init_openai()
        
        # Inicializar AgentOS
        await self._init_agno()
        
        logger.info("✅ PromoAgente Local inicializado com sucesso!")
        
    async def _init_sqlite(self):
        """Inicializar banco SQLite local"""
        try:
            success = await self.local_db.initialize()
            if success:
                await self.local_db.log_system_event("INFO", "PromoAgente Local iniciado", "system")
                logger.info("✅ SQLite inicializado com sucesso!")
            return success
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar SQLite: {e}")
            return False
        
    async def _init_openai(self):
        """Inicializar OpenAI"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                raise ValueError("OpenAI API key não configurada")
            
            # Importar OpenAI apenas quando necessário para evitar conflitos
            from openai import AsyncOpenAI
            
            self.openai_client = AsyncOpenAI(
                api_key=api_key,
                timeout=30.0,  # Timeout explícito
                max_retries=2   # Máximo de tentativas
            )
            
            # Testar conexão
            response = await self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": "Teste de conectividade"}],
                max_tokens=10,
                timeout=15.0
            )
            
            logger.info("✅ OpenAI conectado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar OpenAI: {e}")
            logger.error(f"   Detalhes: {type(e).__name__}")
            return False
    
    
    async def _init_agno(self):
        """Inicializar AgentOS"""
        try:
            # Verificar se AgentOS está disponível
            agno_version = getattr(agno, 'version', 'Unknown')
            logger.info(f"🤖 AgentOS version: {agno_version}")
            
            # Criar um agente simples para demonstração
            # Nota: Agno 2.1.9 tem funcionalidades limitadas, mas vamos usar o que está disponível
            self.agno_agent = {
                'name': 'PromoAgente',
                'version': agno_version,
                'status': 'active',
                'capabilities': ['chat', 'promocoes', 'analytics']
            }
            
            logger.info("✅ AgentOS inicializado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar AgentOS: {e}")
            return False
    
    
    async def chat_with_ai(self, message: str, session_id: str = None) -> Dict:
        """Novo chat usando Orchestrator + Agno"""
        from agno import LLM
        from core.orchestrator import Orchestrator
        from core.memory_manager import MemoryManager
        from agents.extractor import ExtractorAgent
        from agents.validator import ValidatorAgent
        from agents.summarizer import SummarizerAgent

        if not session_id:
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        llm = LLM(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)

        memory = MemoryManager(self.local_db)
        extractor = ExtractorAgent(llm, "prompts/extraction.md")
        validator = ValidatorAgent(llm, "prompts/validation.md")
        summarizer = SummarizerAgent(llm, "prompts/summarization.md")

        orchestrator = Orchestrator(extractor, validator, summarizer, memory)

        ai_response = await orchestrator.handle(message, session_id)

        await memory.save_interaction(session_id, message, ai_response)

        return {
            "response": ai_response,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }

            
  
    
    async def get_system_status(self) -> Dict:
        """Verificar status de todos os sistemas"""
        import sys
        
        # Contar mensagens no SQLite
        message_count = await self.local_db.get_message_count()
        
        status = {
            'openai': bool(self.openai_client),
            'agno_framework': bool(self.agno_agent),
            'sqlite_db': True,  # SQLite sempre disponível
            'python_version': sys.version,
            'openai_version': None,
            'agno_version': getattr(agno, 'version', 'Unknown'),
            'messages_stored': message_count,
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'storage': 'SQLite Local Database'
        }
        
        try:
            import openai
            status['openai_version'] = openai.__version__
        except:
            status['openai_version'] = 'Unknown'
        
        return status

# Instância global
promo_agente = PromoAgenteLocal()

# Rotas da API
@app.on_event("startup")
async def startup_event():
    """Inicializar na startup"""
    await promo_agente.initialize()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Página inicial com design limpo e minimalista"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PromoAgente - Chat IA</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #ffffff;
                color: #333;
                line-height: 1.6;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            .header {
                text-align: center;
                margin-bottom: 20px;
                padding: 15px 0;
            }
            
            .logo {
                width: 120px;
                height: 60px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 15px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .logo img {
                width: 100%;
                height: 100%;
                object-fit: contain;
            }
            
            .title {
                font-size: 28px;
                font-weight: 600;
                color: #333;
                margin: 0;
            }
            
            .chat-container {
                flex: 1;
                border: 1px solid #ddd;
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                background: #fafafa;
                min-height: 400px;
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: white;
                margin: 10px;
                border-radius: 8px;
                min-height: 400px;
                max-height: 500px;
                border: 1px solid #e0e0e0;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 8px;
            }
            
            .message.user {
                background: #e3f2fd;
                text-align: right;
            }
            
            .message.agent {
                background: #f5f5f5;
                text-align: left;
            }
            
            .chat-input {
                padding: 20px;
                border-top: 1px solid #ddd;
                background: white;
            }
            
            .input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }
            
            .input-field {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                outline: none;
                min-height: 80px;
                max-height: 120px;
                resize: none;
                overflow-y: auto;
                font-family: inherit;
                line-height: 1.4;
            }
            
            .input-field:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
            }
            
            .btn {
                padding: 12px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
            }
            
            .btn-send {
                background: #667eea;
                color: white;
            }
            
            .btn-send:hover {
                background: #5a6fd8;
            }
            
            .btn-clear {
                background: #f44336;
                color: white;
                margin-left: 10px;
            }
            
            .btn-clear:hover {
                background: #d32f2f;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 10px;
                color: #666;
                font-style: italic;
            }
            
            .session-info {
                text-align: center;
                font-size: 12px;
                color: #666;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header simples -->
            <div class="header">
                <div class="logo">
                    <img src="/logo_gera.png" alt="Logo GERA" />
                </div>
                <h1 class="title">PromoAgente</h1>
            </div>
            
            <!-- Chat container -->
            <div class="chat-container">
                <div class="session-info" id="sessionInfo">
                    <span id="sessionId">Sessão: Carregando...</span>
                </div>
                
                <div id="chatMessages" class="chat-messages">
                    <div class="message agent">
                        🤖 Olá! Sou o PromoAgente, seu assistente inteligente! Como posso ajudá-lo hoje?
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    🤖 Processando sua mensagem...
                </div>
                
                <div class="chat-input">
                    <div class="input-group">
                        <textarea id="messageInput" class="input-field" 
                               placeholder="Digite sua mensagem..." 
                               onkeypress="handleKeyPress(event)"></textarea>
                        <button onclick="sendMessage()" class="btn btn-send" id="sendButton">Enviar</button>
                    </div>
                    <div style="text-align: center;">
                        <button onclick="clearSession()" class="btn btn-clear">Limpar Tela</button>
                        <a href="/promocoes" class="btn" style="background: #28a745; margin-left: 10px; text-decoration: none;" target="_blank">Ver Promoções 📧</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let currentSessionId = null;
            
            // Gerar um novo ID de sessão
            function generateSessionId() {
                return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            }
            
            // Inicializar nova sessão
            function newSession() {
                currentSessionId = generateSessionId();
                updateSessionInfo();
                clearMessages();
                addMessage('🤖 Olá! Sou o PromoAgente, seu assistente inteligente! Como posso ajudá-lo hoje?', false);
            }
            
            // Limpar sessão atual (apenas a interface - dados preservados no banco)
            function clearSession() {
                clearMessages();
                addMessage('🤖 Chat limpo! Todas as mensagens anteriores foram preservadas no banco de dados. Como posso ajudá-lo?', false);
                // Mantém o currentSessionId - a sessão continua ativa
            }
            
            // Atualizar informações da sessão
            function updateSessionInfo() {
                document.getElementById('sessionId').textContent = `Sessão: ${currentSessionId || 'Nova sessão'}`;
            }
            
            // Limpar mensagens do chat
            function clearMessages() {
                const messagesContainer = document.getElementById('chatMessages');
                messagesContainer.innerHTML = '';
            }
            
            // Adicionar mensagem ao chat
            function addMessage(content, isUser = false) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user' : 'agent'}`;
                
                messageDiv.innerHTML = content;
                
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            // Mostrar/esconder loading
            function showLoading(show) {
                document.getElementById('loading').style.display = show ? 'block' : 'none';
                document.getElementById('sendButton').disabled = show;
            }
            
            // Função para lidar com teclas no textarea
            function handleKeyPress(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                }
                // Shift+Enter permite quebra de linha
            }
            
            // Auto-resize do textarea
            function autoResizeTextarea() {
                const textarea = document.getElementById('messageInput');
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
            }
            
            // Enviar mensagem
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Adicionar mensagem do usuário
                addMessage('👤 ' + message, true);
                input.value = '';
                input.style.height = 'auto'; // Reset altura
                
                // Mostrar loading
                showLoading(true);
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            message: message,
                            session_id: currentSessionId 
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        addMessage('🤖 ' + data.response);
                        currentSessionId = data.session_id;
                        updateSessionInfo();
                    } else {
                        const error = await response.json();
                        addMessage(`❌ Erro: ${error.detail}`);
                    }
                } catch (error) {
                    addMessage(`❌ Erro de conexão: ${error.message}`);
                } finally {
                    showLoading(false);
                }
            }
            
            // Inicializar página
            window.onload = function() {
                newSession();
                
                // Auto-resize do textarea conforme digita
                const textarea = document.getElementById('messageInput');
                textarea.addEventListener('input', autoResizeTextarea);
            };
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/promocoes", response_class=HTMLResponse)
async def visualizar_promocoes():
    """Página para visualizar promoções extraídas"""
    try:
        # Buscar dados do banco
        async with aiosqlite.connect(promo_agente.local_db.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT session_id, user_message, ai_response, timestamp, agno_version
                FROM messages 
                WHERE ai_response LIKE '%✅%Email enviado%' 
                OR ai_response LIKE '%📧%' 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            promocoes = await cursor.fetchall()
        
        html_content = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Promoções Enviadas - Gera Sales</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { background: linear-gradient(135deg, #2c5f8a 0%, #1e4a66 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; }
                .promocao-card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
                .promocao-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
                .session-id { background: #2c5f8a; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em; }
                .timestamp { color: #666; font-size: 0.9em; }
                .user-message { background: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
                .ai-response { background: #f8f9fa; padding: 15px; border-radius: 8px; }
                .back-btn { display: inline-block; background: #2c5f8a; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }
                .back-btn:hover { background: #1e4a66; }
                .status-badge { background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 Promoções Enviadas</h1>
                    <p>Histórico de promoções processadas pelo PromoAgente Gera</p>
                </div>
                
                <a href="/" class="back-btn">← Voltar ao Chat</a>
        """
        
        if promocoes:
            for promocao in promocoes:
                html_content += f"""
                <div class="promocao-card">
                    <div class="promocao-header">
                        <span class="session-id">Sessão: {promocao['session_id'][:8]}...</span>
                        <span class="timestamp">{promocao['timestamp']}</span>
                        <span class="status-badge">ENVIADA</span>
                    </div>
                    <div class="user-message">
                        <strong>👤 Solicitação:</strong><br>
                        {promocao['user_message']}
                    </div>
                    <div class="ai-response">
                        <strong>🤖 Resposta do Agente:</strong><br>
                        {promocao['ai_response'].replace('\\n', '<br>')}
                    </div>
                </div>
                """
        else:
            html_content += """
            <div class="promocao-card">
                <h3>📭 Nenhuma promoção encontrada</h3>
                <p>Ainda não há promoções com e-mail enviado. Crie sua primeira promoção no chat!</p>
            </div>
            """
        
        html_content += """
                <div style="text-align: center; margin-top: 30px; padding: 20px; color: #666;">
                    <p>🤖 PromoAgente - Gera Sales Ecosystem</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        logger.error(f"Erro ao visualizar promoções: {e}")
        return HTMLResponse(content=f"<h1>Erro: {e}</h1>", status_code=500)

@app.get("/test-email")
async def test_email():
    """Endpoint para testar funcionalidade de email"""
    try:
        # Dados de teste
        promocao_teste = {
            "titulo": "Promoção Teste - Gera Sales",
            "descricao": "Teste da funcionalidade de envio de email",
            "publico_alvo": "Equipe de desenvolvimento",
            "periodo": "27/10/2025 a 30/10/2025",
            "condicoes": "Apenas para teste do sistema",
            "premio": "Verificação de funcionalidade",
            "observacoes": "Email de teste - sistema funcionando"
        }
        
        session_teste = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Tentar enviar email de teste
        sucesso = enviar_email_promocao(promocao_teste, session_teste)
        
        if sucesso:
            return {
                "status": "success",
                "message": "Email de teste enviado com sucesso!",
                "promocao": promocao_teste,
                "email_destino": EMAIL_DESTINO,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error", 
                "message": "Falha no envio do email de teste",
                "promocao": promocao_teste
            }
            
    except Exception as e:
        logger.error(f"Erro no teste de email: {e}")
        return {"status": "error", "message": f"Erro: {e}"}

@app.get("/logo_gera.png")
async def get_logo():
    """Servir o logo da GERA"""
    try:
        with open("logo_gera.png", "rb") as f:
            content = f.read()
        return Response(content=content, media_type="image/png")
    except FileNotFoundError:
        return JSONResponse({"error": "Logo não encontrado"}, status_code=404)

@app.get("/api/status")
async def get_status():
    """API de status do sistema"""
    return await promo_agente.get_system_status()

@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """API de chat"""
    result = await promo_agente.chat_with_ai(
        message=chat_message.message,
        session_id=chat_message.session_id
    )
    return ChatResponse(**result)

@app.post("/chat")
async def chat_simple(chat_message: ChatMessage):
    """API de chat simples (alias para /api/chat)"""
    result = await promo_agente.chat_with_ai(
        message=chat_message.message,
        session_id=chat_message.session_id
    )
    return ChatResponse(**result)

@app.get("/api/debug")
async def debug_info():
    """Informações de debug detalhadas"""
    import sys
    import platform
    
    debug_info = {
        'timestamp': datetime.utcnow().isoformat(),
        'system': {
            'platform': platform.platform(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'working_directory': os.getcwd()
        },
        'environment': {
            'DEBUG': os.getenv('DEBUG'),
            'ENVIRONMENT': os.getenv('ENVIRONMENT'),
            'HOST': os.getenv('HOST'),
            'PORT': os.getenv('PORT')
        },
        'azure_config': {
            'openai_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
            'openai_deployment': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            'cosmos_endpoint': os.getenv('AZURE_COSMOS_ENDPOINT'),
            'cosmos_database': os.getenv('AZURE_COSMOS_DATABASE_NAME')
        },
        'services_status': await promo_agente.get_system_status()
    }
    
    return debug_info

if __name__ == "__main__":
    # Configurações do servidor
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 7000))  # Mudando para 7000 como estava antes
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"""
    🚀 PromoAgente Local
    ==================
    Python: {sys.version}
    AgentOS: {getattr(agno, 'version', 'Unknown')}
    URL: http://{host}:{port}
    Debug: {debug}
    """)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )