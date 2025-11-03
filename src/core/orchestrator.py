"""
Orchestrator - Orquestra o fluxo de criação de promoções
"""
import logging
from typing import Dict, Optional
from src.core.promo_state import PromoState
from src.core.memory_manager import MemoryManager
from src.agents.extractor import ExtractorAgent
from src.agents.validator import ValidatorAgent
from src.agents.sumarizer import SumarizerAgent

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orquestra o fluxo completo de criação de promoções"""
    
    def __init__(
        self,
        extractor: ExtractorAgent,
        validator: ValidatorAgent,
        summarizer: SumarizerAgent,
        memory: MemoryManager
    ):
        self.extractor = extractor
        self.validator = validator
        self.summarizer = summarizer
        self.memory = memory
        logger.info("🎼 Orchestrator inicializado")
    
    async def handle_message(self, message: str, session_id: str) -> Dict:
        """
        Processa uma mensagem do usuário no fluxo de criação de promoção
        
        Args:
            message: Mensagem do usuário
            session_id: ID da sessão
            
        Returns:
            Dict com resposta e informações do estado
        """
        try:
            # 1. Carrega ou cria o estado da promoção
            state = await self.memory.load(session_id)
            logger.info(f"Estado carregado para sessão: {session_id} - Status: {state.status}")
            
            # 2. PRIORIDADE MÁXIMA: Detecta se usuário quer criar NOVA promoção
            is_new_promotion_request = await self._is_new_promotion_request(message, state)
            if is_new_promotion_request:
                logger.info(f"Detectado pedido de NOVA promoção - resetando sessão {session_id}")
                await self.memory.delete(session_id)
                state = PromoState(session_id=session_id)
                await self.memory.save(state)
                
                return {
                    "response": "✨ **Vamos criar uma nova promoção!**\n\n😊 Me conte sobre esta nova promoção. Pode me passar todas as informações que tiver:\n\n📌 Título\n🎯 Tipo/Mecânica\n📝 Descrição\n👥 Público-alvo\n📅 Período\n✅ Condições\n🎁 Recompensas\n\n💡 Pode me enviar tudo de uma vez ou aos poucos!",
                    "status": "collecting",
                    "completion": 0,
                    "state": state.to_dict(),
                    "new_promotion": True
                }
            
            # 3. Carrega histórico de conversas (últimas 10 mensagens)
            conversation_history = await self.memory.database.get_recent_messages(session_id, limit=10)
            
            # PROTEÇÃO GLOBAL: Garante que histórico é sempre lista válida sem Nones
            if conversation_history is None:
                conversation_history = []
            else:
                # Filtra qualquer None que possa existir
                conversation_history = [msg for msg in conversation_history if msg and isinstance(msg, dict)]
            
            logger.info(f"Histórico carregado: {len(conversation_history)} mensagens")
            
            # 4. PRIORIDADE: Verifica se está aguardando confirmação de envio de email
            if state.status == "awaiting_email_confirmation":
                return await self._handle_email_confirmation(message, state, session_id)
            
            # 5. PRIORIDADE: Verifica se está aguardando confirmação final dos dados
            if state.status == "ready":
                return await self._handle_final_confirmation(message, state, session_id)
            
            # 6. Detecta se é pergunta ou informação usando IA (apenas se não estiver em fluxo de confirmação)
            is_question = await self._is_question(message, state)
            
            if is_question:
                # É uma pergunta - usa IA para responder naturalmente
                answer = await self._answer_question(message, state, conversation_history)
                return {
                    "response": answer,
                    "status": "collecting",
                    "completion": state.get_completion_percentage(),
                    "state": state.to_dict()
                }
            
            # 7. É informação - extrai informações da mensagem COM CONTEXTO do histórico
            state, updated_fields = await self.extractor.extract_incremental(
                message, state, conversation_history
            )
            logger.info(f"Campos atualizados: {updated_fields}")
            
            # 8. Salva o estado atualizado
            await self.memory.save(state)
            
            # 9. Verifica campos faltantes
            missing = state.missing_fields()
            
            if missing:
                # Ainda faltam campos - solicita mais informações
                response = self._build_missing_fields_response(state, missing, updated_fields)
                return {
                    "response": response,
                    "status": "collecting",
                    "completion": state.get_completion_percentage(),
                    "missing_fields": missing,
                    "state": state.to_dict()
                }
            
            # 10. Todos os campos preenchidos - valida a promoção (APENAS SE NÃO JÁ VALIDADA)
            if state.status != "ready":
                validation = await self.validator.validate(state)
                
                # 11. Se aprovada, cria o resumo e solicita confirmação
                # Aceita tanto "APROVADO" quanto "ÓTIMO"
                if "✅ APROVADO" in validation or "✅ ÓTIMO" in validation:
                    summary = await self.summarizer.summarize(state)
                    state.status = "ready"
                    await self.memory.save(state)
                    
                    confirmation_msg = f"{summary}\n\n---\n\n✅ **Promoção pronta!**\n\n🤔 Está tudo certo ou deseja ajustar algo?"
                    
                    return {
                        "response": confirmation_msg,
                        "status": "ready",
                        "completion": 100,
                        "validation": validation,
                        "summary": summary,
                        "state": state.to_dict()
                    }
                else:
                    # Reprovada - retorna feedback
                    state.status = "rejected"
                    await self.memory.save(state)
                    
                    return {
                        "response": validation,
                        "status": "rejected",
                        "completion": 100,
                        "validation": validation,
                        "state": state.to_dict()
                    }
            
            # Se chegou aqui sem retornar, algo deu errado
            logger.error("Orchestrator handle_message não retornou nenhum valor válido")
            return {
                "response": "Erro: fluxo inválido no processamento",
                "status": "error",
                "state": state.to_dict()
            }
                
        except Exception as e:
            logger.error(f"Erro no orchestrator: {e}", exc_info=True)
            return {
                "response": f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}",
                "status": "error",
                "error": str(e)
            }
    
    def _build_missing_fields_response(
        self, 
        state: PromoState, 
        missing: list, 
        updated_fields: list
    ) -> str:
        """
        Constrói uma resposta amigável solicitando campos faltantes
        
        Args:
            state: Estado atual da promoção
            missing: Lista de campos faltantes
            updated_fields: Lista de campos que foram atualizados
            
        Returns:
            str: Mensagem formatada
        """
        response_parts = []
        
            # Saudação inicial mais amigável
        if not any([state.titulo, state.mecanica, state.descricao]):
            response_parts.append("😊 Olá! Vamos criar uma promoção incrível juntos!")
            response_parts.append("\n**O que eu preciso saber:**")
        elif updated_fields:
            response_parts.append("✨ Perfeito! Vejo que você me passou mais informações.")
        
        # Mostra TODOS os campos já preenchidos (não só os novos)
        filled_fields = []
        if state.titulo:
            filled_fields.append(f"📌 **Título**: {state.titulo}")
        if state.mecanica:
            filled_fields.append(f"🎯 **Tipo**: {state.mecanica}")
        if state.descricao:
            filled_fields.append(f"📝 **Como funciona**: {state.descricao[:100]}{'...' if len(state.descricao) > 100 else ''}")
        if state.segmentacao:
            filled_fields.append(f"👥 **Público**: {state.segmentacao}")
        if state.periodo_inicio and state.periodo_fim:
            filled_fields.append(f"📅 **Período**: {state.periodo_inicio} até {state.periodo_fim}")
        elif state.periodo_inicio or state.periodo_fim:
            filled_fields.append(f"📅 **Período**: {state.periodo_inicio or state.periodo_fim}")
        if state.condicoes:
            filled_fields.append(f"✅ **Condições**: {state.condicoes[:80]}{'...' if len(state.condicoes) > 80 else ''}")
        if state.recompensas:
            filled_fields.append(f"🎁 **Recompensas**: {state.recompensas[:80]}{'...' if len(state.recompensas) > 80 else ''}")
        
        if filled_fields:
            response_parts.append("\n**📋 Informações que já tenho:**")
            response_parts.extend(filled_fields)
        
        # Mostra progresso
        completion = state.get_completion_percentage()
        response_parts.append(f"\n📊 **Progresso geral:** {completion:.0f}% completo")
        
        # Solicita campos faltantes de forma mais conversacional
        if missing:
            if completion < 30:
                response_parts.append("\n💬 **Para continuar, me conte:**")
            else:
                response_parts.append("\n🎯 **Só falta mais alguns detalhes:**")
            
            # Mostra TODOS os campos faltantes, priorizando os mais importantes
            important_fields = ['titulo', 'mecanica', 'descricao', 'segmentacao', 'periodo_inicio', 'periodo_fim']
            priority_missing = [f for f in important_fields if f in missing]
            other_missing = [f for f in missing if f not in important_fields]
            
            # Lista TODOS os campos faltantes (priorizados + outros)
            all_missing_sorted = priority_missing + other_missing
            
            for field in all_missing_sorted:
                response_parts.append(f"• {self._translate_field(field)}")
        
        # Mensagem de encerramento amigável
        if completion < 50:
            response_parts.append("\n💡 **Dica:** Pode me enviar tudo de uma vez ou aos poucos, como preferir!")
        else:
            response_parts.append("\n✨ Estamos quase lá! Me passe essas últimas informações.")
        
        return "\n".join(response_parts)
    
    def _translate_field(self, field: str) -> str:
        """Traduz nomes de campos técnicos para nomes amigáveis"""
        translations = {
            'titulo': 'Título da promoção',
            'mecanica': 'Tipo de mecânica (progressiva, casada, pontos, etc)',
            'descricao': 'Descrição de como funciona',
            'segmentacao': 'Público-alvo/Segmentação',
            'periodo_inicio': 'Data de início',
            'periodo_fim': 'Data de término',
            'condicoes': 'Condições e regras',
            'recompensas': 'Benefícios e recompensas',
            'produtos': 'Produtos incluídos',
            'categorias': 'Categorias',
            'volume_minimo': 'Volume mínimo',
            'desconto_percentual': 'Percentual de desconto'
        }
        return translations.get(field, field.replace('_', ' ').title())
    
    async def validate_promotion(self, session_id: str) -> Dict:
        """
        Valida uma promoção específica
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dict com resultado da validação
        """
        try:
            state = await self.memory.load(session_id)
            validation = await self.validator.validate_comprehensive(state)
            return validation
        except Exception as e:
            logger.error(f"Erro ao validar promoção: {e}")
            return {
                "error": str(e),
                "is_valid": False
            }
    
    async def create_summary(self, session_id: str) -> str:
        """
        Cria um resumo da promoção
        
        Args:
            session_id: ID da sessão
            
        Returns:
            str: Resumo em markdown
        """
        try:
            state = await self.memory.load(session_id)
            summary = await self.summarizer.summarize(state)
            return summary
        except Exception as e:
            logger.error(f"Erro ao criar resumo: {e}")
            return f"Erro ao criar resumo: {str(e)}"
    
    async def create_email(self, session_id: str) -> str:
        """
        Cria o HTML do email da promoção
        
        Args:
            session_id: ID da sessão
            
        Returns:
            str: HTML do email
        """
        try:
            state = await self.memory.load(session_id)
            email_html = await self.summarizer.create_email_body(state)
            return email_html
        except Exception as e:
            logger.error(f"Erro ao criar email: {e}")
            return f"<html><body>Erro ao criar email: {str(e)}</body></html>"
    
    async def get_state(self, session_id: str) -> Optional[PromoState]:
        """
        Obtém o estado de uma promoção
        
        Args:
            session_id: ID da sessão
            
        Returns:
            PromoState ou None se não encontrado
        """
        try:
            return await self.memory.load(session_id)
        except Exception as e:
            logger.error(f"Erro ao obter estado: {e}")
            return None
    
    async def reset_state(self, session_id: str) -> bool:
        """
        Reseta o estado de uma promoção
        
        Args:
            session_id: ID da sessão
            
        Returns:
            bool: True se sucesso
        """
        try:
            await self.memory.delete(session_id)
            logger.info(f"Estado resetado para sessão: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao resetar estado: {e}")
            return False
    
    async def list_all_promotions(self) -> list:
        """Lista todas as promoções"""
        try:
            return await self.memory.list_all()
        except Exception as e:
            logger.error(f"Erro ao listar promoções: {e}")
            return []
    
    async def _handle_final_confirmation(self, message: str, state: PromoState, session_id: str) -> Dict:
        """
        Processa confirmação final dos dados e pergunta sobre envio de email
        
        Args:
            message: Mensagem do usuário
            state: Estado atual
            session_id: ID da sessão
            
        Returns:
            Dict com resposta
        """
        message_lower = message.lower().strip()
        
        # Detecta confirmação positiva (inclui negação de ajustes)
        positive_words = ['sim', 'yes', 'correto', 'ok', 'confirma', 'tudo cert', 'perfeito', 'está bem', 'tá bom']
        negative_adjustment = ['não quero ajustar', 'não quer ajustar', 'não precisa ajustar', 'está correto', 'tá correto', 'sem ajuste']
        
        if any(word in message_lower for word in positive_words) or any(phrase in message_lower for phrase in negative_adjustment):
            state.status = "awaiting_email_confirmation"
            await self.memory.save(state)
            
            return {
                "response": "✅ **Ótimo! Dados confirmados.**\n\n📧 Deseja enviar esta promoção por email agora? (Responda 'sim' ou 'não')",
                "status": "awaiting_email_confirmation",
                "state": state.to_dict()
            }
        else:
            # Usuário quer fazer ajustes
            return {
                "response": "📝 **Entendido.** Me diga o que gostaria de ajustar e vou atualizar a promoção.",
                "status": "collecting",
                "state": state.to_dict()
            }
    
    async def _is_new_promotion_request(self, message: str, state: PromoState) -> bool:
        """
        Detecta se o usuário quer criar uma NOVA promoção
        
        Args:
            message: Mensagem do usuário
            state: Estado atual
            
        Returns:
            bool: True se usuário quer criar nova promoção
        """
        # Se o estado está vazio ou no início, não é pedido de nova promoção
        if state.status in ["draft", ""] and state.get_completion_percentage() < 10:
            return False
        
        # Se está em estado completed, awaiting_email_confirmation ou ready, verifica a mensagem
        if state.status in ["completed", "awaiting_email_confirmation", "ready"]:
            message_lower = message.lower().strip()
            
            # Palavras-chave que indicam nova promoção
            new_promo_keywords = [
                'nova promoção',
                'outra promoção',
                'criar outra',
                'criar nova',
                'nova promo',
                'fazer outra',
                'cadastrar outra',
                'cadastrar nova',
                'quero criar',
                'vamos criar',
                'criar promoção'
            ]
            
            # Verifica se contém alguma palavra-chave
            if any(keyword in message_lower for keyword in new_promo_keywords):
                logger.info(f"Detectado pedido de nova promoção: '{message}'")
                return True
        
        return False
    
    async def _is_question(self, message: str, state: PromoState) -> bool:
        """
        Detecta se a mensagem é uma pergunta usando IA
        
        Args:
            message: Mensagem do usuário
            state: Estado atual
            
        Returns:
            bool: True se é pergunta
        """
        try:
            # Usa IA para detectar se é pergunta
            response = await self.extractor.client.chat.completions.create(
                model=self.extractor.model,
                messages=[
                    {"role": "system", "content": "Você analisa se uma mensagem é PERGUNTA ou INFORMAÇÃO. Responda apenas 'PERGUNTA' ou 'INFORMAÇÃO'."},
                    {"role": "user", "content": f"Mensagem: '{message}'\n\nIsto é uma PERGUNTA (usuário quer saber algo) ou INFORMAÇÃO (usuário está fornecendo dados)?"}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            is_q = "PERGUNTA" in result
            logger.info(f"Mensagem classificada como: {'PERGUNTA' if is_q else 'INFORMAÇÃO'}")
            return is_q
            
        except Exception as e:
            logger.error(f"Erro ao detectar pergunta: {e}")
            # Se der erro, assume que é informação
            return False
    
    async def _answer_question(self, message: str, state: PromoState, conversation_history: list) -> str:
        """
        Responde uma pergunta do usuário usando IA
        
        Args:
            message: Pergunta do usuário
            state: Estado atual
            conversation_history: Histórico da conversa
            
        Returns:
            str: Resposta natural da IA
        """
        try:
            # Carrega prompt persona
            try:
                with open("prompts/persona.md", "r", encoding="utf-8") as f:
                    persona_prompt = f.read()
            except:
                persona_prompt = "Você é o PromoAgente, um assistente entusiasmado e colaborativo que ajuda a criar promoções."
            
            # Prepara contexto
            context_parts = [f"**CONTEXTO DA PROMOÇÃO ATUAL:**"]
            
            if state.titulo:
                context_parts.append(f"- Título: {state.titulo}")
            if state.mecanica:
                context_parts.append(f"- Tipo: {state.mecanica}")
            if state.descricao:
                context_parts.append(f"- Descrição: {state.descricao}")
            
            completion = state.get_completion_percentage()
            context_parts.append(f"- Progresso: {completion:.0f}% completo")
            
            missing = state.missing_fields()
            if missing:
                context_parts.append(f"- Faltam: {', '.join(missing)}")
            
            context = "\n".join(context_parts)
            
            # Histórico recente
            history_text = ""
            if conversation_history:
                history_text = "\n\n**ÚLTIMAS MENSAGENS:**\n"
                for msg in conversation_history[-6:]:  # Últimas 6 mensagens
                    if msg and isinstance(msg, dict):  # Verifica se msg é válido
                        role = "Usuário" if msg.get('role') == 'user' else "Assistente"
                        history_text += f"{role}: {msg.get('content', '')}\n"
            
            full_prompt = f"{persona_prompt}\n\n{context}{history_text}\n\n**PERGUNTA DO USUÁRIO:**\n{message}\n\nResponda de forma natural, entusiasmada e útil!"
            
            # Usa IA para responder
            response = await self.extractor.client.chat.completions.create(
                model=self.extractor.model,
                messages=[
                    {"role": "system", "content": "Você é o PromoAgente, um assistente colaborativo e entusiasmado."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Pergunta respondida naturalmente")
            return answer
            
        except Exception as e:
            logger.error(f"Erro ao responder pergunta: {e}")
            return "Desculpe, não consegui processar sua pergunta. Pode reformular?"
    
    async def _handle_email_confirmation(self, message: str, state: PromoState, session_id: str) -> Dict:
        """
        Processa confirmação de envio de email
        
        Args:
            message: Mensagem do usuário
            state: Estado atual
            session_id: ID da sessão
            
        Returns:
            Dict com resposta
        """
        from src.services.email_service import enviar_email
        from datetime import datetime
        
        message_lower = message.lower().strip()
        
        # Detecta resposta positiva para envio de email
        if any(word in message_lower for word in ['sim', 'yes', 'enviar', 'ok', 'confirma', 'quero']):
            try:
                # Cria o HTML do email
                email_html = await self.summarizer.create_email_body(state)
                
                # Envia o email
                enviado = enviar_email(state.to_dict(), email_html)
                
                if enviado:
                    # Salva a promoção no banco como finalizada
                    state.status = "completed"
                    if not state.promo_id:
                        state.promo_id = f"promo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                    
                    await self.memory.save(state)
                    await self.memory.database.save_promotion(state.to_dict())
                    
                    return {
                        "response": "✅ **Promoção enviada com sucesso!**\n\n📧 O email foi enviado para o destino configurado.\n💾 A promoção foi salva no sistema como completa.\n\n🎉 Tudo pronto! Posso ajudar com outra promoção?",
                        "status": "completed",
                        "state": state.to_dict()
                    }
                else:
                    return {
                        "response": "⚠️ **Erro ao enviar email.**\n\nVerifique se as configurações de email estão corretas no arquivo .env.\n\n💾 Mas não se preocupe! A promoção foi salva no sistema. Deseja tentar enviar novamente?",
                        "status": "awaiting_email_confirmation",
                        "state": state.to_dict()
                    }
                    
            except Exception as e:
                logger.error(f"Erro ao enviar email: {e}", exc_info=True)
                return {
                    "response": f"❌ **Erro ao processar envio:** {str(e)}\n\nDeseja tentar novamente?",
                    "status": "awaiting_email_confirmation",
                    "state": state.to_dict()
                }
        else:
            # Usuário não quer enviar email
            state.status = "completed"
            if not state.promo_id:
                state.promo_id = f"promo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            await self.memory.save(state)
            await self.memory.database.save_promotion(state.to_dict())
            
            return {
                "response": "✅ **Promoção salva no sistema!**\n\n💾 A promoção foi armazenada com sucesso sem envio de email.\n\n🎉 Tudo pronto! Posso ajudar com outra promoção?",
                "status": "completed",
                "state": state.to_dict()
            }
