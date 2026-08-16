Title: fix(letterboxd): robust upstream parsing, add metrics endpoint and monitor

Description:
Melhora parsing upstream do Letterboxd com JSON-LD e meta fallbacks; isola falhas para não quebrar a agregação. Adiciona monitor in-memory (letterboxd.failures / letterboxd.not_found) e endpoint GET /api/v1/metrics para visibilidade em dev.

Changes:
- app/infrastructure/api_clients/letterboxd_client.py: robust fetch/parse and fallback behavior
- app/core/monitor.py: in-memory counters for letterboxd failures/not found
- app/api/v1/routes.py: GET /api/v1/metrics endpoint
- pytest.ini: pythonpath adjustments
- tests: updated/added tests (local)

Validation:
- Backend: 13 tests passed locally (pytest)
- No changes to auth/credentials

Notes:
- .env was removed from index and added to .gitignore (local secrets must be re-applied in your environment)
- Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
