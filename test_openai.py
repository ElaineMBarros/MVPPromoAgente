#!/usr/bin/env python3
"""
Teste da conexão OpenAI com a nova versão
"""

import asyncio
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

async def test_openai():
    """Testa a conexão com OpenAI"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    print("🧪 Testando OpenAI v2.6.1...")
    print("=" * 40)
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ OPENAI_API_KEY não encontrada no .env")
            return False
        
        print(f"✅ API Key encontrada: {api_key[:12]}...")
        
        # Criar cliente OpenAI
        client = AsyncOpenAI(
            api_key=api_key
        )
        
        print("✅ Cliente OpenAI criado com sucesso!")
        
        # Testar uma requisição simples
        print("🔄 Testando requisição para OpenAI...")
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Responda apenas: OK"}],
            max_tokens=5
        )
        
        response_text = response.choices[0].message.content
        print(f"✅ Resposta recebida: {response_text}")
        
        # Fechar cliente
        await client.close()
        print("✅ Cliente OpenAI fechado corretamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"   Tipo: {type(e).__name__}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai())
    
    if result:
        print("\n🎉 OpenAI está funcionando perfeitamente!")
    else:
        print("\n❌ Ainda há problemas com OpenAI")