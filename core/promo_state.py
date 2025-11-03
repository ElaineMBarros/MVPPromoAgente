from pydantic import BaseModel
from typing import Optional, List

class PromoState(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    publico_alvo: Optional[str] = None
    periodo: Optional[str] = None
    condicoes: Optional[str] = None
    premio: Optional[str] = None
    observacoes: Optional[str] = None

    def missing_fields(self) -> List[str]:
        return [k for k, v in self.dict().items() if not v or str(v).strip() == ""]
