# AGENTS.md — RateSync Backend Directive

Operational directives and technical guidelines for AI agents working within the **rate-sync** (Python / FastAPI) repository.

---

## 1. Repository Scope & Limits

This repository (`rate-sync/`) contains the Python FastAPI backend for RateSync, serving REST endpoints, a real-time WebSocket search stream, and external API integrations (Cinemeta, OMDb, Letterboxd).

- **Scope**: Modifications are strictly confined to `rate-sync/` and `rate-sync/specs/`.
- **Frontend Isolation**: Do NOT modify files in `rate-sync-ionic/`. The frontend is read-only for contract verification.

---

## 2. Mandatory Documentation Gate (Backend)

> **IMPLICIT AND MANDATORY RULE**: Before proposing or executing code changes in `rate-sync/`, the agent MUST automatically inspect the backend specifications.

### Pre-Execution Inspection Order:
1. `rate-sync/specs/README.md` — Backend specifications index.
2. `specs/SDD.md` — Global Software Design Document.
3. `rate-sync/specs/architecture.md` — Layered architecture and data flows.
4. `rate-sync/specs/api.md` — REST and WebSocket contracts.
5. `rate-sync/specs/scraper.md` — External clients and scraper normalization rules.
6. `rate-sync/specs/technical-debt.md` — Official technical debt registry and legacy code rules.

*Token Efficiency*: Read the minimum relevant documentation necessary for the task, but always check `rate-sync/specs/README.md`, `specs/SDD.md`, and `technical-debt.md` before code edits.

---

## 3. Critical Directive: Authentication Out of Scope

> ⚠️ **AUTHENTICATION IS OUT OF SCOPE FOR THIS REFACTORING PHASE.**

The following legacy authentication modules are classified in `technical-debt.md`:
- `app/core/security.py` → **NÃO INTEGRAR** / **DESCARTAR APÓS VALIDAÇÃO**
- `app/infrastructure/services/auth_service.py` → **NÃO INTEGRAR** / **DESCARTAR APÓS VALIDAÇÃO**

### Rules for Auth Code:
- ❌ Do NOT integrate these files into active routes or use cases.
- ❌ Do NOT use these files as a base for implementing auth in this phase.
- ❌ Do NOT implement JWT, Cognito, OAuth2, or auth guards.
- ❌ Do NOT delete these files automatically without the 6-step validation protocol.

---

## 4. Legacy Removal Protocol (`DESCARTAR APÓS VALIDAÇÃO`)

Before physically removing any file marked `DESCARTAR APÓS VALIDAÇÃO`, the agent MUST:
1. Search all references and imports (`grep_search`).
2. Search active consumers across routes and use cases.
3. Check unit test suites (`pytest`).
4. Check package dependencies.
5. Update `rate-sync/specs/technical-debt.md` with final decision.
6. Only then remove the file IF explicitly authorized by task.

---

## 5. Target Backend Architecture

The backend follows Clean Layered Architecture:

```
app/
├── main.py                    # Entry point, CORS middleware, router inclusion
├── api/
│   └── v1/                    # REST endpoints and WebSocket handlers
├── core/                      # Configuration (config.py), cache (cache.py), logging
├── domain/
│   ├── models/                # Pure domain entities / dataclasses
│   ├── repositories/          # Abstract Repository Interfaces (ABCs)
│   └── use_cases/             # Async business logic and aggregation use cases
└── infrastructure/
    ├── api_clients/           # Async HTTP clients (CinemetaClient, OMDBClient, LetterboxdClient)
    └── services/              # Infrastructure services
```

### Architectural Guidelines:
- **Routes (`app/api/v1/`)**: Controllers must remain thin, delegating business logic to use cases.
- **Async I/O (`app/infrastructure/api_clients/`)**: Use non-blocking `httpx.AsyncClient` inside `async` use cases. Avoid blocking `requests` library in event loop.
- **Resilient Aggregation**: External API failures (e.g., Letterboxd scraper outage) must be caught isolatedly, returning partial ratings without crashing HTTP 500.

---

## 6. Persistence & Cache Policy

- **No Relational/NoSQL Database**: Do NOT introduce ORMs (SQLAlchemy, Tortoise) or physical DBs in this refactoring phase.
- **In-Memory Cache**: Use lightweight LRU/TTL cache (`app/core/cache.py`) for search (1h TTL) and ratings (15m TTL) to minimize external API rate limits.

---

## 7. Automated Testing Strategy

- **Framework**: `pytest` + `pytest-asyncio` + `httpx.AsyncClient`.
- Create or update test files in `tests/` when modifying endpoints or use cases.
- Use mocks for external HTTP APIs during unit tests.

---

## 8. Secrets & Configuration

- Centralized configuration via `pydantic-settings` in `app/core/config.py`.
- ❌ Do NOT modify `.env` files or production environment secrets.
- ❌ Do NOT log or expose API keys (`TMDB_API_KEY`, `OMDB_API_KEY`).

---

## 9. Git Safety Rules

- ❌ NEVER execute `git clean`, `git add`, `git commit`, or `git push` automatically.
- Keep changes minimal, focused, and verified.
