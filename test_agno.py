import asyncio
import os
from dotenv import load_dotenv

# Importa as classes necessárias do Agno
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

async def main():
    """
    Função principal para executar o chat de teste com Agno e OpenAI.
    """
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Garante que a chave da API da OpenAI está disponível
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\x1b[31mErro: A variável de ambiente OPENAI_API_KEY não está definida.\x1b[0m")
        print("Por favor, adicione-a ao seu arquivo .env e tente novamente.")
        return

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    print(f"\x1b[36m--- Iniciando Chat de Teste com Agno e OpenAI ({model_name}) ---\x1b[0m")
    
    try:
        # 1. Configura o agente Agno com o modelo GPT da OpenAI
        test_agent = Agent(
            name="AgenteDeTesteOpenAI",
            model=OpenAIChat(id=model_name),
            db=SqliteDb(db_file="test_chat.db"),  # Usa um banco de dados em arquivo para o teste
            markdown=True,
        )
        print("\x1b[32mAgente inicializado com sucesso!\x1b[0m")
        print("Digite sua mensagem ou 'sair' para terminar.")
        print("-" * 50)

        # 2. Loop de chat interativo
        while True:
            # Lê a mensagem do usuário do terminal
            user_message = input("\x1b[33mVocê: \x1b[0m")
            
            if user_message.lower() in ["sair", "exit", "quit"]:
                print("\x1b[36mEncerrando o chat. Até logo!\x1b[0m")
                break

            # Envia a mensagem para o agente e aguarda a resposta
            response = await test_agent.arun(user_message)
            
            # Imprime a resposta do agente
            print(f"\x1b[34mAgente: \x1b[0m{response.content}")

    except Exception as e:
        print(f"\x1b[31mOcorreu um erro inesperado: {e}\x1b[0m")
        print("Verifique sua chave de API e a instalação das dependências.")

if __name__ == "__main__":
    # Executa a função principal assíncrona
    asyncio.run(main())
