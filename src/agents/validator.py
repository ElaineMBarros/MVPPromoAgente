"""
ValidatorAgent - Valida promoções com regras de negócio B2B
"""
import logging
from typing import List, Dict
from openai import AsyncOpenAI
from src.core.promo_state import PromoState

logger = logging.getLogger(__name__)


class ValidatorAgent:
    """Agent responsável por validar promoções com regras de negócio"""
    
    def __init__(self, openai_client: AsyncOpenAI, model: str, prompt_path: str):
        self.client = openai_client
        self.model = model
        
        # Carrega o prompt de validação
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.prompt = f.read()
            logger.info(f"Prompt de validação carregado: {prompt_path}")
        except Exception as e:
            logger.warning(f"Erro ao carregar prompt: {e}. Usando prompt padrão.")
            self.prompt = self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Retorna um prompt padrão caso o arquivo não exista"""
        return """Você é um especialista em validação de promoções B2B do varejo.

Analise a promoção e verifique:

1. **Viabilidade Comercial**: A promoção é viável para o varejo B2B?
2. **Clareza**: As regras estão claras e compreensíveis?
3. **Completude**: Todas as informações necessárias estão presentes?
4. **Riscos**: Há algum risco ou problema potencial?
5. **Sugestões**: Há melhorias que podem ser feitas?

Retorne sua análise em texto claro, começando com:
- "✅ APROVADO" se a promoção está boa para envio
- "⚠️ ATENÇÃO" se há pontos de atenção mas pode prosseguir
- "❌ REPROVADO" se há problemas graves que impedem o envio

Depois explique os motivos e forneça sugestões se aplicável."""
    
    async def validate(self, state: PromoState) -> str:
        """
        Valida o estado da promoção
        
        Args:
            state: Estado da promoção a ser validada
            
        Returns:
            str: Resultado da validação com análise detalhada
        """
        # Verifica campos obrigatórios primeiro
        missing = state.missing_fields()
        if missing:
            return f"⚠️ ATENÇÃO: Campos obrigatórios faltando: {', '.join(missing)}"
        
        # Valida com IA
        try:
            from datetime import datetime
            current_date = datetime.now().strftime("%d/%m/%Y")
            
            promo_json = state.to_json()
            full_prompt = f"**DATA ATUAL DO SISTEMA: {current_date}**\n\n{self.prompt}\n\n**PROMOÇÃO PARA VALIDAR:**\n{promo_json}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em validação de promoções B2B."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.4
            )
            
            validation_result = response.choices[0].message.content
            logger.info(f"Validação concluída para promoção: {state.titulo}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Erro ao validar promoção: {e}")
            return "⚠️ ATENÇÃO: Erro ao validar promoção. Revise manualmente antes de enviar."
    
    def validate_basic_rules(self, state: PromoState) -> Dict[str, List[str]]:
        """
        Valida regras básicas sem usar IA
        
        Returns:
            Dict com 'errors', 'warnings' e 'info'
        """
        errors = []
        warnings = []
        info = []
        
        # Verifica campos obrigatórios
        missing = state.missing_fields()
        if missing:
            errors.append(f"Campos obrigatórios faltando: {', '.join(missing)}")
        
        # Valida título
        if state.titulo and len(state.titulo) < 5:
            warnings.append("Título muito curto (menos de 5 caracteres)")
        
        if state.titulo and len(state.titulo) > 100:
            warnings.append("Título muito longo (mais de 100 caracteres)")
        
        # Valida descrição
        if state.descricao and len(state.descricao) < 20:
            warnings.append("Descrição muito curta (menos de 20 caracteres)")
        
        # Valida mecânica
        mecanicas_validas = ['progressiva', 'casada', 'pontos', 'relâmpago', 'escalonada', 'vip']
        if state.mecanica and state.mecanica.lower() not in mecanicas_validas:
            info.append(f"Mecânica '{state.mecanica}' não está na lista padrão: {', '.join(mecanicas_validas)}")
        
        # Valida datas
        if state.periodo_inicio and state.periodo_fim:
            # Validação básica - poderia ser melhorada com datetime
            info.append("Lembre-se de validar se a data de fim é posterior à data de início")
        
        # Valida completude
        completion = state.get_completion_percentage()
        if completion == 100:
            info.append("✅ Todos os campos obrigatórios preenchidos")
        else:
            info.append(f"📊 Completude: {completion:.0f}%")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'info': info
        }
    
    async def validate_comprehensive(self, state: PromoState) -> Dict:
        """
        Validação completa (básica + IA)
        
        Returns:
            Dict com 'basic_validation' e 'ai_validation'
        """
        basic = self.validate_basic_rules(state)
        ai_result = await self.validate(state)
        
        return {
            'basic_validation': basic,
            'ai_validation': ai_result,
            'is_valid': len(basic['errors']) == 0
        }
