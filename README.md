# MVPPromoAgente 🔍

MVP com OCR e Azure 100% - Promotional Material Analyzer

## 📋 Descrição

MVPPromoAgente é um agente de análise de materiais promocionais que utiliza OCR (Reconhecimento Óptico de Caracteres) através do Azure Computer Vision para extrair e analisar textos de imagens promocionais como panfletos, banners, anúncios e ofertas.

## ✨ Funcionalidades

- ✅ Extração de texto de imagens usando Azure Computer Vision OCR
- ✅ Análise de imagens locais e URLs
- ✅ Detecção automática de palavras-chave promocionais
- ✅ Identificação de preços e percentuais de desconto
- ✅ Geração de relatórios detalhados de análise
- ✅ Suporte para múltiplos idiomas (PT, EN, ES)
- ✅ Logging completo de operações
- ✅ Tratamento robusto de erros

## 🚀 Requisitos

- Python 3.7 ou superior
- Conta Azure com serviço Computer Vision ativo
- Chave de API e endpoint do Azure Computer Vision

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/ElaineMBarros/MVPPromoAgente.git
cd MVPPromoAgente
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as credenciais do Azure:
```bash
cp .env.template .env
```

4. Edite o arquivo `.env` com suas credenciais do Azure:
```
AZURE_COMPUTER_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_COMPUTER_VISION_KEY=your_subscription_key_here
```

## 🔧 Configuração do Azure

1. Acesse o [Portal do Azure](https://portal.azure.com/)
2. Crie um recurso de Computer Vision
3. Copie o endpoint e a chave de API
4. Cole as credenciais no arquivo `.env`

## 💻 Uso

### Uso Básico - Linha de Comando

Analise uma imagem local:
```bash
python promo_agent.py caminho/para/imagem.jpg
```

Analise uma imagem via URL:
```bash
python promo_agent.py https://exemplo.com/imagem.jpg --url
```

### Uso Programático

```python
from promo_agent import PromoAgent

# Inicializar o agente
agent = PromoAgent()

# Analisar imagem local
result = agent.analyze_promotional_image('promotional_flyer.jpg')

# Analisar imagem via URL
result = agent.analyze_promotional_image('https://example.com/promo.jpg', is_url=True)

# Gerar relatório
report = agent.generate_report(result)
print(report)
```

### Usando o Serviço OCR Diretamente

```python
from azure_ocr_service import AzureOCRService

# Inicializar o serviço
ocr_service = AzureOCRService()

# Extrair texto de imagem
result = ocr_service.extract_text_from_image('image.jpg')

if result['success']:
    print(f"Texto extraído: {result['text']}")
    print(f"Linhas detectadas: {result['line_count']}")
else:
    print(f"Erro: {result['error']}")
```

## 📊 Exemplo de Saída

```
============================================================
PROMOTIONAL MATERIAL ANALYSIS REPORT
============================================================

Source: promotional_flyer.jpg
Lines Detected: 15

------------------------------------------------------------
EXTRACTED TEXT:
------------------------------------------------------------
MEGA PROMOÇÃO
Desconto de 50%
Válido até 31/12/2025
R$ 99,90

------------------------------------------------------------
ANALYSIS:
------------------------------------------------------------
Word Count: 12
Character Count: 68
Is Promotional: Yes
Has Discount Info: Yes

Promotional Keywords Found: promoção, desconto, %
Prices Detected: R$ 99,90
Percentages Detected: 50%
============================================================
```

## 📁 Estrutura do Projeto

```
MVPPromoAgente/
├── azure_ocr_service.py    # Serviço de OCR do Azure
├── promo_agent.py           # Agente promocional principal
├── requirements.txt         # Dependências Python
├── .env.template           # Template de configuração
├── .gitignore              # Arquivos ignorados pelo Git
└── README.md               # Esta documentação
```

## 🔍 Módulos

### azure_ocr_service.py
Módulo responsável pela integração com Azure Computer Vision:
- `AzureOCRService`: Classe principal do serviço OCR
- `extract_text_from_image()`: Extrai texto de arquivo local
- `extract_text_from_url()`: Extrai texto de URL

### promo_agent.py
Agente de análise de materiais promocionais:
- `PromoAgent`: Classe principal do agente
- `analyze_promotional_image()`: Analisa material promocional
- `generate_report()`: Gera relatório formatado

## 🛠️ Tecnologias Utilizadas

- **Azure Computer Vision**: Serviço de OCR em nuvem
- **Python**: Linguagem de programação
- **azure-cognitiveservices-vision-computervision**: SDK do Azure
- **python-dotenv**: Gerenciamento de variáveis de ambiente
- **Pillow**: Processamento de imagens

## ⚠️ Tratamento de Erros

O sistema possui tratamento robusto de erros incluindo:
- Validação de credenciais do Azure
- Verificação de existência de arquivos
- Timeout de operações assíncronas
- Logging detalhado de erros

## 🔒 Segurança

- Credenciais armazenadas em arquivo `.env` (não versionado)
- `.gitignore` configurado para proteger informações sensíveis
- Validação de entrada de dados

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é um MVP (Minimum Viable Product) para demonstração.

## 👥 Autores

- Elaine M. Barros

## 📧 Suporte

Para questões e suporte, abra uma issue no GitHub.

## 🔄 Versão

**v1.0.0** - MVP com OCR e Azure 100% implementado
