"""
MemoryManager - Gerencia a persistência do estado de promoções
"""
import json
import logging
from typing import Optional, Dict
from src.core.promo_state import PromoState

logger = logging.getLogger(__name__)


class MemoryManager:
    """Gerencia o estado das promoções em memória e database"""
    
    def __init__(self, database):
        self.database = database
        self._cache: Dict[str, PromoState] = {}
    
    async def load(self, session_id: str) -> PromoState:
        """Carrega o estado de uma promoção pela session_id"""
        # Verifica cache primeiro
        if session_id in self._cache:
            logger.debug(f"PromoState carregado do cache: {session_id}")
            return self._cache[session_id]
        
        # Tenta carregar do banco
        try:
            state_data = await self.database.get_promo_state(session_id)
            if state_data:
                state = PromoState.from_dict(state_data)
                self._cache[session_id] = state
                logger.info(f"PromoState carregado do database: {session_id}")
                return state
        except Exception as e:
            logger.warning(f"Erro ao carregar PromoState do database: {e}")
        
        # Se não existe, cria um novo
        state = PromoState(session_id=session_id)
        self._cache[session_id] = state
        logger.info(f"Novo PromoState criado: {session_id}")
        return state
    
    async def save(self, state: PromoState) -> bool:
        """Salva o estado de uma promoção"""
        try:
            state.update_timestamp()
            self._cache[state.session_id] = state
            
            # Persiste no database
            await self.database.save_promo_state(state.session_id, state.to_dict())
            logger.info(f"PromoState salvo: {state.session_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar PromoState: {e}")
            return False
    
    async def delete(self, session_id: str) -> bool:
        """Remove o estado de uma promoção"""
        try:
            if session_id in self._cache:
                del self._cache[session_id]
            
            await self.database.delete_promo_state(session_id)
            logger.info(f"PromoState deletado: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar PromoState: {e}")
            return False
    
    async def list_all(self) -> list:
        """Lista todos os estados de promoções"""
        try:
            states = await self.database.list_all_promo_states()
            return states
        except Exception as e:
            logger.error(f"Erro ao listar PromoStates: {e}")
            return []
    
    def clear_cache(self):
        """Limpa o cache de memória"""
        self._cache.clear()
        logger.info("Cache de PromoStates limpo")
