# PromoAgente Frontend

Aplicação React + Vite responsável pela interface web do PromoAgente GERA.

## Requisitos

- Node.js 18+
- npm 9+
- Backend FastAPI rodando (porta padrão `7000`)

## Instalação

```bash
cd frontend
npm install
```

## Variáveis de ambiente

Crie um arquivo `.env` na pasta `frontend` (ou `.env.local`) com a URL do backend, se necessário:

```
VITE_API_BASE_URL=http://localhost:7000
```

## Execução

Servidor de desenvolvimento:

```bash
npm run dev
```

Build para produção:

```bash
npm run build
npm run preview
```

## Estrutura

- `src/components`: componentes reutilizáveis (chat, histórico, status)
- `src/services`: cliente HTTP e integração com a API FastAPI/Agno
- `src/types`: definições TypeScript compartilhadas
- `src/styles`: estilo global e tipagem de tema

O layout utiliza um tema clean em tons de branco/azul e exibe o logo da GERA carregado via `/logo_gera.png` exposto pelo backend Python.
