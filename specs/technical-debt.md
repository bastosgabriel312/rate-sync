# Débitos Técnicos

Registro dos débitos técnicos, limitações, pontos de falha e problemas identificados no código atual do backend RateSync.

---

## Código legado e untracked

| Arquivo | Estado | Decisão | Justificativa |
|---|---|---|---|
| `app/core/security.py` | Removido | DESCARTAR APÓS VALIDAÇÃO | Arquivo validado (sem referências, imports, testes ou consumidores nas rotas) e removido. |
| `app/infrastructure/services/auth_service.py` | Removido | DESCARTAR APÓS VALIDAÇÃO | Arquivo validado (sem referências, imports, testes ou consumidores nas rotas) e removido. |
| `app/infrastructure/api_clients/tmdb_client.py` | Removido | DESCARTAR APÓS VALIDAÇÃO | Migrado para `CinemetaClient` (sem API key). Validação completa em 2026-08-16: sem imports ativos em `routes.py` ou use cases, sem testes, dependência `tmdbv3api` removida de `requirements.txt`. Arquivo fisicamente removido. |

## Migração TMDB → Cinemeta

| Item | Detalhe |
|------|---------|
| Motivador | TMDB exige `TMDB_API_KEY` obrigatória (impede boot sem credencial); API paga inviabilizou alternativas (Trakt exige VIP desde ago/2026). |
| Novos arquivos | `app/infrastructure/api_clients/cinemeta_client.py` (httpx async, sem key) |
| Use cases atualizados | `find_movie.py`, `get_more_populars.py`, `get_movie_ratings.py` |
| Chave de resposta | `tmdb` → `cinemeta` em `GET /ratings/{movie_id}` (schema Pydantic atualizado em `schemas.py`) |
| Config | `TMDB_API_KEY` removida de `Settings`; adicionada `CINEMETA_BASE_URL` (default `https://v3-cinemeta.strem.io`) |
| Contrato de poster | `poster_path` agora é **URL completa** (ex.: `https://m.media-amazon.com/...`), não path relativo. O frontend que monta `https://image.tmdb.org/t/p/w500` + `poster_path` precisa ser atualizado. |
| `overview` na busca | Cinemeta `search` não retorna descrição → `overview` vazio (`""`) em `find_movie`. `more_populars` usa o catálogo `top` que inclui `description`. |
| Rating | `{title, rating, year}` — `rating` = `imdbRating` (float), `year` = `releaseInfo`. **Sem** `vote_count` (Cinemeta não fornece). Frontend precisa remover dependência de `reviews.tmdb.vote_count`. |
| `.env` | Se o `.env` local ainda contiver `TMDB_API_KEY`, o boot falha (`extra_forbidden`). Remover a variável do `.env`. |
| Dependência | `tmdbv3api` removida de `requirements.txt` (2026-08-16) — não utilizada após a migração. |
| Resolvido | Migração concluída em 2026-08-16: backend (`cinemeta` key), frontend (`reviews.cinemeta`, poster URL completa), specs globais e frontend atualizados. `tmdb_client.py` e `tmdbv3api` removidos. |

---

## Código morto / não integrado

| Componente | Arquivo | Problema |
|------------|---------|----------|
| `SecurityService` | `app/core/security.py` | Não referenciado por nenhuma rota. Referencia `settings.JWKS_URL` que não existe em `Settings`. |
| `AuthService` | `app/infrastructure/services/auth_service.py` | Não referenciado. Referencia `settings.TOKEN_URL`, `CLIENT_ID`, `CLIENT_SECRET` inexistentes em `Settings`. |
| `MovieRepository` | `app/domain/repositories/movie_repository.py` | ABC sem implementação concreta. |
| `MovieRatingResponse` | `app/api/v1/schemas.py` | Não usado como `response_model`. ~~Campos desatualizados~~ **Atualizado** (2026-08-16): `{cinemeta, omdb, letterboxd}` alinhado à resposta real. |
| `MovieReviewSource` | `app/api/v1/schemas.py` | ~~Importado em `get_movie_ratings.py` mas não utilizado~~ **Atualizado** (2026-08-16): representa a estrutura real de `cinemeta`/`letterboxd` (`{title, rating, year}`), usado como referência de contrato. |
| `rottentomatoes-python` | `requirements.txt` | Dependência instalada, não referenciada no código `app/`. |

