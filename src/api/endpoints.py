from fastapi import APIRouter, Response, Body, Query
from fastapi.responses import HTMLResponse, JSONResponse
from src.api.models import ChatResponse
from src.core.agent_logic import promo_agente
from src.services.email_service import enviar_email
from datetime import datetime
from typing import Annotated, Optional

router = APIRouter()

HOME_HTML = """
<html>
<head><title>PromoAgente Local</title></head>
<body><h1>PromoAgente Local v2</h1><p>Arquitetura modular.</p></body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def home():
    return HOME_HTML

@router.get("/status")
async def get_status():
    return await promo_agente.get_system_status()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: Annotated[str, Body(embed=True)],
    session_id: Annotated[Optional[str], Body(embed=True)] = None
):
    """
    Endpoint para interagir com o agente de IA.
    Recebe uma mensagem e opcionalmente um session_id para manter o contexto.
    """
    result = await promo_agente.chat_with_ai(
        message=message,
        session_id=session_id
    )
    return result

@router.get("/test-email")
async def test_email():
    promocao_teste = { "titulo": "Promoção Teste Modular" }
    enviado = enviar_email(promocao_teste, "<h1>Teste</h1>")
    if enviado:
        return {"status": "success", "message": "Email de teste enviado."}
    else:
        return {"status": "error", "message": "Falha no envio do email."}

@router.get("/logo_gera.png")
async def get_logo():
    try:
        with open("logo_gera.png", "rb") as f:
            content = f.read()
        return Response(content=content, media_type="image/png")
    except FileNotFoundError:
        return JSONResponse({"error": "Logo não encontrado"}, status_code=404)


# ========== NOVOS ENDPOINTS PARA PROMOÇÕES ==========

@router.get("/promotions")
async def list_promotions(limit: int = Query(50, description="Número máximo de promoções")):
    """Lista todas as promoções finalizadas"""
    try:
        promotions = await promo_agente.local_db.get_promotions(limit=limit)
        return {
            "promotions": promotions,
            "count": len(promotions)
        }
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao listar promoções: {str(e)}"},
            status_code=500
        )


@router.get("/promotions/{promo_id}")
async def get_promotion(promo_id: str):
    """Busca uma promoção específica por ID"""
    try:
        promotion = await promo_agente.local_db.get_promotion_by_id(promo_id)
        if promotion:
            return promotion
        return JSONResponse(
            {"error": "Promoção não encontrada"},
            status_code=404
        )
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao buscar promoção: {str(e)}"},
            status_code=500
        )


@router.get("/promotion-state/{session_id}")
async def get_promotion_state(session_id: str):
    """Obtém o estado atual de uma promoção em criação"""
    try:
        state = await promo_agente.get_promotion_state(session_id)
        if state:
            return state
        return JSONResponse(
            {"error": "Estado não encontrado"},
            status_code=404
        )
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao obter estado: {str(e)}"},
            status_code=500
        )


@router.post("/promotion-state/{session_id}/validate")
async def validate_promotion(session_id: str):
    """Valida uma promoção"""
    try:
        validation = await promo_agente.validate_promotion(session_id)
        return validation
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao validar promoção: {str(e)}"},
            status_code=500
        )


@router.post("/promotion-state/{session_id}/summary")
async def create_summary(session_id: str):
    """Cria um resumo da promoção"""
    try:
        summary = await promo_agente.create_summary(session_id)
        return {"summary": summary}
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao criar resumo: {str(e)}"},
            status_code=500
        )


@router.post("/promotion-state/{session_id}/email")
async def create_email(session_id: str):
    """Cria o HTML do email da promoção"""
    try:
        email_html = await promo_agente.create_email(session_id)
        return HTMLResponse(content=email_html)
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao criar email: {str(e)}"},
            status_code=500
        )


@router.post("/promotion-state/{session_id}/save")
async def save_promotion(session_id: str):
    """Salva uma promoção finalizada"""
    try:
        success = await promo_agente.save_final_promotion(session_id)
        if success:
            return {"status": "success", "message": "Promoção salva com sucesso"}
        return JSONResponse(
            {"error": "Não foi possível salvar a promoção"},
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao salvar promoção: {str(e)}"},
            status_code=500
        )


@router.post("/promotion-state/{session_id}/send-email")
async def send_promotion_email(session_id: str):
    """Cria e envia o email da promoção"""
    try:
        # Primeiro obtém o estado
        state = await promo_agente.get_promotion_state(session_id)
        if not state:
            return JSONResponse(
                {"error": "Promoção não encontrada"},
                status_code=404
            )
        
        # Cria o HTML do email
        email_html = await promo_agente.create_email(session_id)
        
        # Envia o email
        enviado = enviar_email(state, email_html)
        
        if enviado:
            # Salva a promoção final
            await promo_agente.save_final_promotion(session_id)
            return {
                "status": "success",
                "message": "Email enviado e promoção salva com sucesso"
            }
        else:
            return JSONResponse(
                {"error": "Falha ao enviar email"},
                status_code=500
            )
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao enviar email: {str(e)}"},
            status_code=500
        )


@router.delete("/promotion-state/{session_id}")
async def reset_promotion(session_id: str):
    """Reseta o estado de uma promoção"""
    try:
        success = await promo_agente.reset_promotion(session_id)
        if success:
            return {"status": "success", "message": "Promoção resetada com sucesso"}
        return JSONResponse(
            {"error": "Não foi possível resetar a promoção"},
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            {"error": f"Erro ao resetar promoção: {str(e)}"},
            status_code=500
        )
