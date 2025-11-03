from typing import Optional
from core.promo_state import PromoState

class MemoryManager:
    def __init__(self, local_db):
        self.db = local_db

    async def load(self, session_id: str) -> PromoState:
        messages = await self.db.get_recent_messages(session_id)
        text = "\n".join(m["content"] for m in messages if m["role"] == "user")
        # Estado começa vazio e será atualizado pelo extractor
        return PromoState()

    async def save_interaction(self, session_id: str, user_message: str, ai_message: str):
        await self.db.save_message(session_id, user_message, ai_message)
