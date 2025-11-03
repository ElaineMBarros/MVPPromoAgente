import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def extrair_informacoes_promocao(messages: List[Dict]) -> Dict[str, str]:
    """Extrai informações COMPLETAS da promoção das mensagens da conversa"""
    promocao = {
        "titulo": "", "descricao": "", "publico_alvo": "", "periodo": "",
        "condicoes": "", "premio": "", "observacoes": ""
    }
    texto_resumo = ""
    for msg in reversed(messages):
        if msg.get("role") == "agent" and len(msg.get("content", "")) > 200:
            content = msg["content"]
            if any(termo in content for termo in ["1. **", "2. **", "Título**", "Mecânica", "Descrição", "Segmentação", "Período", "Condições", "Recompensas"]):
                texto_resumo = content
                logger.info("📋 Encontrado resumo estruturado do agente")
                break
    
    if not texto_resumo:
        return promocao

    # Padrões de extração
    padroes = {
        "titulo": [r"1\.\s*\*\*Título\*\*:\s*([^\n]+?)(?=\s*2\.|$)", r"\*\*Título\*\*:\s*([^*\n]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)", r"Título[:\s]*([^\n]+?)(?=\n|$)", r"(Promoção.*?[^\n]*)"],
        "descricao": [r"3\.\s*\*\*Descrição.*?\*\*:\s*([^4]+?)(?=4\.|$)", r"2\.\s*\*\*.*?Mecânica.*?\*\*:\s*([^3]+?)(?=3\.|$)", r"\*\*Descrição\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)", r"Descrição[:\s]*([^\n]+?)(?=\n|$)"],
        "publico_alvo": [r"4\.\s*\*\*Segmentação.*?\*\*:\s*([^5]+?)(?=5\.|$)", r"\*\*Público-alvo.*?\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)", r"3\.\s*\*\*Público-alvo.*?\*\*:\s*([^*]+?)(?=\n\d+\.|$)", r"Público-alvo[:\s]*([^\n]+?)(?=\n|$)"],
        "periodo": [r"5\.\s*\*\*Período.*?\*\*:\s*([^6]+?)(?=6\.|$)", r"\*\*Período\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)", r"4\.\s*\*\*Período\*\*:\s*([^*]+?)(?=\n\d+\.|$)", r"Período[:\s]*([^\n]+?)(?=\n|$)", r"(\d{2}/\d{2}/\d{4}\s*a\s*\d{2}/\d{2}/\d{4})"],
        "condicoes": [r"6\.\s*\*\*Condições.*?\*\*:\s*([^7]+?)(?=7\.|$)", r"\*\*Condições\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)", r"5\.\s*\*\*Condições\*\*:\s*([^*]+?)(?=\n\d+\.|$)", r"Condições[:\s]*([^\n]+?)(?=\n|$)"],
        "premio": [r"7\.\s*\*\*Sistema.*?Recompensas.*?\*\*:\s*([^\.]+?)(?=\n\n|\.\s|$)", r"\*\*Prêmio\*\*:\s*([^*]+?)(?=\d+\.\s*\*\*|\n\d+\.|$)", r"6\.\s*\*\*Prêmio\*\*:\s*([^*]+?)(?=\n\d+\.|$)", r"Prêmio[:\s]*([^\n]+?)(?=\n|$)", r"(\d+%\s*.*?desconto[^\n]*)"]
    }

    for campo, lista_padroes in padroes.items():
        for padrao in lista_padroes:
            match = re.search(padrao, texto_resumo, re.DOTALL | re.IGNORECASE)
            if match:
                promocao[campo] = match.group(1).strip()
                logger.info(f"✅ {campo.capitalize()} extraído")
                break
    
    campos_preenchidos = sum(1 for v in promocao.values() if v)
    logger.info(f"📊 Total de campos extraídos: {campos_preenchidos}/7")
    return promocao

def criar_previa_chat_promocao(promocao: Dict[str, str]) -> str:
    """Cria uma prévia compacta da promoção para mostrar no chat."""
    previa = "```\n🎯 PRÉVIA DA PROMOÇÃO GERA\n" + "=" * 50 + "\n\n"
    if promocao.get("titulo"): previa += f"🏷️  TÍTULO: {promocao['titulo']}\n\n"
    if promocao.get("descricao"): previa += f"📝 DESCRIÇÃO: {promocao['descricao']}\n\n"
    if promocao.get("publico_alvo"): previa += f"🎯 PÚBLICO-ALVO: {promocao['publico_alvo']}\n\n"
    if promocao.get("periodo"): previa += f"📅 PERÍODO: {promocao['periodo']}\n\n"
    if promocao.get("condicoes"): previa += f"✅ CONDIÇÕES: {promocao['condicoes']}\n\n"
    if promocao.get("premio"): previa += f"🎁 PRÊMIO: {promocao['premio']}\n\n"
    previa += "```"
    return previa
