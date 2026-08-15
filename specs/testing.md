# Testes

Documentação do estado atual de testes automatizados no backend RateSync.

## Resumo

**Não identificado no código analisado.**

Não há arquivos de teste no repositório do backend.

## O que foi verificado

| Item | Resultado |
|------|-----------|
| Arquivos `test_*.py` | Não encontrados |
| Arquivos `*_test.py` | Não encontrados |
| Diretório `tests/` | Não encontrado |
| `pytest` em `requirements.txt` | Não presente |
| `unittest` / `pytest` no código `app/` | Não referenciado |
| Configuração de CI (`.github/workflows`, etc.) | Não identificado no código analisado |

## Framework de teste disponível (via dependências)

`fastapi` inclui `TestClient` (`fastapi.testclient`), mas **não há uso** no código da aplicação.

## Cobertura aparente

| Área | Cobertura |
|------|-----------|
| Endpoints REST | 0% |
| WebSocket | 0% |
| Use cases | 0% |
| API clients (TMDB, OMDb, Letterboxd) | 0% |
| Configuração / Settings | 0% |
| SecurityService / AuthService | 0% |
| Normalização (OMDb `sanitize_number`, Letterboxd `sanitize`) | 0% |

## Testes manuais

Não identificado no código analisado. Não há scripts, coleções Postman ou documentação de testes manuais no repositório.

## Implicações

- Mudanças em clients externos ou formatos de resposta não são detectadas automaticamente.
- Regressões em normalização de dados (OMDb ratings, sanitização Letterboxd) passam despercebidas.
- Código de autenticação (`SecurityService`, `AuthService`) não possui validação automatizada.
- Bugs de tipagem conhecidos (ex: `dict[str:MovieReviewSource]` em `get_movie_ratings.py`) não são capturados por linter/CI no repositório.
