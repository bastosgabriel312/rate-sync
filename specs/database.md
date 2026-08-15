# Banco de Dados e Persistência

Documentação do estado atual de armazenamento de dados no backend RateSync.

## Banco de dados

**Não identificado no código analisado.**

Não há:

- Driver de banco de dados (SQLAlchemy, psycopg2, motor, etc.) em `requirements.txt`
- Models ORM ou entidades de domínio persistíveis
- Migrations ou scripts de schema
- Conexão ou configuração de datasource em `app/core/config.py`
- Implementação concreta de `MovieRepository` (`app/domain/repositories/movie_repository.py`)

## Interface de repositório (não implementada)

`app/domain/repositories/movie_repository.py` define uma ABC com dois métodos:

```python
class MovieRepository(ABC):
    async def get_movie(self, movie_id: str): ...
    async def save_movie(self, movie_data: dict): ...
```

Nenhuma classe concreta implementa essa interface. Nenhum use case a utiliza.

## Persistência de dados

### Filmes e ratings

Os dados de filmes e avaliações **não são persistidos**. Cada requisição:

1. Consulta APIs externas (TMDB, OMDb, Letterboxd) em tempo real.
2. Retorna o resultado diretamente ao cliente.
3. Não armazena o resultado em memória, disco ou banco.

### Cache

**Não identificado no código analisado.**

Não há uso de Redis, memória compartilhada, `@lru_cache` ou mecanismo similar.

### Sessões e autenticação

`SecurityService` carrega JWKS do Cognito em memória (`self.jwks`), mas:

- Não é chamado por nenhuma rota.
- O cache é apenas o atributo de instância `self.jwks` (sem TTL ou invalidação).

### Arquivos

**Não identificado no código analisado.**

Não há leitura ou escrita de arquivos de dados (JSON, CSV, SQLite, etc.) no código da aplicação.

A configuração carrega variáveis de um arquivo `.env` via `python-dotenv` (`app/core/config.py`), mas esse arquivo não está versionado no repositório.

## Implicações

| Aspecto | Comportamento atual |
|---------|---------------------|
| Histórico de buscas | Não armazenado |
| Cache de ratings | Não existe — mesma busca refaz 3 chamadas externas |
| Consistência entre fontes | Depende exclusivamente das APIs externas no momento da consulta |
| Disponibilidade offline | Não suportada |
| Backup / recovery | Não aplicável |

## Configuração relacionada a persistência

Variáveis em `app/core/config.py`:

| Variável | Propósito |
|----------|-----------|
| `TMDB_API_KEY` | Credencial de API (não é dado persistido) |
| `OMDB_API_KEY` | Credencial de API (não é dado persistido) |

Variáveis referenciadas em código não integrado (também não são persistência):

| Variável | Arquivo | Status em `Settings` |
|----------|---------|---------------------|
| `JWKS_URL` | `core/security.py` | Não definida |
| `TOKEN_URL` | `infrastructure/services/auth_service.py` | Não definida |
| `CLIENT_ID` | `infrastructure/services/auth_service.py` | Não definida |
| `CLIENT_SECRET` | `infrastructure/services/auth_service.py` | Não definida |
