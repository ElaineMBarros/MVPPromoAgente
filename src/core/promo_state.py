"""
PromoState - Gerencia o estado de uma promoção durante a criação
"""
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class PromoState:
    """Estado de uma promoção sendo criada"""
    
    # Identificação
    session_id: str = ""
    promo_id: Optional[str] = None
    
    # Campos obrigatórios da promoção
    titulo: Optional[str] = None
    mecanica: Optional[str] = None  # Ex: progressiva, casada, pontos, relâmpago
    descricao: Optional[str] = None
    segmentacao: Optional[str] = None  # Público-alvo
    periodo_inicio: Optional[str] = None
    periodo_fim: Optional[str] = None
    condicoes: Optional[str] = None
    recompensas: Optional[str] = None
    
    # Campos opcionais B2B
    produtos: Optional[List[str]] = field(default_factory=list)
    categorias: Optional[List[str]] = field(default_factory=list)
    clientes_alvo: Optional[List[str]] = field(default_factory=list)
    volume_minimo: Optional[str] = None
    desconto_percentual: Optional[str] = None
    margem_esperada: Optional[str] = None
    roi_estimado: Optional[str] = None
    
    # Metadados
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "draft"  # draft, validating, approved, rejected, sent
    
    def missing_fields(self) -> List[str]:
        """Retorna lista de campos obrigatórios faltantes"""
        required = {
            'titulo': self.titulo,
            'mecanica': self.mecanica,
            'descricao': self.descricao,
            'segmentacao': self.segmentacao,
            'periodo_inicio': self.periodo_inicio,
            'periodo_fim': self.periodo_fim,
            'condicoes': self.condicoes,
            'recompensas': self.recompensas
        }
        
        missing = [field for field, value in required.items() if not value]
        return missing
    
    def is_complete(self) -> bool:
        """Verifica se todos os campos obrigatórios estão preenchidos"""
        return len(self.missing_fields()) == 0
    
    def to_dict(self) -> Dict:
        """Converte o estado para dicionário"""
        return {
            'session_id': self.session_id,
            'promo_id': self.promo_id,
            'titulo': self.titulo,
            'mecanica': self.mecanica,
            'descricao': self.descricao,
            'segmentacao': self.segmentacao,
            'periodo_inicio': self.periodo_inicio,
            'periodo_fim': self.periodo_fim,
            'condicoes': self.condicoes,
            'recompensas': self.recompensas,
            'produtos': self.produtos,
            'categorias': self.categorias,
            'clientes_alvo': self.clientes_alvo,
            'volume_minimo': self.volume_minimo,
            'desconto_percentual': self.desconto_percentual,
            'margem_esperada': self.margem_esperada,
            'roi_estimado': self.roi_estimado,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PromoState':
        """Cria um PromoState a partir de um dicionário"""
        return cls(
            session_id=data.get('session_id', ''),
            promo_id=data.get('promo_id'),
            titulo=data.get('titulo'),
            mecanica=data.get('mecanica'),
            descricao=data.get('descricao'),
            segmentacao=data.get('segmentacao'),
            periodo_inicio=data.get('periodo_inicio'),
            periodo_fim=data.get('periodo_fim'),
            condicoes=data.get('condicoes'),
            recompensas=data.get('recompensas'),
            produtos=data.get('produtos', []),
            categorias=data.get('categorias', []),
            clientes_alvo=data.get('clientes_alvo', []),
            volume_minimo=data.get('volume_minimo'),
            desconto_percentual=data.get('desconto_percentual'),
            margem_esperada=data.get('margem_esperada'),
            roi_estimado=data.get('roi_estimado'),
            created_at=data.get('created_at', datetime.utcnow().isoformat()),
            updated_at=data.get('updated_at', datetime.utcnow().isoformat()),
            status=data.get('status', 'draft')
        )
    
    def to_json(self) -> str:
        """Converte o estado para JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def update_timestamp(self):
        """Atualiza o timestamp de modificação"""
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_completion_percentage(self) -> float:
        """Retorna o percentual de completude dos campos obrigatórios"""
        total_required = 8  # Total de campos obrigatórios
        missing = len(self.missing_fields())
        return ((total_required - missing) / total_required) * 100
