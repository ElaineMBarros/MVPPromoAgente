#!/usr/bin/env python3
"""
Teste isolado do OpenAI para identificar o problema
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_openai_isolated():
    """Testa OpenAI isoladamente"""
    
    print("🔬 Teste isolado do OpenAI...")
    
    try:
        # Carregar env
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        print(f"✅ API Key: {api_key[:12]}...")
        
        # Importar e testar OpenAI
        from openai import AsyncOpenAI
        
        print("✅ Importação OK")
        
        # Criar cliente sem argumentos extras
        client = AsyncOpenAI(
            api_key=api_key
        )
        
        print("✅ Cliente criado")
        
        # Teste simples
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Responda apenas: FUNCIONANDO"}],
            max_tokens=5
        )
        
        print(f"✅ Resposta: {response.choices[0].message.content}")
        
        await client.close()
        print("✅ Cliente fechado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print(f"   Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openai_isolated())
    print(f"\nResultado: {'✅ SUCESSO' if result else '❌ FALHOU'}")