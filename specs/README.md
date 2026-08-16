# RateSync Backend — Especificações Técnicas

Documentação do **estado atual** do backend RateSync, baseada exclusivamente no código existente em `rate-sync/`.

## Sobre o projeto

O RateSync é uma API em Python/FastAPI que agrega informações e avaliações de filmes a partir de fontes externas (Cinemeta, OMDb e Letterboxd). Os dados são consultados **em tempo real** a cada requisição — não há persistência local de filmes ou ratings.

## Localização do código

```
rate-sync/
├── app/
│   ├── main.py
│   ├── api/v1/
│   ├── core/
│   ├── domain/
│   └── infrastructure/
├── requirements.txt
├── README.md
└── specs/          ← esta documentação
```

> **Nota:** O diretório `./backend/` não existe no workspace. O backend está em `rate-sync/`.

## Índice da documentação

| Documento | Conteúdo |
|-----------|----------|
| [architecture.md](./architecture.md) | Camadas, módulos, fluxo de dados e dependências entre componentes |
| [api.md](./api.md) | Endpoints REST e WebSocket, contratos de request/response |
| [database.md](./database.md) | Persistência e armazenamento de dados |
| [scraper.md](./scraper.md) | Integrações externas, scraping e normalização |
| [testing.md](./testing.md) | Testes automatizados e cobertura |
| [technical-debt.md](./technical-debt.md) | Débitos técnicos, limitações e pontos de falha |
| [deployment.md](./deployment.md) | Configuração, variáveis de ambiente e deploy |

## Stack resumida

| Item | Valor |
|------|-------|
| Linguagem | Python |
| Framework | FastAPI 0.112.2 |
| Servidor ASGI | Uvicorn 0.30.6 (referenciado no README) |
| Validação/config | Pydantic 2.7 / pydantic-settings 2.4 |
| Gerenciador de pacotes | pip (`requirements.txt`) |

## Endpoints ativos

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/health` | Health check (status, timestamp, versão) |
| `GET` | `/api/v1/ratings/{movie_id}` | Ratings consolidados de Cinemeta, OMDb e Letterboxd |
| `GET` | `/api/v1/more_populars` | Filmes populares da Cinemeta |
| `GET` | `/api/v1/movie/?movie_title=` | Busca de filmes por título (REST) |
| `WS` | `/api/v1/ws/find_movie/` | Busca de filmes por título (WebSocket) |

## Variáveis de ambiente

| Variável | Uso | Obrigatória |
|----------|-----|-------------|
| `OMDB_API_KEY` | Cliente OMDb | Sim |
| `CINEMETA_BASE_URL` | Base URL da Cinemeta (padrão `https://v3-cinemeta.strem.io`) | Não |

Carregadas via `python-dotenv` e `pydantic-settings` em `app/core/config.py`.

## O que este backend **não** possui (confirmado no código)

- Banco de dados
- Cache ou fila de mensagens
- Autenticação ativa nos endpoints
- Testes automatizados
- Arquivos de deploy (Dockerfile, Procfile, etc.) no repositório
