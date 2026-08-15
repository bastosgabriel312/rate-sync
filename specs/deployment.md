# Deploy e Configuração

Documentação do estado atual de configuração, ambiente e deploy do backend RateSync.

---

## Entry point

**Arquivo:** `app/main.py`

```python
app = FastAPI()
app.include_router(movie_router, prefix="/api/v1")
```

A aplicação é uma instância FastAPI padrão. Não há bloco `if __name__ == "__main__"` no código.

## Servidor ASGI

O `README.md` do projeto referencia **Uvicorn** como servidor web.

Comando típico (não documentado em script no repositório):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> Este comando é inferido da stack documentada no README. **Script de start não identificado no código analisado.**

---

## Variáveis de ambiente

**Arquivo de configuração:** `app/core/config.py`

```python
class Settings(BaseSettings):
    app_name: ClassVar[str] = "Rate Sync"
    TMDB_API_KEY: str
    OMDB_API_KEY: str

    class Config:
        env_file = ".env"
```

### Variáveis obrigatórias

| Variável | Tipo | Descrição |
|----------|------|-----------|
| `TMDB_API_KEY` | `str` | Chave de API do The Movie Database |
| `OMDB_API_KEY` | `str` | Chave de API do OMDb |

Carregamento:

1. `load_dotenv()` — lê arquivo `.env` se existir.
2. `pydantic-settings` — valida e popula `settings`.

Se variáveis obrigatórias estiverem ausentes, a aplicação **falha ao importar** `app.core.config`.

### Arquivo `.env`

**Não identificado no código analisado** (não versionado no repositório).

### Variáveis referenciadas em código não integrado

| Variável | Arquivo que referencia | Definida em `Settings`? |
|----------|------------------------|------------------------|
| `JWKS_URL` | `app/core/security.py` | Não |
| `TOKEN_URL` | `app/infrastructure/services/auth_service.py` | Não |
| `CLIENT_ID` | `app/infrastructure/services/auth_service.py` | Não |
| `CLIENT_SECRET` | `app/infrastructure/services/auth_service.py` | Não |

---

## Dependências

**Arquivo:** `requirements.txt`

Instalação:

```bash
pip install -r requirements.txt
```

### Dependências diretas da aplicação

| Pacote | Versão | Uso |
|--------|--------|-----|
| `fastapi` | 0.112.2 | Framework web |
| `uvicorn` | 0.30.6 | Servidor ASGI |
| `pydantic` | 2.7.0 | Validação |
| `pydantic-settings` | 2.4.0 | Configuração |
| `python-dotenv` | 1.0.1 | Carregamento de `.env` |
| `tmdbv3api` | 1.9.0 | Cliente TMDB |
| `requests` | 2.32.3 | Cliente HTTP OMDb |
| `letterboxdpy` | Git commit fixo | Scraping Letterboxd |
| `websockets` | 13.0.1 | Suporte WebSocket (via Starlette/FastAPI) |

Lista completa em `requirements.txt` (53 pacotes incluindo transitivas pinadas).

### Dependência implícita ausente

| Pacote | Referenciado em | Em `requirements.txt`? |
|--------|-----------------|------------------------|
| `PyJWT` | `app/core/security.py` | Não |

---

## CORS

**Arquivo:** `app/main.py`

```python
CORSMiddleware(
    allow_origins=["https://ratesync.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Implicações:

- Frontend em `https://ratesync.vercel.app` pode acessar a API.
- Requisições de `localhost` ou outras origens são bloqueadas pelo browser.
- `allow_credentials=True` requer origem explícita (não `*`).

---

## Infraestrutura de deploy

| Item | Status |
|------|--------|
| `Dockerfile` | Não identificado no código analisado |
| `docker-compose.yml` | Não identificado no código analisado |
| `Procfile` | Não identificado no código analisado |
| `railway.json` / `railway.toml` | Não identificado no código analisado |
| Scripts de deploy | Não identificado no código analisado |
| CI/CD (GitHub Actions, etc.) | Não identificado no código analisado |
| URL de produção | Não identificado no código analisado |

### Ambiente de produção (referência externa)

A URL `https://rate-sync-production.up.railway.app` é referenciada no frontend (`rate-sync-ionic/src/environments/environment.prod.ts`), sugerindo deploy no Railway. **Esta informação não está no código do backend** e não foi verificada.

---

## Ambiente de desenvolvimento local

Não identificado no código analisado.

Não há:

- `Makefile`
- Scripts em `package.json` (projeto Python)
- Documentação de setup além do `README.md` genérico
- Arquivo `.env.example`

### Requisitos inferidos da configuração

1. Python compatível com as dependências pinadas.
2. Variáveis `TMDB_API_KEY` e `OMDB_API_KEY` configuradas.
3. Uvicorn ou equivalente para servir `app.main:app`.

---

## Portas e protocolos

| Protocolo | Uso |
|-----------|-----|
| HTTP | Endpoints REST |
| WebSocket | `/api/v1/ws/find_movie/` |

Porta padrão do Uvicorn: `8000` (convenção; não configurada no código).

---

## Logging e monitoramento

| Item | Status |
|------|--------|
| Logging configurado (`logging` module) | Não identificado no código analisado |
| Métricas (Prometheus, etc.) | Não identificado no código analisado |
| APM / tracing | Não identificado no código analisado |
| Health check endpoint | Não identificado no código analisado |

Único output observável: `print()` em `app/api/v1/routes.py` (WebSocket) e `app/infrastructure/api_clients/letterboxd_client.py` (erros).

---

## OpenAPI / documentação automática

FastAPI gera documentação interativa por padrão:

| URL | Conteúdo |
|-----|----------|
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |
| `/openapi.json` | Schema OpenAPI |

Não há customização destas rotas no código analisado.

---

## Checklist de deploy (estado atual)

Com base no que o código exige para funcionar:

- [ ] Python instalado
- [ ] `pip install -r requirements.txt`
- [ ] `TMDB_API_KEY` configurada
- [ ] `OMDB_API_KEY` configurada
- [ ] Servidor ASGI apontando para `app.main:app`
- [ ] CORS origin alinhada com o domínio do frontend
- [ ] Suporte a WebSocket no proxy/load balancer (se aplicável)

Itens **não** necessários no estado atual (código não os utiliza):

- Banco de dados
- Redis / cache
- Variáveis Cognito (`JWKS_URL`, `TOKEN_URL`, etc.)
- `PyJWT` (a menos que `SecurityService` seja integrado)
