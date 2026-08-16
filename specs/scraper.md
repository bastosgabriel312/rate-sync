# Scraping e Integrações Externas

Documentação das fontes de dados externas, mecanismos de coleta e normalização no backend RateSync.

## Visão geral

O backend não possui um módulo de scraping dedicado. A coleta de dados ocorre via **três clients de infraestrutura** em `app/infrastructure/api_clients/`, cada um com mecanismo diferente:

| Client | Arquivo | Mecanismo | Biblioteca |
|--------|---------|-----------|------------|
| `CinemetaClient` | `cinemeta_client.py` | REST HTTP (GET) | `httpx` 0.27.2 |
| `OMDBClient` | `omdb_client.py` | API REST (HTTP GET) | `requests` 2.32.3 |
| `LetterBoxdClient` | `letterboxd_client.py` | Scraping (via lib) | `letterboxdpy` (Git) |

## CinemetaClient

**Arquivo:** `app/infrastructure/api_clients/cinemeta_client.py`

### Configuração

- Base URL: `settings.CINEMETA_BASE_URL` (padrão: `https://v3-cinemeta.strem.io`).
- **Sem API key.** A Cinemeta (addon Stremio) não exige credencial.
- Cliente HTTP assíncrono: `httpx.AsyncClient(follow_redirects=True)`.

### Endpoints consumidos

| Operação | Endpoint Cinemeta | Retorno |
|----------|-------------------|---------|
| `get_movie_rating(movie_title)` | `GET /catalog/movie/top/search={query}.json` → primeiro resultado → `GET /meta/movie/{imdb_id}.json` | `{title, rating, year}` |
| `find_movie(movie_title)` | `GET /catalog/movie/top/search={query}.json` | `[{title, overview, poster_path}, ...]` |
| `find_more_populars()` | `GET /catalog/movie/top.json` (redireciona para `cinemeta-catalogs.strem.io`) | `[{title, overview, poster_path}, ...]` |

### Normalização

- `rating` vem do campo `imdbRating` (string) convertido para `float`; `None` se ausente/`N/A`.
- `year` vem de `releaseInfo` convertido para `int`.
- `poster_path` recebe o valor **URL completa** de `poster` da Cinemeta (ex.: `https://m.media-amazon.com/...`) — **não** é um path relativo como no TMDB.
- `overview` usa `description` quando presente; nas buscas (`search`) a Cinemeta não retorna descrição, então `overview` vem vazio (`""`).

### Comportamento em erro

- Filme não encontrado: `{"error": "Movie not found"}`
- Exceção: `{"error": str(e)}`
- Usa sempre o **primeiro resultado** da busca para ratings (mesma heurística do TMDB antigo; título ambíguo pode retornar filme errado).

### Dependência externa (nota)

A Cinemeta é um addon mantido pela comunidade Stremio. A busca é exposta via `catalog` com extra `search` (o manifest **não** declara recurso `search` próprio). Redirecionamentos (307) para `cinemeta-catalogs.strem.io` são seguidos automaticamente.

---

## OMDBClient

**Arquivo:** `app/infrastructure/api_clients/omdb_client.py`

### Configuração

- API key: `settings.OMDB_API_KEY`
- Base URL: `http://www.omdbapi.com/` (HTTP, não HTTPS)

### Operação

`get_movie_rating(movie_title)`:

1. `GET` com params `t={movie_title}` e `apikey={OMDB_API_KEY}`.
2. Se `Response == 'True'`:
   - Extrai ratings de `data['Ratings']` via `get_ratings()`.
   - Adiciona bloco IMDB separado com dados de `imdbRating`, `imdbVotes`, `Year`.
   - Adiciona a propriedade `"source_name"` a cada objeto de avaliação retornado (ex: `"Rotten Tomatoes"`, `"Metacritic"`, `"IMDB"`).
3. Retorna **lista** de dicts.

### Normalização (`get_ratings`)

**Arquivo:** `omdb_client.py`, linhas 34–51

Mapeamento de fontes OMDb:

| Source (OMDb) | Chave no response |
|---------------|-------------------|
| `Internet Movie Database` | `imdb` (excluído desta lista — adicionado separadamente) |
| `Rotten Tomatoes` | `rotten_tomatoes` |
| `Metacritic` | `metacritic` |
| Outros | Nome original da source |

Transformação de valores:
```python
rating['Value'].replace('%', '').replace('/100', '')
```
- Remove `%` e `/100` dos valores (ex: `"87%"` → `"87"`, `"75/100"` → `"75"`).
- Ratings permanecem como **string** após normalização (exceto IMDB rating/vote_count).

### Normalização (`sanitize_number`)

**Arquivo:** `omdb_client.py`, linhas 53–59

