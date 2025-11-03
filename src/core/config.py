import os
import logging

# NUNCA carregar .env em produção - Railway tem suas próprias variáveis
# Apenas importar dotenv se necessário (desenvolvimento local)
try:
    from dotenv import load_dotenv
    # Só carrega .env se o arquivo existir (desenvolvimento local)
    if os.path.exists('.env'):
        load_dotenv()
        print("🔧 DEBUG: Carregou .env (modo desenvolvimento)")
    else:
        print("🚀 DEBUG: Sem .env, usando variáveis do sistema (produção)")
except ImportError:
    # Em produção, dotenv pode nem estar instalado
    print("🚀 DEBUG: python-dotenv não instalado, usando variáveis do sistema")
    pass

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG', 'False').lower() == 'true' else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Modelo padrão correto

# Configurações de E-mail SMTP
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "promocoes.agente@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_DESTINO = os.getenv("EMAIL_DESTINATION", "promocoes@gera.com")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

# Configurações da Aplicação
HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', 7000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Configurações dos Agents
EXTRACTION_PROMPT_PATH = "prompts/extraction.md"
VALIDATION_PROMPT_PATH = "prompts/validation.md"
SUMMARIZATION_PROMPT_PATH = "prompts/summarization.md"
PERSONA_PROMPT_PATH = "prompts/persona.md"

def log_configs():
    logger.info("🚀 Configurações Carregadas")
    logger.info(f"ENVIRONMENT: {ENVIRONMENT}")
    logger.info(f"DEBUG MODE: {DEBUG}")
    logger.info(f"OPENAI_MODEL: {OPENAI_MODEL}")
    logger.info(f"HOST: {HOST}:{PORT}")
