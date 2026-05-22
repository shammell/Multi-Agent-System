# Multi-Agent System

A deterministic, verification-driven multi-agent architecture in Python for orchestrating structured research-and-writing workflows under strict reliability constraints.

## Abstract

This repository implements a lightweight multi-agent framework composed of a coordinator (orchestrator), specialized workers (researcher and writer), and an asynchronous message bus with explicit envelope contracts. The system is engineered around falsification-first design and empirical verification, emphasizing reproducibility, bounded failure modes, and operational transparency across both backend execution and UI-level interactions.

## Research Motivation

Most agent stacks optimize for speed of prototyping but hide execution semantics behind opaque abstractions. This project takes the opposite stance:

- deterministic state transitions over emergent behavior,
- explicit contracts over implicit coupling,
- measurable reliability over anecdotal success.

The implementation therefore avoids heavy orchestration frameworks and relies on native Python concurrency primitives (`asyncio`, `threading`) with strict payload invariants.

## Architectural Overview

### Core Components

1. **MessageBus (`src/core/message_bus.py`)**
   - Native async publish/subscribe transport
   - Strict JSON envelope normalization/validation
   - Checksum verification (`hashlib`) to detect payload corruption
   - Bounded retry policy via `ExponentialBackoff`

2. **Agent Base (`src/core/agent.py`)**
   - Isolated per-agent state container
   - Decoupled interaction model (agents communicate only through bus topics)

3. **Researcher Agent (`src/agents/researcher_agent.py`)**
   - Accepts `TaskEnvelope`
   - Produces `ResearchPayload`
   - Supports mock and live LLM clients

4. **Writer Agent (`src/agents/writer_agent.py`)**
   - Consumes `ResearchPayload`
   - Produces `DraftPayload`

5. **Orchestrator (`src/orchestrator/manager.py`)**
   - Deterministic handshake/state machine
   - Transition sequence: `RECEIVED -> RESEARCHED -> DRAFTED -> COMPLETED`

6. **UI Layer (`src/ui/`)**
   - Streamlit dashboard for query submission and output inspection
   - Sync/async bridge with timeout controls
   - Trace visualization for message-routing introspection

### End-to-End Flow

```text
User Goal
  -> Orchestrator (TaskEnvelope)
  -> Researcher Agent (ResearchPayload)
  -> MessageBus (validated envelope transport)
  -> Writer Agent (DraftPayload)
  -> Orchestrator Final Output
  -> Streamlit Dashboard + Trace View
```

## Verification Philosophy

This project follows an empirical protocol:

- Test-first design where feasible (RED -> GREEN loops)
- Explicit edge-case targeting (timeouts, malformed payloads, state contamination)
- Runtime proof through executable tests, not narrative claims
- Defensive defaults for local reproducibility

## Repository Layout

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
pytest.ini
```

## Installation

```bash
python -m pip install -U pip
python -m pip install streamlit pytest playwright python-dotenv groq
python -m playwright install chromium
```

## Environment Configuration

Create `.env` at repository root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
APP_MODE=mock
GROQ_TIMEOUT_SECONDS=25
```

Security note: `.env` is excluded via `.gitignore`.

## Execution

### Run Test Suite

```bash
PYTHONPATH="/c/Users/AK/Multi-agent-system-remote" python -m pytest -q tests
```

### Launch Dashboard

```bash
python -m streamlit run src/ui/dashboard.py
```

## Operation Modes

- **mock**: deterministic and CI-friendly
- **live**: Groq-backed generation via `GROQ_API_KEY`

## E2E Test Policy

Due to Streamlit headless rendering variability across environments, E2E lanes are opt-in:

- DOM E2E (mock): `RUN_STREAMLIT_E2E=1`
- Live E2E (Groq): `RUN_LIVE_E2E=1`

Examples:

```bash
RUN_STREAMLIT_E2E=1 PYTHONPATH="/c/Users/AK/Multi-agent-system-remote" python -m pytest tests/test_e2e_dashboard.py -v
RUN_LIVE_E2E=1 PYTHONPATH="/c/Users/AK/Multi-agent-system-remote" python -m pytest tests/test_e2e_dashboard_live.py -v
```

## Reproducibility and Constraints

- Core logic intentionally avoids heavyweight agent frameworks
- Payload contracts remain explicit and inspectable
- Timeouts are bounded at orchestration and bridge layers
- Secrets remain outside versioned artifacts

## Contribution Guidance

Contributions should preserve:

1. deterministic protocol semantics,
2. explicit envelope contracts,
3. test-backed behavioral claims,
4. separation between stable CI lanes and environment-sensitive E2E lanes.

## License

Add project license file if/when legal policy is finalized.
