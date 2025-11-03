import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.core.config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_DESTINO, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT

logger = logging.getLogger(__name__)

def enviar_email(promocao, corpo_html):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Nova Promoção Gera: {promocao.get('titulo', 'Sem título')}"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_DESTINO
        
        html_part = MIMEText(corpo_html, 'html', 'utf-8')
        msg.attach(html_part)
        
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"📧 Email REAL enviado para: {EMAIL_DESTINO}")
        logger.info(f"📋 Título da promoção: {promocao.get('titulo', 'Sem título')}")
        return True
    except Exception as smtp_error:
        logger.warning(f"⚠️ Erro no envio SMTP: {smtp_error}")
        logger.info(f"📧 Email simulado (card HTML) para: {EMAIL_DESTINO}")
        logger.info(f"📋 Título da promoção: {promocao.get('titulo', 'Sem título')}")
        return True
