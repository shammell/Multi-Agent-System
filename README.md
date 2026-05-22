# Multi-Agent System

Deterministic Python multi-agent framework with async message passing, defensive orchestration, Streamlit dashboard, and test-first engineering.

## Features

- **Specialized agents**
  - `ResearcherAgent` for query expansion/research payload generation
  - `WriterAgent` for draft synthesis payload generation
- **Async communication layer**
  - Lightweight `MessageBus` using native `asyncio`
  - Strict JSON envelope validation and checksum verification (`hashlib`)
- **Deterministic orchestrator**
  - Handshake state transitions: `RECEIVED -> RESEARCHED -> DRAFTED -> COMPLETED`
- **Rate-limit resilience**
  - `ExponentialBackoff` policy for 429 handling
- **Streamlit dashboard**
  - Goal input + mode toggle (`mock` / `live`)
  - Routing graph and final output rendering
- **Groq live mode**
  - `.env`-driven API key/model wiring
- **Verification-first test suite**
  - Unit, integration, memory guard, UI bridge, and E2E lanes

## Project Structure

```text
src/
  core/
    agent.py
    message_bus.py
  agents/
    researcher_agent.py
    writer_agent.py
  orchestrator/
    manager.py
  llm/
    groq_client.py
  ui/
    bridge.py
    trace_viz.py
    dashboard.py
tests/
main.py
```

## Quick Start

### 1) Install dependencies

```bash
python -m pip install -U pip
python -m pip install streamlit pytest playwright python-dotenv groq
python -m playwright install chromium
```

### 2) Configure environment

Create `.env` in repo root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
APP_MODE=mock
GROQ_TIMEOUT_SECONDS=25
```

> `.env` is gitignored by default.

### 3) Run tests

```bash
PYTHONPATH="/c/Users/AK/Multi-agent-system-remote" python -m pytest -q tests
```

### 4) Launch dashboard

```bash
python -m streamlit run src/ui/dashboard.py
```

## Modes

- **mock**: deterministic local behavior for stable tests and CI
- **live**: real Groq client calls via `GROQ_API_KEY`

## E2E Testing

Stable risk-managed default:
- `tests/test_e2e_dashboard.py` is opt-in (`RUN_STREAMLIT_E2E=1`)
- `tests/test_e2e_dashboard_live.py` is opt-in (`RUN_LIVE_E2E=1`)

Run mock DOM E2E:

```bash
RUN_STREAMLIT_E2E=1 PYTHONPATH="/c/Users/AK/Multi-agent-system-remote" python -m pytest tests/test_e2e_dashboard.py -v
```

Run live E2E:

```bash
RUN_LIVE_E2E=1 PYTHONPATH="/c/Users/AK/Multi-agent-system-remote" python -m pytest tests/test_e2e_dashboard_live.py -v
```

## Notes

- Core logic avoids heavy frameworks and keeps communication contracts explicit.
- Dashboard pipeline is defensive and exposes explicit run markers for observability.
