# Repository Guidelines

## Project Structure & Module Organization

The core application lives under `src/app/`, with `api.py` exposing the FastAPI service. Configuration defaults sit in `src/app/core/`, vector access in `src/app/db/`, ingestion utilities in `src/app/ingestion/`, shared helpers in `src/app/utils/`, and LangGraph orchestration in `src/app/workflow/`. The web UI now resides in `frontend/`, a Next.js project styled as the operations control room. Persist images in `assets/` and keep exploratory work in `notebooks/`—notebook outputs should stay lightweight.

## Build, Test, and Development Commands

Run `uv sync` followed by `uv pip install -e .` to install runtime and editable sources. Copy credentials with `cp .env.example .env` and populate API keys before running services. Start Qdrant locally via `docker compose up -d`. Prime the knowledge base with `uv run python -m app.ingestion.cli --urls https://example.com` (see `--help` for PDF and chunking flags). Launch the backend using `uv run fastapi run src/app/api.py`. For the UI, `cd frontend`, install once with `pnpm install`, then run `pnpm dev` (set `NEXT_PUBLIC_RAG_API` if the backend isn’t on `localhost:8000`).

## Coding Style & Naming Conventions

Target Python 3.12 and follow PEP8 defaults: four-space indentation, 88–100 character lines, and `snake_case` modules/functions. Leverage type hints and concise docstrings as shown in `config.py` and `rag_workflow.py`. Prefer `logging` over bare prints, and route shared constants through `src/app/core/settings` so environment overrides remain centralized.

## Testing Guidelines

A formal test suite is not yet established; new contributions should include `pytest`-compatible cases under `tests/` and run with `uv run pytest`. Use fixture data that mirrors the ingestion pipeline’s chunk metadata. For qualitative checks, re-run `notebooks/ragas_eval.ipynb` after updating retrieval or generation logic and document evaluation outcomes in the PR.

## Commit & Pull Request Guidelines

Match existing Conventional Commit prefixes (`feat:`, `chore:`, `fix:`) seen in the log, keeping messages under 72 characters. Each PR should summarize the change, note environment or schema impacts, and link related issues. Include before/after screenshots when touching the Next.js control room, describe ingestion or workflow regressions mitigated, and confirm Docker + uv + pnpm commands used for verification.

## Configuration & Secrets

All environment defaults live in `src/app/core/config.py`. Never commit credentials; rely on `.env` and document new keys in `.env.example`. When adding external services, capture rate limits or retry guidance alongside the related configuration.