---

## Bugs e erros de tipagem

| Local | Problema |
|-------|----------|
| ~~`app/domain/use_cases/get_movie_ratings.py:14`~~ | ~~Anotação inválida: `dict[str:MovieReviewSource]`~~ **Corrigido** (2026-08-16): assinatura agora é `dict[str, Any]`. |
| ~~`app/infrastructure/api_clients/letterboxd_client.py:14`~~ | ~~Anotação inválida `dict[str:any]`~~ **Corrigido** (2026-08-16): `dict[str, Any]`. |
| ~~`app/domain/repositories/movie_api_client.py:8` vs clients~~ | ~~Inconsistência `movie_id` vs `movie_title`~~ **Corrigido** (2026-08-16): ABC define `movie_title: str`. |
| `app/core/security.py:14` | `settings.JWKS_URL` — arquivo removido; referência residual. |
| `app/infrastructure/services/auth_service.py:10-12` | `settings.TOKEN_URL` — arquivo removido; referência residual. |

---

## Dependências ausentes ou inconsistentes

| Item | Detalhe |
|------|---------|
| `PyJWT` | Importado em `core/security.py` (`import jwt`), mas **não listado** em `requirements.txt`. Presente apenas no ambiente virtual local (`.venv2`). |
| `letterboxdpy` | Instalado via Git (commit fixo), sem versão semver. Atualizações upstream podem quebrar silenciosamente. |

---

## Segurança

| Problema | Detalhe | Severidade |
|----------|---------|------------|
| Endpoints públicos | Nenhuma rota exige autenticação | Média (depende do contexto de deploy) |
| JWT sem verificação de assinatura | `jwt.decode(token, options={"verify_signature": False})` em `SecurityService` | Alta (se auth for ativada) |
| Issuer hardcoded | URL do Cognito fixa no código (`sa-east-1_S28wSp1EG`) | Média |
| OMDb via HTTP | `http://www.omdbapi.com/` — tráfego sem TLS | Média |
| CORS | ~~Apenas `https://ratesync.vercel.app`~~ **Corrigido** (2026-08-16): `CORS_ORIGINS` inclui `localhost:4200`, `localhost:8100`, Vercel | Baixa (bloqueia dev local) |
| Exposição de erros internos | `HTTPException(status_code=500, detail=str(e))` — mensagens de exceção expostas ao cliente | Baixa-Média |

---

## Arquitetura e design

| Problema | Impacto |
|----------|---------|
| ~~`async` sem benefício real~~ | ~~Clients OMDb e Letterboxd usam libs síncronas~~ **Corrigido** (2026-08-16): OMDb agora usa `httpx.AsyncClient`; Letterboxd usa `asyncio.to_thread` (lib `letterboxdpy` é síncrona). |
| ~~Chamadas sequenciais em ratings~~ | ~~3 APIs consultadas em série~~ **Corrigido** (2026-08-16): `asyncio.gather(..., return_exceptions=True)` com isolamento de falha por fonte. |
| ~~Sem cache~~ | ~~Mesma consulta repetida gera novas chamadas~~ **Corrigido** (2026-08-16): `app/core/cache.py` (TTLCache LRU, thread-safe). Busca 1h, ratings 15m. |
| Sem persistência | Indisponibilidade de API externa = falha total para aquele dado. |
| Parâmetro `movie_id` é título | Nome enganoso; sem ID canônico entre fontes. |
| Cinemeta usa primeiro resultado | Título ambíguo pode retornar filme errado. |
| Sem `vote_count` | Cinemeta não fornece votos; resposta `cinemeta` traz `{title, rating, year}`. |
| OMDb exige título exato | Parâmetro `t` não faz busca parcial. |
| Formato de resposta heterogêneo | `omdb` retorna lista; `cinemeta` e `letterboxd` retornam dict. Erros também variam (dict em todas as fontes, mas omdb em sucesso é lista). |
| Schemas Pydantic não aplicados | ~~Sem validação de contrato de saída~~ **Parcial** (2026-08-16): schemas alinhados à resposta real; ainda não usados como `response_model` (mantém contrato flexível entre fontes). |
| Singletons no módulo | Clients instanciados no import de `routes.py`; dificulta testes e configuração por request. |

