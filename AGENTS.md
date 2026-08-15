# AGENTS.md — RateSync Backend

Orientações para agentes de IA que trabalham neste repositório.

## Escopo

Este repositório (`rate-sync/`) contém o **backend** do RateSync: uma API Python/FastAPI que agrega dados e avaliações de filmes a partir de fontes externas (TMDB, OMDb e Letterboxd).

**Não modifique o frontend** (`rate-sync-ionic/`), salvo se a tarefa explicitamente exigir leitura de contratos de integração — e mesmo assim, sem alterar arquivos do frontend.

## Antes de qualquer mudança

1. Leia a documentação em `specs/`:
   - `specs/README.md` — visão geral
   - `specs/architecture.md` — camadas e fluxo de dados
   - `specs/api.md` — contratos dos endpoints
   - `specs/scraper.md` — integrações externas e normalização
   - `specs/database.md` — persistência (atualmente inexistente)
   - `specs/testing.md` — estado dos testes
   - `specs/technical-debt.md` — limitações conhecidas
   - `specs/deployment.md` — configuração e ambiente

2. Identifique quais arquivos em `app/` serão afetados e mantenha-se dentro do escopo da tarefa.

3. Confirme o impacto no frontend: o consumidor principal está em `rate-sync-ionic/` e depende dos contratos documentados em `specs/api.md`.

## Arquitetura

Respeite a organização em camadas documentada em `specs/architecture.md`:

```
app/
├── main.py                    # Entry point, CORS
├── api/v1/                    # Rotas REST e WebSocket
├── core/                      # Configuração e segurança
├── domain/
│   ├── use_cases/             # Orquestração de regras
│   └── repositories/          # Abstrações (ABC)
└── infrastructure/
    ├── api_clients/           # TMDB, OMDb, Letterboxd
    └── services/              # Serviços de infraestrutura
```

Regras:

- Rotas em `app/api/v1/` — sem lógica de negócio pesada; delegue a use cases.
- Regras de orquestração em `app/domain/use_cases/`.
- Chamadas a APIs externas em `app/infrastructure/api_clients/`.
- Configuração centralizada em `app/core/config.py`.

Não mova código entre camadas ou refatore estrutura fora do escopo da tarefa.

## Regras de API

- **Consulte `specs/api.md` antes de modificar endpoints**, parâmetros, códigos de status ou formatos de resposta.
- **Não altere a API sem atualizar `specs/api.md`** com o comportamento real resultante.
- Endpoints ativos (base `/api/v1`):
  - `GET /ratings/{movie_id}`
  - `GET /more_populars`
  - `GET /movie/?movie_title=`
  - `WS /ws/find_movie/`
- Preserve **compatibilidade com o frontend** (`rate-sync-ionic/`). Mudanças breaking em formato de resposta exigem atualização coordenada da spec e comunicação explícita na tarefa.
- O parâmetro `movie_id` em `/ratings/{movie_id}` é tratado como **título** pelos clients — não renomeie ou mude semântica sem atualizar spec e frontend.
- CORS está configurado para `https://ratesync.vercel.app` em `app/main.py` — alterações de origem afetam o frontend em produção.

## Banco de dados e persistência

O backend **não possui banco de dados** no estado atual (`specs/database.md`).

- **Não execute operações destrutivas em banco** — não há banco configurado neste projeto.
- Se a tarefa introduzir persistência:
  - Documente o schema em `specs/database.md`.
  - Crie migrations quando um sistema de migrations for adotado.
  - **Não altere schema sem migration** quando migrations existirem.
- `MovieRepository` (`app/domain/repositories/movie_repository.py`) é uma ABC não implementada — não assuma que persistência já existe.

## Integrações externas e scraper

Documentação em `specs/scraper.md`.

- Clients: `TMDBClient`, `OMDBClient`, `LetterBoxdClient` em `app/infrastructure/api_clients/`.
- **Não altere comportamento de coleta ou normalização** (sanitização de títulos, mapeamento de ratings OMDb, formato de resposta por fonte) sem atualizar `specs/scraper.md`.
- Letterboxd usa scraping via `letterboxdpy` — mudanças são frágeis; documente o impacto.
- Variáveis obrigatórias: `TMDB_API_KEY`, `OMDB_API_KEY` (via `.env` ou ambiente).

## Dependências

- Gerenciadas em `requirements.txt` via `pip`.
- **Não adicione dependências sem justificativa** explícita na tarefa.
- Ao adicionar, pinne a versão seguindo o padrão do arquivo e documente o motivo.
- Não remova dependências sem verificar uso em `app/` (ex.: `letterboxdpy`, `tmdbv3api`, `requests`).
- `PyJWT` é importado em `app/core/security.py` mas ausente de `requirements.txt` — corrija apenas se a tarefa envolver autenticação.

## Funcionalidades existentes

- **Não remova funcionalidades existentes** sem solicitação explícita.
- Código não integrado (`SecurityService`, `AuthService`) ainda faz parte do repositório — não delete silenciosamente; se a tarefa envolver remoção, documente em `specs/`.
- WebSocket de busca (`/ws/find_movie/`) é o canal usado pelo frontend — preserve o contrato.

## Testes

Estado atual: **não há testes automatizados** (`specs/testing.md`).

- **Crie ou atualize testes quando a tarefa introduzir ou modificar comportamento** verificável.
- Ao adicionar testes, use `pytest` ou `unittest` com `fastapi.testclient.TestClient` — adicione o framework necessário ao `requirements.txt` se ainda não existir.
- Atualize `specs/testing.md` ao introduzir infraestrutura de testes.
- **Execute os testes antes de concluir a tarefa.** Se ainda não houver suite, valide manualmente os endpoints afetados com o servidor local:

  ```bash
  uvicorn app.main:app --reload
  ```

  Confirme que a aplicação inicia sem erro de importação e que os endpoints modificados respondem conforme `specs/api.md`.

## Segredos e configuração

- **Não altere `.env`**, secrets, credenciais ou valores de API keys.
- **Não commite** arquivos `.env` ou chaves.
- Configuração da aplicação: `app/core/config.py` — novas variáveis de ambiente devem ser documentadas em `specs/deployment.md`.
- Não modifique `allow_origins` em CORS sem alinhar com o domínio real do frontend.

## Disciplina de mudanças

- **Mantenha mudanças pequenas e focadas** no que a tarefa pede.
- **Não refatore partes fora do escopo** (renomeações amplas, reorganização de pastas, limpeza de débitos não solicitados).
- Não altere `requirements.txt`, `specs/` ou configurações de deploy além do necessário para a tarefa.
- Ao resolver débitos listados em `specs/technical-debt.md`, atualize a spec correspondente.
- Siga o estilo e convenções do código existente (async nos use cases, retorno de `{"error": ...}` nos clients, `Depends()` nas rotas REST).

## Commits

- **Não crie commits** a menos que o usuário solicite explicitamente.

## Checklist antes de concluir

- [ ] Li e respeitei as `specs/` relevantes
- [ ] Atualizei `specs/` se mudei API, integrações, persistência, testes ou deploy
- [ ] Mudança compatível com o frontend (ou breaking change documentado)
- [ ] Sem alteração em `.env` ou secrets
- [ ] Dependências novas justificadas e pinadas
- [ ] Testes criados/atualizados e executados (ou validação manual documentada se não houver suite)
- [ ] Escopo limitado — sem refatoração extra
