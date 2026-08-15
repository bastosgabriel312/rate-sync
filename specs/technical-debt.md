# Débitos Técnicos

Registro dos débitos técnicos, limitações, pontos de falha e problemas identificados no código atual do backend RateSync.

---

## Código morto / não integrado

| Componente | Arquivo | Problema |
|------------|---------|----------|
| `SecurityService` | `app/core/security.py` | Não referenciado por nenhuma rota. Referencia `settings.JWKS_URL` que não existe em `Settings`. |
| `AuthService` | `app/infrastructure/services/auth_service.py` | Não referenciado. Referencia `settings.TOKEN_URL`, `CLIENT_ID`, `CLIENT_SECRET` inexistentes em `Settings`. |
| `MovieRepository` | `app/domain/repositories/movie_repository.py` | ABC sem implementação concreta. |
| `MovieRatingResponse` | `app/api/v1/schemas.py` | Não usado como `response_model`. Campos desatualizados (`rotten_tomatoes` em vez de estrutura real). |
| `MovieReviewSource` | `app/api/v1/schemas.py` | Importado em `get_movie_ratings.py` mas não utilizado. |
| `rottentomatoes-python` | `requirements.txt` | Dependência instalada, não referenciada no código `app/`. |

---

## Bugs e erros de tipagem

| Local | Problema |
|-------|----------|
| `app/domain/use_cases/get_movie_ratings.py:14` | Anotação inválida: `dict[str:MovieReviewSource]` (sintaxe incorreta; deveria ser `dict[str, MovieReviewSource]`). |
| `app/infrastructure/api_clients/tmdb_client.py:41` | Anotação inválida: `dict[str:str]`. |
| `app/infrastructure/api_clients/tmdb_client.py:30` | Anotação com tipo duplicado: `list[Any] | dict[str, str] | dict[str, str]`. |
| `app/infrastructure/api_clients/tmdb_client.py:16` | Uso de `any` (built-in) como tipo em `dict[str, any]`; o correto é `typing.Any`. |
| `app/infrastructure/api_clients/letterboxd_client.py:14` | Anotação inválida e uso de `any` (built-in): `dict[str:any]`; o correto é `dict[str, Any]`. |
| `app/domain/repositories/movie_api_client.py:8` vs clients | Inconsistência de parâmetro: `MovieAPIClient.get_movie_rating` define `movie_id: str`, enquanto `TMDBClient`, `OMDBClient` e `LetterBoxdClient` declaram `movie_title: str`. |
| `app/core/security.py:14` | `settings.JWKS_URL` — atributo não definido em `Settings`. Causaria `AttributeError` se instanciado. |
| `app/infrastructure/services/auth_service.py:10-12` | `settings.TOKEN_URL`, `CLIENT_ID`, `CLIENT_SECRET` — atributos não definidos em `Settings`. |

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
| CORS restritivo | Apenas `https://ratesync.vercel.app` | Baixa (bloqueia dev local) |
| Exposição de erros internos | `HTTPException(status_code=500, detail=str(e))` — mensagens de exceção expostas ao cliente | Baixa-Média |

---

## Arquitetura e design

| Problema | Impacto |
|----------|---------|
| `async` sem benefício real | Clients usam libs síncronas (`requests`, `tmdbv3api`). Event loop bloqueado durante chamadas externas. |
| Chamadas sequenciais em ratings | 3 APIs consultadas em série; latência = soma dos tempos individuais. |
| Sem cache | Mesma consulta repetida gera novas chamadas a todas as fontes. |
| Sem persistência | Indisponibilidade de API externa = falha total para aquele dado. |
| Parâmetro `movie_id` é título | Nome enganoso; sem ID canônico entre fontes. |
| TMDB usa primeiro resultado | Título ambíguo pode retornar filme errado. |
| OMDb exige título exato | Parâmetro `t` não faz busca parcial. |
| Formato de resposta heterogêneo | `omdb` retorna lista; `tmdb` e `letterboxd` retornam dict. Erros também variam (dict em todas as fontes, mas omdb em sucesso é lista). |
| Schemas Pydantic ignorados | Sem validação de contrato de saída. |
| Singletons no módulo | Clients instanciados no import de `routes.py`; dificulta testes e configuração por request. |

---

## WebSocket

| Problema | Arquivo | Detalhe |
|----------|---------|---------|
| Conexão encerra após erro | `routes.py:71` | `break` após enviar `{"error": ...}` — cliente precisa reconectar. |
| Sem heartbeat/ping | `routes.py` | Conexões idle podem ser encerradas por proxies sem aviso. |
| Log via `print` | `routes.py:73-75` | Sem logging estruturado. |
| `receive_text` sem validação | `routes.py:64` | Título vazio ou malformado é repassado diretamente ao TMDB. |

---

## Pontos de falha

### APIs externas

| Fonte | Modo de falha | Comportamento no backend |
|-------|---------------|--------------------------|
| TMDB | API key inválida, rate limit, timeout | `{"error": "mensagem"}` no body (status 200) ou HTTP 500 se exceção escapar |
| OMDb | Título não encontrado, API key inválida | `{"error": "Movie not found"}` ou `{"error": "mensagem"}` |
| Letterboxd | Site mudou HTML, título não encontrado | `{"error": "mensagem"}` + `print(e)` |
| Cognito (se ativado) | Config ausente | `AttributeError` na instanciação |

### Configuração

| Condição | Resultado |
|----------|-----------|
| `TMDB_API_KEY` ausente | Falha na inicialização de `Settings` (Pydantic validation error) |
| `OMDB_API_KEY` ausente | Falha na inicialização de `Settings` |
| `.env` ausente | Depende de variáveis de ambiente do sistema |

### Deploy

| Condição | Resultado |
|----------|-----------|
| CORS origin diferente do frontend | Browser bloqueia requisições |
| WebSocket atrás de proxy mal configurado | Conexão pode falhar |

---

## Limitações funcionais atuais

- Apenas filmes (TMDB `Search.movies` e OMDb `t`); séries não são tratadas de forma diferenciada.
- Sem paginação nos resultados de busca TMDB.
- Sem filtro por ano, idioma ou tipo de mídia.
- Sem endpoint de health check (`/health`, `/ready`).
- Sem documentação OpenAPI customizada além do padrão FastAPI.
- Sem versionamento formal de contrato de API.
- Sem rate limiting no backend.

---

## Manutenção

| Problema | Detalhe |
|----------|---------|
| Zero testes | Regressões não detectadas automaticamente |
| Zero CI no repositório | Não identificado no código analisado |
| Dependência Git para Letterboxd | Reprodutibilidade depende do commit fixo no `requirements.txt` |
| `.venv2` no repositório | Ambiente virtual presente no diretório do projeto (não deveria ser versionado — verificar `.gitignore`) |

---

## Débitos por prioridade (observação factual, não proposta)

Esta seção lista débitos por impacto observado, sem recomendar soluções.

| Prioridade | Débito |
|------------|--------|
| Alta | Ausência total de testes |
| Alta | `PyJWT` ausente de `requirements.txt` com código que o importa |
| Alta | Settings incompleto para módulos de auth existentes |
| Média | Async bloqueante em clients |
| Média | Formato de resposta inconsistente (OMDb lista vs dict) |
| Média | WebSocket encerra conexão após erro |
| Média | Sem cache — dependência total de APIs externas em tempo real |
| Baixa | `rottentomatoes-python` não utilizado |
| Baixa | Schemas Pydantic não aplicados |
| Baixa | Logs via `print` em vez de logging |
