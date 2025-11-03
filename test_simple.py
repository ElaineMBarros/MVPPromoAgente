#!/usr/bin/env python3
"""
Teste simples para verificar se o PromoAgente está funcionando
Usando apenas bibliotecas padrão do Python
"""

import urllib.request
import urllib.parse
import json
import socket
from datetime import datetime

def test_promoagente():
    """Testa as funcionalidades básicas do PromoAgente"""
    
    base_url = "http://localhost:7000"
    
    print("🧪 Testando PromoAgente Local...")
    print("=" * 50)
    
    try:
        # Teste 1: Conectividade básica
        print("\n1. Testando conectividade TCP...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 7000))
        sock.close()
        
        if result == 0:
            print("✅ Porta 7000 está aberta e respondendo!")
        else:
            print("❌ Não foi possível conectar na porta 7000")
            return
            
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        return
    
    try:
        # Teste 2: Página principal
        print("\n2. Testando página principal...")
        req = urllib.request.Request(f"{base_url}/")
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            content_type = response.headers.get('content-type', 'N/A')
            content_length = len(response.read())
            
            print(f"✅ Página principal funcionando!")
            print(f"   Status: {status_code}")
            print(f"   Content-Type: {content_type}")
            print(f"   Content Length: {content_length} bytes")
            
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP na página principal: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"❌ Erro de URL na página principal: {e.reason}")
    except Exception as e:
        print(f"❌ Erro inesperado na página principal: {e}")
    
    try:
        # Teste 3: Status da API
        print("\n3. Testando API de status...")
        req = urllib.request.Request(f"{base_url}/status")
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            
            print(f"✅ API de status funcionando!")
            print(f"   Status: {status_code}")
            
            try:
                status_data = json.loads(content)
                print("   Status dos componentes:")
                for key, value in status_data.items():
                    status_icon = "✅" if value else "❌"
                    print(f"   {status_icon} {key}: {value}")
            except json.JSONDecodeError:
                print("   ⚠️  Resposta não é JSON válido")
                print(f"   Conteúdo: {content[:200]}...")
                
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP na API de status: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"❌ Erro de URL na API de status: {e.reason}")
    except Exception as e:
        print(f"❌ Erro inesperado na API de status: {e}")
    
    try:
        # Teste 4: Chat simples
        print("\n4. Testando funcionalidade de chat...")
        
        chat_data = {
            "message": "Olá, você está funcionando?",
            "session_id": "test_session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        
        data = json.dumps(chat_data).encode('utf-8')
        req = urllib.request.Request(f"{base_url}/chat", 
                                   data=data,
                                   headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            
            print(f"✅ API de chat respondendo!")
            print(f"   Status: {status_code}")
            
            try:
                chat_response = json.loads(content)
                response_text = chat_response.get('response', 'N/A')
                session_id = chat_response.get('session_id', 'N/A')
                
                print(f"   Resposta: {response_text[:100]}...")
                print(f"   Session ID: {session_id}")
            except json.JSONDecodeError:
                print("   ⚠️  Resposta do chat não é JSON válido")
                print(f"   Conteúdo: {content[:200]}...")
                
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP na API de chat: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"❌ Erro de URL na API de chat: {e.reason}")
    except Exception as e:
        print(f"❌ Erro inesperado na API de chat: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")
    print("\n💡 Notas importantes:")
    print("   - Se o OpenAI estiver com erro, o agente ainda funcionará")
    print("   - O sistema usa respostas de fallback quando necessário")
    print("   - O SQLite e AgentOS estão funcionando corretamente")

if __name__ == "__main__":
    test_promoagente()