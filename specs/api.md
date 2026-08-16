# API

Documentação dos endpoints expostos pelo backend RateSync.

**Base path:** `/api/v1`  
**Definido em:** `app/main.py` (linha 19)

---

## Autenticação

Nenhum endpoint exige autenticação no estado atual. `SecurityService` e `AuthService` existem no código mas **não estão conectados às rotas**.

---

## Endpoints REST

### `GET /api/v1/health`

Retorna o estado operacional da API backend.

**Arquivo:** `app/api/v1/routes.py`  
**Contrato (SDD 7.1):** `{ "status", "timestamp", "version" }`

#### Parâmetros

Nenhum.

#### Resposta de sucesso (`200`)

```json
{
  "status": "ok",
  "timestamp": "2026-08-16T00:35:18.506007+00:00",
  "version": "1.0.0"
}
```

---

### `GET /api/v1/ratings/{movie_id}`

Retorna avaliações consolidadas de um filme a partir de Cinemeta, OMDb e Letterboxd.

**Arquivo:** `app/api/v1/routes.py` (linhas 45–51)  
**Use case:** `GetMovieRatings.execute(movie_title)` — agrega Cinemeta, OMDb e Letterboxd em **paralelo** (`asyncio.gather(..., return_exceptions=True)`); falha isolada de uma fonte retorna `{"error": ...}` sem quebrar a resposta. Resultado cacheado em memória por `RATINGS_CACHE_TTL_SECONDS` (15m).

#### Parâmetros

| Nome | Local | Tipo | Descrição |
|------|-------|------|-----------|
| `movie_id` | path | `string` | Tratado como **título do filme** pelos clients (não é um ID numérico de banco) |

#### Resposta de sucesso (`200`)

```json
{
  "cinemeta": { ... },
  "omdb": [ ... ] | { "error": "..." },
  "letterboxd": { ... }
}
```

**Formato por fonte:**

**`cinemeta`** — objeto:
```json
{
  "title": "string",
  "rating": number | null,
  "year": number | null
}
```
Ou `{"error": "Movie not found"}` / `{"error": "mensagem"}`.

**`omdb`** — **lista** de objetos (formato heterogêneo):
```json
[
  {
    "rotten_tomatoes": {
      "movie_title": "string",
      "rating": "string",
      "source_name": "Rotten Tomatoes"
    }
  },
  {
    "metacritic": {
      "movie_title": "string",
      "rating": "string",
      "source_name": "Metacritic"
    }
  },
  {
    "imdb": {
      "title": "string",
      "rating": number | null,
      "vote_count": number | null,
      "year": "string",
      "source_name": "IMDB"
    }
  }
]
```
Ou `{"error": "Movie not found"}` / `{"error": "mensagem"}`.

**`letterboxd`** — objeto:
```json
{
  "title": "string",
  "rating": number,
  "year": number
}
```
Ou `{"error": "Movie not found"}` / `{"error": "mensagem"}`.

#### Erros

| Status | Condição |
|--------|----------|
| `500` | Qualquer exceção não tratada no use case (`HTTPException` com `detail=str(e)`) |

---

### `GET /api/v1/more_populars`

Retorna lista de filmes populares da Cinemeta (catálogo `top`).

**Arquivo:** `app/api/v1/routes.py` (linhas 43–49)  
**Use case:** `GetMorePopulars.execute()`

#### Parâmetros

Nenhum.

#### Resposta de sucesso (`200`)

Array de objetos:
```json
[
  {
    "title": "string",
    "overview": "string",
    "poster_path": "string | null"
  }
]
```

Ou objeto de erro:
```json
{"error": "mensagem"}
```

#### Erros

| Status | Condição |
|--------|----------|
| `500` | Exceção no use case |

---

### `GET /api/v1/movie/`

Busca filmes por título via Cinemeta.

**Arquivo:** `app/api/v1/routes.py` (linhas 51–57)  
**Use case:** `FindMovie.execute(movie_title)`

#### Parâmetros

| Nome | Local | Tipo | Obrigatório |
|------|-------|------|-------------|
| `movie_title` | query | `string` | Sim |