---

## WebSocket

| Problema | Arquivo | Detalhe |
|----------|---------|---------|
| Conexão encerra após erro | `routes.py:71` | `break` após enviar `{"error": ...}` — cliente precisa reconectar. |
| Sem heartbeat/ping | `routes.py` | Conexões idle podem ser encerradas por proxies sem aviso. |
| Log via `print` | `routes.py:73-75` | Sem logging estruturado. |
| `receive_text` sem validação | `routes.py:64` | Título vazio ou malformado é repassado diretamente à Cinemeta. |

---

## Pontos de falha

### APIs externas

| Fonte | Modo de falha | Comportamento no backend |
|-------|---------------|--------------------------|
| Cinemeta | Busca 404/título ambíguo/rate limit | `{"error": "mensagem"}` no body (status 200) ou HTTP 500 se exceção escapar |
| OMDb | Título não encontrado, API key inválida | `{"error": "Movie not found"}` ou `{"error": "mensagem"}` |
| Letterboxd | Site mudou HTML, título não encontrado | `{"error": "mensagem"}` + `print(e)` |
| Cognito (se ativado) | Config ausente | `AttributeError` na instanciação |

### Configuração

| Condição | Resultado |
|----------|-----------|
| `TMDB_API_KEY` no `.env` | Variável não declarada em `Settings` causa `extra_forbidden` na inicialização |
| `OMDB_API_KEY` ausente | Falha na inicialização de `Settings` |
| `.env` ausente | Depende de variáveis de ambiente do sistema |

### Deploy

| Condição | Resultado |
|----------|-----------|
| CORS origin diferente do frontend | Browser bloqueia requisições |
| WebSocket atrás de proxy mal configurado | Conexão pode falhar |

---

## Limitações funcionais atuais

- Apenas filmes (Cinemeta `search`/`top` e OMDb `t`); séries não são tratadas de forma diferenciada.
- Sem paginação nos resultados de busca Cinemeta.
- Sem filtro por ano, idioma ou tipo de mídia.
- Sem documentação OpenAPI customizada além do padrão FastAPI.
- Sem versionamento formal de contrato de API.
- Sem rate limiting no backend.

---

## Manutenção

| Problema | Detalhe |
|----------|---------|
| ~~Zero testes~~ | ~~Regressões não detectadas automaticamente~~ **Corrigido** (2026-08-16): suíte criada em `tests/` (`test_cache.py`, `test_use_cases.py`, `test_routes.py`) — 11 testes, `pytest` + `pytest-asyncio` + `httpx`. Dependências em `requirements-dev.txt`. |
| Zero CI no repositório | Não identificado no código analisado |
| Dependência Git para Letterboxd | Reprodutibilidade depende do commit fixo no `requirements.txt` |
| `.venv2` no repositório | Ambiente virtual presente no diretório do projeto (não deveria ser versionado — verificar `.gitignore`) |

---

## Débitos por prioridade (observação factual, não proposta)

Esta seção lista débitos por impacto observado, sem recomendar soluções.

| Prioridade | Débito |
|------------|--------|
| Alta | ~~Ausência total de testes~~ **Resolvido** (2026-08-16): 11 testes |
| Alta | `PyJWT` ausente de `requirements.txt` com código que o importa |
| Alta | Settings incompleto para módulos de auth existentes |
| Média | ~~Async bloqueante em clients~~ **Resolvido** (2026-08-16): OMDb httpx async; Letterboxd `to_thread` |
| Média | Formato de resposta inconsistente (OMDb lista vs dict) |
| Média | WebSocket encerra conexão após erro |
| Média | ~~Sem cache — dependência total de APIs externas~~ **Resolvido** (2026-08-16): TTL cache busca 1h / ratings 15m |
| Baixa | `rottentomatoes-python` não utilizado |
| Baixa | ~~Schemas Pydantic não aplicados~~ **Parcial** (2026-08-16): schemas alinhados; não usados como `response_model` |
| Baixa | Logs via `print` em vez de logging |
