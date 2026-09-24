# Contributing to AETHER Capital

Thank you for your interest in contributing to AETHER Capital — an institutional-grade AI hedge fund platform built for quantitative research, portfolio optimization, and algorithmic execution.

---

## 🚀 Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-hedge-fund.git
cd ai-hedge-fund

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Copy environment config
cp .env.example .env
# Edit .env — add OPENAI_API_KEY if you have one (optional, works offline without it)

# 5. Start the server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 6. Open in browser
# → http://127.0.0.1:8000
# → Login: analyst@aether.fund / quant2026
```

---

## 🧪 Running Tests

```bash
# Run full test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_risk_metrics.py -v
pytest tests/test_portfolio_optimizer.py -v
```

---

## 📁 Project Structure

```
ai-hedge-fund/
├── backend/app/          # FastAPI backend
│   ├── api/v1/           # REST endpoints (auth, analyze, trade, backtest)
│   ├── core/             # Security, guardrails, RBAC
│   ├── models/           # SQLAlchemy ORM models
│   └── schemas/          # Pydantic request/response schemas
├── src/                  # Quantitative engine
│   ├── agents/           # LangGraph multi-agent nodes (Bull, Bear, Quant, Risk)
│   ├── quant/            # Risk metrics, portfolio optimizer, Monte Carlo
│   ├── graph/            # LangGraph workflow orchestration
│   ├── data/             # Market data fetcher + cache manager
│   └── db/               # Audit trail database manager
├── frontend/             # Vanilla JS/HTML5 terminal UI
│   ├── index.html        # SPA with 6 analytical tabs
│   ├── styles.css        # Dark terminal theme + glassmorphism
│   └── app.js            # JWT auth, chart rendering, API client
└── tests/                # Pytest test suite
```

---

## 🏗️ Key Design Decisions

| Decision | Rationale |
|---|---|
| **LangGraph** over plain LangChain | Stateful graph execution — agents maintain typed `AgentState` across rounds |
| **Raw bcrypt** over passlib | passlib incompatible with bcrypt v4+; raw `bcrypt.hashpw` is equivalent in security |
| **SQLite + WAL mode** | Zero-dependency deployment; WAL enables concurrent reads for audit trail |
| **Vanilla JS frontend** | No framework overhead — demonstrates DOM, Canvas, fetch API mastery |
| **Deterministic fallback** | Platform runs without OpenAI API key — great for demos and CI |

---

## 📐 Coding Standards

- **Python**: Follow PEP 8. Run `ruff check .` before committing.
- **Type hints**: Required on all public functions.
- **Docstrings**: Required on all modules and public methods.
- **Tests**: Every new quant function needs a corresponding test in `tests/`.
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/) format:
  - `feat:` — new features
  - `fix:` — bug fixes
  - `test:` — adding or updating tests
  - `docs:` — documentation only
  - `refactor:` — code refactoring

---

## 🔀 Pull Request Process

1. Fork the repo and create your branch: `git checkout -b feat/my-new-feature`
2. Write tests for any new quant functions
3. Ensure `pytest tests/` passes
4. Ensure `ruff check .` passes
5. Update `README.md` if you add a major feature
6. Open a PR with a clear description of what changed and why

---

## 🧩 Areas Where Contributions Are Welcome

- [ ] **WebSocket price feed** — replace polling with live WebSocket streaming
- [ ] **PostgreSQL support** — extend `DATABASE_URL` to support production Postgres
- [ ] **Additional agents** — Macro agent, Earnings agent, Options flow agent
- [ ] **Mobile responsive CSS** — adapt terminal UI to mobile viewports
- [ ] **SHAP explainability** — add feature importance to portfolio decisions
- [ ] **Additional tickers** — extend beyond US equities to ETFs and crypto

---

## 👤 Author

**Shantanu Kalhapure** — Lead Quantitative Strategist & Systems Architect  
Built as an institutional-grade demonstration of AI-driven quantitative finance engineering.

---

*AETHER Capital is a research and educational project. It is not financial advice and does not manage real assets.*