#### Resposta de sucesso (`200`)

Array de objetos:
```json
[
  {
    "title": "string",
    "overview": "string",
    "poster_path": "string | null"
  }
]
```

Ou objeto de erro:
```json
{"error": "Movie not found"}
```
```json
{"error": "mensagem de exceção"}
```

#### Erros

| Status | Condição |
|--------|----------|
| `500` | Exceção no use case |

---

## WebSocket

### `GET /api/v1/metrics`

Lightweight in-memory metrics for operational visibility. Returns counters produced by internal monitor (e.g., `letterboxd.failures`, `letterboxd.not_found`). Intended for dev/local monitoring and short-term troubleshooting — not a replacement for production metrics systems.

**Arquivo:** `app/api/v1/routes.py` (new)

**Resposta de sucesso (`200`):**

```json
{
  "letterboxd.failures": 3,
  "letterboxd.not_found": 10
}
```


## WebSocket

### `WS /api/v1/ws/find_movie/`

Busca filmes por título em tempo real. Mantém conexão aberta e processa múltiplas buscas em loop.

**Arquivo:** `app/api/v1/routes.py` (linhas 59–77)  
**Use case:** `FindMovie.execute(movie_title)`

#### Protocolo

1. Cliente conecta → servidor aceita (`websocket.accept()`).
2. Loop:
   - Cliente envia **texto plano** (`receive_text()`) com o título do filme.
   - Servidor executa busca e responde com JSON (`send_json()`).
3. Conexão encerrada no `finally` (`websocket.close()`).

#### Mensagem do cliente

Texto plano com o título do filme. Exemplo: `Inception`

#### Resposta do servidor

Mesmo formato do endpoint REST `GET /movie/`:

```json
[
  {"title": "...", "overview": "...", "poster_path": "..."}
]
```

Em caso de erro na busca:
```json
{"error": "mensagem"}
```

> Antes de enviar a resposta JSON de erro, o handler verifica explicitamente se o cliente permanece conectado via `websocket.client_state == WebSocketState.CONNECTED` (`starlette.websockets.WebSocketState`). Após o envio de `{"error": ...}`, o handler executa `break` e **encerra o loop**, fechando a conexão no bloco `finally`.

#### Eventos de desconexão

- `WebSocketDisconnect` — log via `print("WebSocket desconectado")`.
- Outras exceções — log via `print(f"Erro inesperado: {e}")`.

---

## Schemas Pydantic (definidos, não aplicados)

**Arquivo:** `app/api/v1/schemas.py`

### `MovieRatingResponse`

```python
class MovieRatingResponse(pydantic.BaseModel):
    cinemeta: MovieReviewSource | dict[str, str]
    omdb: list[dict] | dict[str, str]
    letterboxd: MovieReviewSource | dict[str, str]
```

Alinhado à resposta real de `get_movie_ratings` (2026-08-16).

### `MovieReviewSource`

```python
class MovieReviewSource(pydantic.BaseModel):
    title: str | None = None
    rating: float | str | None = None
    year: int | str | None = None
    error: str | None = None
```

Representa a estrutura de `cinemeta`/`letterboxd` (`{title, rating, year}`) e casos de erro (`{error}`).

**Nenhum desses schemas é usado** como `response_model` nas rotas — as respostas são dicts retornados diretamente pelos use cases.

---

## Códigos de status HTTP

| Status | Uso atual |
|--------|-----------|
| `200` | Respostas bem-sucedidas (incluindo respostas com `{"error": ...}` no body) |
| `500` | Exceções capturadas nos handlers REST |
| `401` | Definido em `SecurityService`, mas não exposto por nenhuma rota |

Não há tratamento explícito para `404` ou `422` nos endpoints atuais.

---

## CORS

Origens permitidas via `settings.CORS_ORIGINS` (`app/main.py`): dev local (`http://localhost:4200`, `http://localhost:8100`) e produção (`https://ratesync.vercel.app`). Origens fora da lista serão bloqueadas pelo browser.

---

## Integração com frontend (contexto externo)

Não identificado no código do backend. A integração é inferida apenas pelo CORS configurado para `https://ratesync.vercel.app`.
