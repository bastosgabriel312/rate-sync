# Testes

Documentação do estado atual de testes automatizados no backend RateSync.

## Resumo

Suíte `pytest` criada em `tests/` em 2026-08-16 durante a refatoração Phase 2.

## Framework

- `pytest` + `pytest-asyncio` (modo `auto`) + `httpx` (TestClient FastAPI).
- Dependências de desenvolvimento em `requirements-dev.txt`.
- Configuração em `pytest.ini` (`asyncio_mode = auto`, `testpaths = tests`).

## Suíte atual (11 testes)

| Arquivo | Cobertura |
|---------|-----------|
| `tests/test_cache.py` | `TTLCache`: set/get, TTL por item, expiração, evicção LRU |
| `tests/test_use_cases.py` | `GetMovieRatings` (agregação, isolamento de falha, cache), `FindMovie` (cache) com clients mockados |
| `tests/test_routes.py` | `GET /api/v1/health`, `GET /api/v1/ratings/{movie_id}` (chamada real externa) |

## Como rodar

```bash
python -m pytest
```

## Cobertura aparente

| Área | Cobertura |
|------|-----------|
| Cache (`app/core/cache.py`) | ✔ Testado |
| Use cases (`GetMovieRatings`, `FindMovie`) | ✔ Testado (com mocks) |
| Endpoints REST (`health`, `ratings`) | ✔ Testado |
| WebSocket | ✘ Sem teste automatizado (validado manualmente) |
| API clients reais (Cinemeta, OMDb, Letterboxd) | ✘ Não mockados (rotas usam chamada real) |
| Normalização (OMDb `sanitize_number`, Letterboxd `sanitize`) | ✘ |
| Configuração / Settings | ✘ |

## Observações

- Testes de use cases usam cache dedicado (`TTLCache()` por instância) para não depender do `shared_cache` global (populado por testes de rota reais).
- `tests/test_routes.py::test_ratings_returns_three_sources` faz chamada externa real — depende de rede e da chave OMDb do ambiente (no dev, `OMDB_API_KEY=test_key` faz o OMDb retornar `{"error": ...}`, o que valida a resiliência).
- Bug de tipagem `dict[str:MovieReviewSource]` corrigido em 2026-08-16; cobre a implicação anterior de falta de CI/linter para erros de tipo.