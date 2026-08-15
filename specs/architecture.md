# Arquitetura

Documentação do estado atual da arquitetura do backend RateSync (`rate-sync/`).

## Visão geral

A aplicação segue uma organização em **camadas inspirada em Clean Architecture**, com separação entre API, domínio (use cases) e infraestrutura (clientes externos). Não há camada de persistência implementada.

```
┌─────────────────────────────────────────────────────────────┐
│  app/main.py                                                │
│  FastAPI + CORSMiddleware                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ prefix /api/v1
┌──────────────────────────▼──────────────────────────────────┐
│  app/api/v1/routes.py                                         │
│  Endpoints REST + WebSocket                                   │
│  Instanciação de clients e use cases (singleton no módulo)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  app/domain/use_cases/                                        │
│  FindMovie | GetMorePopulars | GetMovieRatings               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  app/infrastructure/api_clients/                              │
│  TMDBClient | OMDBClient | LetterBoxdClient                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
              APIs externas (TMDB, OMDb, Letterboxd)
```

## Estrutura de diretórios

```
app/
├── main.py                              # Entry point
├── api/v1/
│   ├── routes.py                        # Rotas e wiring de dependências
│   └── schemas.py                       # Modelos Pydantic (não usados nas rotas)
├── core/
│   ├── config.py                        # Settings (TMDB_API_KEY, OMDB_API_KEY)
│   └── security.py                      # SecurityService (não integrado)
├── domain/
│   ├── use_cases/
│   │   ├── find_movie.py
│   │   ├── get_more_populars.py
│   │   └── get_movie_ratings.py
│   └── repositories/
│       ├── movie_api_client.py          # ABC para clients de rating
│       └── movie_repository.py          # ABC não implementada
└── infrastructure/
    ├── api_clients/
    │   ├── tmdb_client.py
    │   ├── omdb_client.py
    │   └── letterboxd_client.py
    └── services/
        └── auth_service.py              # Cognito M2M (não integrado)
```

## Camadas e responsabilidades

### API (`app/api/v1/`)

- Define rotas HTTP e WebSocket.
- Instancia clients e use cases **uma única vez** no carregamento do módulo (`routes.py`, linhas 18–24).
- Expõe funções factory para injeção via `Depends()` nos endpoints REST.
- Captura exceções genéricas e retorna `HTTP 500` com `detail` da mensagem.

### Domínio (`app/domain/`)

**Use cases** — orquestram chamadas aos clients:

| Use case | Arquivo | Dependências | Método |
|----------|---------|--------------|--------|
| `FindMovie` | `find_movie.py` | `TMDBClient` | `execute(movie_title)` |
| `GetMorePopulars` | `get_more_populars.py` | `TMDBClient` | `execute()` |
| `GetMovieRatings` | `get_movie_ratings.py` | `TMDBClient`, `OMDBClient`, `LetterBoxdClient` | `execute(movie_title)` |

**Repositórios (abstrações):**

- `MovieAPIClient` — interface com `get_movie_rating(movie_id: str)`. Implementada por TMDB, OMDb e Letterboxd (as implementações concretas utilizam o nome de parâmetro `movie_title: str` em vez de `movie_id: str`).
- `MovieRepository` — interface com `get_movie` e `save_movie`. **Não possui implementação concreta.**

### Infraestrutura (`app/infrastructure/`)

- **API clients** — encapsulam chamadas a serviços externos.
- **AuthService** — solicita token OAuth2 `client_credentials` ao AWS Cognito. **Não é referenciado por nenhuma rota.**

### Core (`app/core/`)

- **Settings** — carrega `TMDB_API_KEY` e `OMDB_API_KEY` de variáveis de ambiente / `.env`.
- **SecurityService** — validação de JWT via JWKS do Cognito. **Não é referenciado por nenhuma rota.**

## Fluxo de dados

### Busca de filmes (WebSocket — fluxo usado pelo frontend)

```
Cliente WS
  → receive_text(movie_title)
  → FindMovie.execute(movie_title)
  → TMDBClient.find_movie(movie_title)
  → tmdbv3api Search.movies()
  → send_json([{title, overview, poster_path}, ...])
```

### Busca de filmes (REST — disponível, uso pelo frontend não identificado no backend)

```
GET /api/v1/movie/?movie_title=
  → FindMovie.execute(movie_title)
  → TMDBClient.find_movie()
  → JSON response
```

### Filmes populares

```
GET /api/v1/more_populars
  → GetMorePopulars.execute()
  → TMDBClient.find_more_populars()
  → tmdbv3api Movie.popular()
  → JSON response [{title, overview, poster_path}, ...]
```

### Ratings consolidados

```
GET /api/v1/ratings/{movie_id}
  → GetMovieRatings.execute(movie_id)    # parâmetro é tratado como título
  → TMDBClient.get_movie_rating()        # sequencial
  → OMDBClient.get_movie_rating()        # sequencial
  → LetterBoxdClient.get_movie_rating()  # sequencial
  → JSON response {tmdb, omdb, letterboxd}
```

> As três chamadas de rating são `await` sequenciais. Os métodos são declarados `async`, mas os clients TMDB e OMDb executam operações **síncronas** internamente (`tmdbv3api`, `requests`).

## Injeção de dependências

| Mecanismo | Onde | Comportamento |
|-----------|------|---------------|
| Instanciação manual | `routes.py` | Singletons criados no import do módulo |
| `Depends()` | Endpoints REST | Factory functions retornam os mesmos singletons |
| WebSocket | `websocket_find_movie` | Usa `find_movie_use_case` diretamente, sem `Depends` |

## Modelos e validação de entrada/saída

- `app/api/v1/schemas.py` define `MovieRatingResponse` e `MovieReviewSource`.
- **Nenhuma rota utiliza esses schemas** como `response_model` ou validação de entrada.
- As respostas são dicts Python retornados diretamente pelos use cases.

## Autenticação e segurança (estado atual)

| Componente | Status |
|------------|--------|
| `SecurityService` (`core/security.py`) | Existe, não integrado |
| `AuthService` (`infrastructure/services/auth_service.py`) | Existe, não integrado |
| Proteção nos endpoints | **Nenhuma** — todos os endpoints são públicos |

## CORS

Configurado em `app/main.py`:

- `allow_origins`: `["https://ratesync.vercel.app"]`
- `allow_credentials`: `True`
- `allow_methods`: `["*"]`
- `allow_headers`: `["*"]`

## Dependências entre módulos

```
main.py
  └── api/v1/routes.py
        ├── domain/use_cases/*
        │     └── infrastructure/api_clients/*
        │           └── core/config.py (settings)
        └── infrastructure/api_clients/* (instanciação direta)

core/security.py → core/config.py (referencia settings.JWKS_URL — não definido em Settings)
infrastructure/services/auth_service.py → core/config.py (referencia TOKEN_URL, CLIENT_ID, CLIENT_SECRET — não definidos em Settings)
```

## Limitações arquiteturais atuais

- Não há camada de persistência — toda consulta vai às APIs externas.
- Não há cache — mesma busca gera novas chamadas externas.
- Código de autenticação existe mas não participa do fluxo de requisições.
- `MovieRepository` definido mas sem implementação.
- Schemas Pydantic definidos mas não aplicados nas rotas.
- Parâmetro `movie_id` nos endpoints é, na prática, um **título de filme** (string livre).