| Entrada | Flag | Saída |
|---------|------|-------|
| `'N/A'` | qualquer | `None` |
| `"1,234,567"` | `is_int=True` | `1234567` (int) |
| `"8.5"` | `is_float=True` | `8.5` (float) |

Aplicado a `imdbRating` (float) e `imdbVotes` (int).

### Comportamento em erro

- Filme não encontrado: `{"error": "Movie not found"}`
- Exceção: `{"error": str(e)}`

### Busca por título exato

OMDb usa parâmetro `t` (título exato), não busca parcial. Títulos imprecisos tendem a falhar.

---

## LetterBoxdClient

**Arquivo:** `app/infrastructure/api_clients/letterboxd_client.py`

### Mecanismo

Utiliza `letterboxdpy.movie.Movie`, que realiza **scraping** do site Letterboxd (não é API oficial).

Dependência instalada via Git:
```
letterboxdpy @ git+https://github.com/nmcassa/letterboxdpy.git@9ac7d0c4c66822e10a9a18011cfe8156dcf7640e
```

Dependências transitivas relevantes em `requirements.txt`: `beautifulsoup4`, `lxml`.

### Operação

`get_movie_rating(movie_title)`:

1. Sanitiza o título via `sanitize()`.
2. Instancia `Movie(sanitized_title)`.
3. Retorna `{title, rating, year}`.

### Normalização (`sanitize`)

**Arquivo:** `letterboxd_client.py`, linhas 28–33

```
1. unicodedata.normalize('NFKD', title)
2. Remove caracteres não-ASCII
3. Remove caracteres especiais (mantém a-z, A-Z, 0-9, espaços)
4. Substitui espaços por hífens
5. Lowercase
6. Remove hífens duplicados
```

Exemplo: `"Cidade de Deus"` → `"cidade-de-deus"`

### Comportamento em erro

- Exceção: `print(e)` no stdout + `{"error": str(e)}`
- Filme não encontrado: `{"error": "Movie not found"}` (se `movie_request` for falsy)

### Fragilidade

O scraping depende da estrutura HTML do Letterboxd. Mudanças no site ou na lib `letterboxdpy` podem quebrar a integração sem aviso.

---

## Biblioteca não utilizada

| Pacote | Versão em requirements.txt | Uso no código |
|--------|------------------------------|---------------|
| `rottentomatoes-python` | 0.6.5 | **Não referenciado** em nenhum arquivo em `app/` |

Ratings do Rotten Tomatoes são obtidos via OMDb, não via este pacote.

---

## Fluxo de consolidação (GetMovieRatings)

**Arquivo:** `app/domain/use_cases/get_movie_ratings.py`

```
execute(movie_title)
  ├── cinemeta_client.get_movie_rating(movie_title)  → dict
  ├── omdb_client.get_movie_rating(movie_title)      → list | dict
  └── letterboxd_client.get_movie_rating(movie_title) → dict

  return {
    "cinemeta": cinemeta_rating,
    "omdb": omdb_rating,
    "letterboxd": letterboxd_rating
  }
```

Não há normalização unificada entre fontes. Cada client retorna formato próprio; o use case apenas agrupa em um dict.

## Inconsistências de formato na resposta consolidada

| Fonte | Tipo de retorno em sucesso | Tipo de retorno em erro |
|-------|---------------------------|------------------------|
| Cinemeta | `dict` | `dict` com `error` |
| OMDb | `list[dict]` | `dict` com `error` |
| Letterboxd | `dict` | `dict` com `error` |

O cliente consumidor precisa tratar `omdb` como lista ou dict de erro.

## Processamento assíncrono

Todos os métodos dos clients são declarados `async` e executam de forma não bloqueante:

- `CinemetaClient` usa `httpx.AsyncClient` (**assíncrono** de fato).
- `OMDBClient` usa `httpx.AsyncClient` (**assíncrono** de fato, desde 2026-08-16).
- `LetterBoxdClient` usa `letterboxdpy` (biblioteca **síncrona**), executada via `asyncio.to_thread` para não bloquear o event loop.

`GetMovieRatings.execute()` dispara as três fontes em **paralelo** via `asyncio.gather(..., return_exceptions=True)`, isolando falha de uma fonte sem quebrar a resposta.

## Limitações atuais

- Busca por título, não por ID unificado entre fontes.
- Cinemeta usa primeiro resultado da busca; OMDb exige título exato; Letterboxd usa slug derivado do título.
- Sem retry, timeout configurável ou circuit breaker nas chamadas externas.
- Sem validação de rate limits das APIs externas.
- OMDb usa HTTP sem TLS (`http://www.omdbapi.com/`).
- Dependência da infraestrutura da comunidade Stremio (Cinemeta) — pode sofrer rate limit/instabilidade.
