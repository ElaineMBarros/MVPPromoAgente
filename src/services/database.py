import aiosqlite
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LocalDatabase:
    def __init__(self, db_path: str = "promoagente_local.db"):
        self.db_path = db_path

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Tabela de sessões
            await db.execute(
                '''CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    last_activity TEXT,
                    user_agent TEXT
                );'''
            )
            
            # Tabela de mensagens
            await db.execute(
                '''CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    user_message TEXT,
                    ai_response TEXT,
                    timestamp TEXT,
                    agno_version TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                );'''
            )
            
            # Tabela de logs do sistema
            await db.execute(
                '''CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    level TEXT,
                    message TEXT,
                    component TEXT
                );'''
            )
            
            # NOVA: Tabela de estados de promoções
            await db.execute(
                '''CREATE TABLE IF NOT EXISTS promo_states (
                    session_id TEXT PRIMARY KEY,
                    promo_id TEXT,
                    state_data TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    status TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                );'''
            )
            
            # NOVA: Tabela de promoções finalizadas
            await db.execute(
                '''CREATE TABLE IF NOT EXISTS promotions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    promo_id TEXT UNIQUE,
                    session_id TEXT,
                    titulo TEXT,
                    mecanica TEXT,
                    descricao TEXT,
                    segmentacao TEXT,
                    periodo_inicio TEXT,
                    periodo_fim TEXT,
                    condicoes TEXT,
                    recompensas TEXT,
                    produtos TEXT,
                    categorias TEXT,
                    volume_minimo TEXT,
                    desconto_percentual TEXT,
                    status TEXT,
                    created_at TEXT,
                    sent_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                );'''
            )
            
            await db.commit()
        logger.info("✅ SQLite inicializado com sucesso!")
        return True

    async def get_message_count(self) -> int:
        """Retorna total de mensagens registradas para monitoramento de saúde."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) FROM messages") as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as exc:
            logger.warning(f"Erro ao contar mensagens no SQLite: {exc}")
            return 0

    async def get_recent_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Buscar mensagens recentes de uma sessão."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT user_message, ai_response, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (session_id, limit)
                )
                rows = await cursor.fetchall()
                messages = []
                for row in reversed(rows):  # Inverter para ordem cronológica
                    # Garante que sempre adiciona dict válido, nunca None
                    if row and row['user_message']:
                        messages.append({"role": "user", "content": str(row['user_message'])})
                    if row and row['ai_response']:
                        messages.append({"role": "assistant", "content": str(row['ai_response']), "timestamp": str(row['timestamp'])})
                return messages  # Sempre retorna lista, mesmo que vazia
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens: {e}")
            return []

    async def save_message(self, session_id: str, user_message: str, ai_response: str):
        """Salva uma única interação de chat no banco de dados."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO messages (id, session_id, user_message, ai_response, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (f"msg_{datetime.utcnow().timestamp()}", session_id, user_message, ai_response, datetime.utcnow().isoformat())
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
    
    # ========== MÉTODOS PARA PROMO_STATES ==========
    
    async def save_promo_state(self, session_id: str, state_dict: Dict) -> bool:
        """Salva ou atualiza o estado de uma promoção"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                state_json = json.dumps(state_dict, ensure_ascii=False)
                await db.execute(
                    """INSERT OR REPLACE INTO promo_states 
                       (session_id, promo_id, state_data, created_at, updated_at, status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        session_id,
                        state_dict.get('promo_id'),
                        state_json,
                        state_dict.get('created_at', datetime.utcnow().isoformat()),
                        state_dict.get('updated_at', datetime.utcnow().isoformat()),
                        state_dict.get('status', 'draft')
                    )
                )
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar promo_state: {e}")
            return False
    
    async def get_promo_state(self, session_id: str) -> Optional[Dict]:
        """Recupera o estado de uma promoção"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT state_data FROM promo_states WHERE session_id = ?",
                    (session_id,)
                )
                row = await cursor.fetchone()
                if row:
                    return json.loads(row['state_data'])
                return None
        except Exception as e:
            logger.error(f"Erro ao recuperar promo_state: {e}")
            return None
    
    async def delete_promo_state(self, session_id: str) -> bool:
        """Remove o estado de uma promoção"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM promo_states WHERE session_id = ?",
                    (session_id,)
                )
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar promo_state: {e}")
            return False
    
    async def list_all_promo_states(self) -> List[Dict]:
        """Lista todos os estados de promoções"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT state_data FROM promo_states ORDER BY updated_at DESC"
                )
                rows = await cursor.fetchall()
                return [json.loads(row['state_data']) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao listar promo_states: {e}")
            return []
    
    # ========== MÉTODOS PARA PROMOTIONS ==========
    
    async def save_promotion(self, state_dict: Dict) -> bool:
        """Salva uma promoção finalizada"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT INTO promotions 
                       (promo_id, session_id, titulo, mecanica, descricao, segmentacao,
                        periodo_inicio, periodo_fim, condicoes, recompensas, produtos,
                        categorias, volume_minimo, desconto_percentual, status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        state_dict.get('promo_id'),
                        state_dict.get('session_id'),
                        state_dict.get('titulo'),
                        state_dict.get('mecanica'),
                        state_dict.get('descricao'),
                        state_dict.get('segmentacao'),
                        state_dict.get('periodo_inicio'),
                        state_dict.get('periodo_fim'),
                        state_dict.get('condicoes'),
                        state_dict.get('recompensas'),
                        json.dumps(state_dict.get('produtos', [])),
                        json.dumps(state_dict.get('categorias', [])),
                        state_dict.get('volume_minimo'),
                        state_dict.get('desconto_percentual'),
                        state_dict.get('status', 'sent'),
                        state_dict.get('created_at', datetime.utcnow().isoformat())
                    )
                )
                await db.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar promotion: {e}")
            return False
    
    async def get_promotions(self, limit: int = 50) -> List[Dict]:
        """Lista promoções finalizadas"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    """SELECT * FROM promotions 
                       ORDER BY created_at DESC LIMIT ?""",
                    (limit,)
                )
                rows = await cursor.fetchall()
                promotions = []
                for row in rows:
                    promo = dict(row)
                    promo['produtos'] = json.loads(promo['produtos']) if promo['produtos'] else []
                    promo['categorias'] = json.loads(promo['categorias']) if promo['categorias'] else []
                    promotions.append(promo)
                return promotions
        except Exception as e:
            logger.error(f"Erro ao listar promotions: {e}")
            return []
    
    async def get_promotion_by_id(self, promo_id: str) -> Optional[Dict]:
        """Busca uma promoção por ID"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM promotions WHERE promo_id = ?",
                    (promo_id,)
                )
                row = await cursor.fetchone()
                if row:
                    promo = dict(row)
                    promo['produtos'] = json.loads(promo['produtos']) if promo['produtos'] else []
                    promo['categorias'] = json.loads(promo['categorias']) if promo['categorias'] else []
                    return promo
                return None
        except Exception as e:
            logger.error(f"Erro ao buscar promotion: {e}")
            return None
