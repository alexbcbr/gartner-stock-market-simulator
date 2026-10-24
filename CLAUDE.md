# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

A stock trading simulator with three independent components sharing one SQLite database:

- **trade-backend/** — FastAPI service exposing REST APIs for market prices, trades, and revenue calculation.
- **trade-ui/** — Vue 3 + TypeScript + Pinia SPA (Vite) that consumes the backend API.
- **trade-console/** — a standalone Python CLI client that talks to the same backend API (menu-driven, no direct DB access).

Database: SQLite file at `data/market_stock.db`, schema defined in `ddl/market_price.sql` and `ddl/trade.sql`.

## Commands

### Backend (trade-backend/)
```
cd trade-backend
uv run uvicorn app.main:app --reload      # start dev server (http://127.0.0.1:8000)
uv run pytest                              # run all tests
uv run pytest tests/test_trade_repository.py -s --log-cli-level=INFO -q  # run one test file with logs
make run-local                             # same as above via Makefile
make test
make create-db                             # recreate data/market_stock.db from ddl/*.sql (destructive)
```
Requires Python >=3.14, managed via `uv`.

### Frontend (trade-ui/)
```
cd trade-ui
npm install
npm run dev            # start Vite dev server (http://localhost:5173)
npm run build           # type-check + production build
npm run type-check      # vue-tsc only
npm run lint             # eslint --fix
npm run format           # prettier
```
Frontend reads config from `trade-ui/.env` (`VITE_LAYOUT`, `VITE_URL_TRADE_SERVICES`) via `src/config/index.ts`. Backend CORS is hardcoded in `trade-backend/app/main.py` to allow only `http://localhost:5173` / `http://127.0.0.1:5173`, so keep the dev server on that origin.

### Console client (trade-console/)
```
cd trade-console
python main.py           # interactive menu; talks to the backend API, not the DB directly
```

### Kubernetes / Docker (trade-backend)
```
cd trade-backend
docker build -t trade-backend:latest .
docker save trade-backend:latest | docker exec -i desktop-control-plane ctr -n=k8s.io images import -
kubectl apply -f k8s/deployment.yaml
kubectl port-forward svc/trade-backend 8000:8000
```

## Backend architecture

Layered structure per resource (market_price, trade, revenue), each split across:
- `app/routers/*.py` — FastAPI route handlers; translate exceptions to HTTP errors (`ValueError` → 400, `LookupError`/`sqlite3.IntegrityError` → domain errors → 400/404).
- `app/services/*.py` — business logic (e.g. `trade_services.create_trade` computes `price_difference` before persisting).
- `app/repositories/*.py` — raw SQL against SQLite via `app.db.get_connection()`, one connection per call using a context manager.
- `app/schemas/*.py` — Pydantic models for request/response validation.

`app/db.py` resolves the DB path relative to the repo (`data/market_stock.db`), not an env var. Foreign keys are enforced (`PRAGMA foreign_keys = ON`).

Data model constraints (enforced at the SQLite layer, not just in Pydantic):
- `symbol` must be exactly 4 uppercase characters, on both `market_price` and `trade`.
- `trade.symbol` has a FK to `market_price.symbol` (`ON DELETE RESTRICT`) plus a `BEFORE INSERT` trigger that blocks inserting a trade for a symbol with no market price row — so tests/data setup must insert `market_price` before `trade`.
- All price fields are `CHECK (>= 0)`.

`app/main.py` registers routers for `revenue`, `market_price`, and `trade` and calls `setup_logging()` once at import time (see `app/utils/logging.py`).

## Frontend architecture

Vue 3 (Composition API) + Pinia stores + vue-router, built with Vite.
- `src/stores/` — Pinia stores per domain (`marketPrices.ts`, `trades.ts`, `notifications.ts`) hold API state.
- `src/services/api.ts` — HTTP client wrapper around the backend, base URL from `config.URL_SERVICES`.
- `src/views/` — route-level pages (`MarketPricesView`, `TradesView`, `LeaderboardView`), wired in `src/router/index.ts`.
- `src/components/` — presentational/feature components (forms, modals, lists, charts).
- Theming via swappable CSS files in `src/assets/` (`blue.css`, `gray.css`, `leaderboard.css`), selected by `VITE_LAYOUT`.

## Notes

- `data/market_stock.db` is a tracked binary file — `make create-db` wipes and regenerates it from the DDL scripts; be cautious about running it against data you want to keep.
- The console client and the web UI are two independent frontends to the same backend API; there is no shared code between them.
