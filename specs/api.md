# API

Documentação dos endpoints expostos pelo backend RateSync.

**Base path:** `/api/v1`  
**Definido em:** `app/main.py` (linha 19)

---

## Autenticação

Nenhum endpoint exige autenticação no estado atual. `SecurityService` e `AuthService` existem no código mas **não estão conectados às rotas**.

---

## Endpoints REST

### `GET /api/v1/ratings/{movie_id}`

Retorna avaliações consolidadas de um filme a partir de TMDB, OMDb e Letterboxd.

**Arquivo:** `app/api/v1/routes.py` (linhas 35–41)  
**Use case:** `GetMovieRatings.execute(movie_id)`

#### Parâmetros

| Nome | Local | Tipo | Descrição |
|------|-------|------|-----------|
| `movie_id` | path | `string` | Tratado como **título do filme** pelos clients (não é um ID numérico de banco) |

#### Resposta de sucesso (`200`)

```json
{
  "tmdb": { ... },
  "omdb": [ ... ] | { "error": "..." },
  "letterboxd": { ... }
}
```

**Formato por fonte:**

**`tmdb`** — objeto:
```json
{
  "title": "string",
  "rating": number,
  "vote_count": number
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

Retorna lista de filmes populares do TMDB.

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

Busca filmes por título via TMDB.

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
    omdb: dict
    tmdb: dict
    rotten_tomatoes: dict
```

**Não é usado** como `response_model` em nenhuma rota. O campo `rotten_tomatoes` não corresponde à resposta real (ratings do Rotten Tomatoes vêm dentro de `omdb`).

### `MovieReviewSource`

```python
class MovieReviewSource(pydantic.BaseModel):
    title: str
    rating: float | str | None
    year: int | str | None
    error: str | None
```

Importado em `get_movie_ratings.py` mas **não utilizado** para validação ou serialização da resposta.

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

Apenas origem `https://ratesync.vercel.app` é permitida (`app/main.py`). Requisições de outras origens serão bloqueadas pelo browser.

---

## Integração com frontend (contexto externo)

Não identificado no código do backend. A integração é inferida apenas pelo CORS configurado para `https://ratesync.vercel.app`.
