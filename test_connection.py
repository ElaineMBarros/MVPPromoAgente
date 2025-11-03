#!/usr/bin/env python3
"""
Teste simples para verificar se o PromoAgente está funcionando
"""

import requests
import json
from datetime import datetime

def test_promoagente():
    """Testa as funcionalidades básicas do PromoAgente"""
    
    base_url = "http://localhost:7000"
    
    print("🧪 Testando PromoAgente Local...")
    print("=" * 50)
    
    try:
        # Teste 1: Página principal
        print("\n1. Testando página principal...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Página principal funcionando!")
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        else:
            print(f"❌ Erro na página principal: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão na página principal: {e}")
    
    try:
        # Teste 2: Status da API
        print("\n2. Testando API de status...")
        response = requests.get(f"{base_url}/status", timeout=10)
        if response.status_code == 200:
            print("✅ API de status funcionando!")
            try:
                status_data = response.json()
                print("   Status dos componentes:")
                for key, value in status_data.items():
                    status_icon = "✅" if value else "❌"
                    print(f"   {status_icon} {key}: {value}")
            except json.JSONDecodeError:
                print("   ⚠️  Resposta não é JSON válido")
        else:
            print(f"❌ Erro na API de status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão na API de status: {e}")
    
    try:
        # Teste 3: Chat simples (sem OpenAI)
        print("\n3. Testando funcionalidade de chat...")
        chat_data = {
            "message": "Olá, você está funcionando?",
            "session_id": "test_session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{base_url}/chat", 
                               json=chat_data, 
                               headers=headers, 
                               timeout=15)
        
        if response.status_code == 200:
            print("✅ API de chat respondendo!")
            try:
                chat_response = response.json()
                print(f"   Resposta: {chat_response.get('response', 'N/A')[:100]}...")
                print(f"   Session ID: {chat_response.get('session_id', 'N/A')}")
            except json.JSONDecodeError:
                print("   ⚠️  Resposta do chat não é JSON válido")
        else:
            print(f"❌ Erro na API de chat: {response.status_code}")
            if response.text:
                print(f"   Detalhes: {response.text[:200]}...")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão na API de chat: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")
    print("\n💡 Se o OpenAI estiver com erro, o agente ainda funcionará")
    print("   com respostas de fallback local.")

if __name__ == "__main__":
    test_promoagente()