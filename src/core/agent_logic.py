"""
Agent Logic - Lógica principal do PromoAgente integrada com Orchestrator
"""
import os
import sys
import logging
from typing import Optional, Dict
from datetime import datetime

import agno
from openai import AsyncOpenAI

from src.core.config import OPENAI_API_KEY, OPENAI_MODEL, logger
from src.core.config import EXTRACTION_PROMPT_PATH, VALIDATION_PROMPT_PATH, SUMMARIZATION_PROMPT_PATH
from src.services.database import LocalDatabase
from src.core.memory_manager import MemoryManager
from src.core.orchestrator import Orchestrator
from src.agents.extractor import ExtractorAgent
from src.agents.validator import ValidatorAgent
from src.agents.sumarizer import SumarizerAgent


class PromoAgenteLocal:
    """Sistema principal do PromoAgente com arquitetura integrada"""
    
    def __init__(self):
        self.openai_client: Optional[AsyncOpenAI] = None
        self.openai_version: Optional[str] = None
        
        # Components Agno (mantidos para compatibilidade)
        self.agno_agent = None
        self.agno_agent_os = None
        self.agno_ready: bool = False
        self.agno_status_error: Optional[str] = None
        
        # Database e Memory
        self.local_db = LocalDatabase()
        self.memory_manager: Optional[MemoryManager] = None
        
        # Agents especializados
        self.extractor: Optional[ExtractorAgent] = None
        self.validator: Optional[ValidatorAgent] = None
        self.summarizer: Optional[SumarizerAgent] = None
        
        # Orchestrator
        self.orchestrator: Optional[Orchestrator] = None
        
        # Status
        self.system_ready: bool = False

    async def initialize(self):
        """Inicializa todos os componentes do sistema"""
        logger.info("🚀 Inicializando PromoAgente Local...")
        
        # 1. Inicializa database
        await self.local_db.initialize()
        
        # 2. Inicializa OpenAI
        await self._init_openai()
        
        # 3. Inicializa Agno (opcional, para compatibilidade)
        await self._init_agno()
        
        # 4. Inicializa Memory Manager
        self.memory_manager = MemoryManager(self.local_db)
        logger.info("✅ MemoryManager inicializado")
        
        # 5. Inicializa Agents especializados
        if self.openai_client:
            self.extractor = ExtractorAgent(
                self.openai_client,
                OPENAI_MODEL,
                EXTRACTION_PROMPT_PATH
            )
            logger.info("✅ ExtractorAgent inicializado")
            
            self.validator = ValidatorAgent(
                self.openai_client,
                OPENAI_MODEL,
                VALIDATION_PROMPT_PATH
            )
            logger.info("✅ ValidatorAgent inicializado")
            
            self.summarizer = SumarizerAgent(
                self.openai_client,
                OPENAI_MODEL,
                SUMMARIZATION_PROMPT_PATH
            )
            logger.info("✅ SumarizerAgent inicializado")
            
            # 6. Inicializa Orchestrator
            self.orchestrator = Orchestrator(
                self.extractor,
                self.validator,
                self.summarizer,
                self.memory_manager
            )
            logger.info("✅ Orchestrator inicializado")
            
            self.system_ready = True
        else:
            logger.error("❌ OpenAI não inicializado - sistema não está pronto")
            self.system_ready = False
        
        logger.info("✅ PromoAgente Local inicializado com sucesso!")

    async def _init_openai(self) -> bool:
        """Inicializa cliente OpenAI"""
        try:
            from openai import __version__ as openai_version
            if not OPENAI_API_KEY:
                logger.warning("⚠️ OPENAI_API_KEY não definido.")
                return False
            self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            self.openai_version = openai_version
            logger.info("✅ Cliente OpenAI inicializado")
            return True
        except ImportError:
            logger.error("❌ SDK do OpenAI não encontrado.")
            return False
        except Exception as exc:
            logger.error(f"❌ Erro ao inicializar cliente OpenAI: {exc}")
            return False

    async def _init_agno(self):
        """Inicializa AgentOS (Agno) - mantido para compatibilidade"""
        try:
            from agno.agent import Agent
            from agno.db.sqlite import SqliteDb
            from agno.models.openai import OpenAIChat
            from agno.os import AgentOS
            from agno.tools.mcp import MCPTools

            self.agno_agent = Agent(
                name="PromoAgente",
                model=OpenAIChat(id=OPENAI_MODEL),
                db=SqliteDb(db_file="agno.db"),
                tools=[MCPTools(transport="streamable-http", url="https://docs.agno.com/mcp")],
                add_history_to_context=True,
                markdown=True,
            )
            self.agno_agent_os = AgentOS(agents=[self.agno_agent])
            self.agno_ready = True
            logger.info("✅ AgentOS (Agno) inicializado com sucesso!")
            return True
        except Exception as e:
            logger.warning(f"⚠️ AgentOS (Agno) não inicializado: {e}")
            self.agno_ready = False
            self.agno_status_error = str(e)
            return False

    async def chat_with_ai(self, message: str, session_id: Optional[str] = None) -> Dict:
        """
        Processa a mensagem do usuário através do Orchestrator
        
        Args:
            message: Mensagem do usuário
            session_id: ID da sessão (opcional, será criado se não fornecido)
            
        Returns:
            Dict com resposta e metadados
        """
        if not session_id:
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        if not self.system_ready or not self.orchestrator:
            logger.error("❌ Sistema não está pronto")
            return {
                "response": "Desculpe, o sistema não está disponível no momento. Tente novamente mais tarde.",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }

        try:
            # Usa o orchestrator para processar a mensagem
            result = await self.orchestrator.handle_message(message, session_id)
            
            # PROTEÇÃO: Verifica se result é válido antes de usar
            if not result or not isinstance(result, dict):
                result = {
                    "response": "Erro ao processar mensagem - resposta inválida",
                    "status": "error"
                }
            
            # Salva a interação no banco
            await self.local_db.save_message(
                session_id,
                message,
                result.get('response', '')
            )
            
            # Adiciona metadados
            result['session_id'] = session_id
            result['timestamp'] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro durante o chat: {e}", exc_info=True)
            return {
                "response": f"Ocorreu um erro ao processar sua mensagem: {e}",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }

    async def validate_promotion(self, session_id: str) -> Dict:
        """Valida uma promoção específica"""
        if not self.orchestrator:
            return {"error": "Orchestrator não inicializado", "is_valid": False}
        return await self.orchestrator.validate_promotion(session_id)

    async def create_summary(self, session_id: str) -> str:
        """Cria resumo de uma promoção"""
        if not self.orchestrator:
            return "Erro: Orchestrator não inicializado"
        return await self.orchestrator.create_summary(session_id)

    async def create_email(self, session_id: str) -> str:
        """Cria HTML de email para uma promoção"""
        if not self.orchestrator:
            return "<html><body>Erro: Orchestrator não inicializado</body></html>"
        return await self.orchestrator.create_email(session_id)

    async def get_promotion_state(self, session_id: str) -> Optional[Dict]:
        """Obtém o estado de uma promoção"""
        if not self.orchestrator:
            return None
        state = await self.orchestrator.get_state(session_id)
        return state.to_dict() if state else None

    async def reset_promotion(self, session_id: str) -> bool:
        """Reseta uma promoção"""
        if not self.orchestrator:
            return False
        return await self.orchestrator.reset_state(session_id)

    async def list_promotions(self) -> list:
        """Lista todas as promoções"""
        if not self.orchestrator:
            return []
        return await self.orchestrator.list_all_promotions()

    async def save_final_promotion(self, session_id: str) -> bool:
        """
        Salva uma promoção finalizada no banco de promoções
        
        Args:
            session_id: ID da sessão
            
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            state = await self.orchestrator.get_state(session_id)
            if state and state.is_complete():
                # Gera um promo_id se não existir
                if not state.promo_id:
                    state.promo_id = f"promo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                # Salva na tabela de promoções
                await self.local_db.save_promotion(state.to_dict())
                logger.info(f"Promoção salva: {state.promo_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao salvar promoção final: {e}")
            return False

    async def get_system_status(self) -> Dict:
        """Retorna o status completo do sistema"""
        messages_stored = await self.local_db.get_message_count()
        
        # Conta promoções
        try:
            promotions = await self.local_db.get_promotions(limit=1000)
            promo_count = len(promotions)
        except:
            promo_count = 0
        
        return {
            'system_ready': self.system_ready,
            'openai': self.openai_client is not None,
            'openai_version': self.openai_version,
            'openai_model': OPENAI_MODEL,
            'agno_framework': self.agno_ready,
            'agno_version': getattr(agno, '__version__', 'Unknown'),
            'agno_status_error': self.agno_status_error,
            'orchestrator': self.orchestrator is not None,
            'extractor': self.extractor is not None,
            'validator': self.validator is not None,
            'summarizer': self.summarizer is not None,
            'memory_manager': self.memory_manager is not None,
            'sqlite_db': True,
            'messages_stored': messages_stored,
            'promotions_count': promo_count,
            'python_version': sys.version,
            'environment': os.getenv('ENVIRONMENT', 'development'),
        }


# Singleton instance
promo_agente = PromoAgenteLocal()
