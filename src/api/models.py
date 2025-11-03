from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

class SystemStatus(BaseModel):
    openai: bool
    agno_framework: bool
    sqlite_db: bool
    python_version: str
    openai_version: Optional[str] = None
    agno_version: Optional[str] = None
    messages_stored: int = 0
    environment: str = "development"
    agno_ready: bool
    agno_agent_is_none: bool
    agno_os_is_none: bool
    agno_status_error: Optional[str] = None
