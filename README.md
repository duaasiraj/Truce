# Truce

**One conversation. One trusted contract.**

Truce is an AI-mediated scoping and negotiation pipeline for freelance/client work. A client or freelancer describes a project once; the system extracts structured requirements, asks for clarification wherever it's unsure instead of assuming, generates a scope document (included/excluded) with a transparent risk score, sets fair pricing boundaries, runs a bounded negotiation only where needed, and outputs a single contract with milestones.

Built for the **AMD Developer Hackathon: ACT II — Unicorn Track**.

---

## What this MVP actually does

- **Structured extraction** — a Client Agent parses a free-text project brief into deliverables, must-haves, nice-to-haves, and constraints, and flags anything ambiguous for clarification rather than guessing.
- **Scope document  — an included/excluded scope statement 
- **Pricing floor** — a Freelancer Agent reasons a fair minimum rate against a set of comparable market rates.
- **Bounded negotiation** — a Mediator Agent runs a capped, deterministic negotiation between the client's budget ceiling and the freelancer's price floor. Round limits and threshold enforcement live in plain Python, not in model judgment.
- **Contract generation** — once negotiation converges, a PDF contract (scope, pricing, milestones, signatures) is generated and stored.
- **Human approval throughout** — no agent action finalizes a deal or moves money. Every consequential step is reviewed by a human in the loop.

This is the **Layer 1 (Scoping & Negotiation)** slice of a larger planned product, scoped intentionally for the hackathon timeframe. No money moves in this MVP.

---

## Important disclaimers

**Market-rate data is static, not live.** The comparable rates used by the Freelancer Agent to set a price floor come from a curated, offline snapshot dataset (`tools/data/comparables.json`), not a live scrape or real-time market feed. This was a deliberate MVP tradeoff — live scraping is fragile (anti-bot measures, layout drift, rate limits) and adds demo risk with no upside for hackathon judging. Swapping in a real, continuously-updated data pipeline is a scoped post-hackathon task and only touches `tools/market_research.py`; it does not require changes to the agents that consume it.

**Negotiation is a simulation of the mechanic, not financial advice.** The bounded negotiation logic demonstrates a deterministic, auditable approach to closing a price gap. It is not a substitute for real market judgment, and pricing outputs should be treated as a starting point for human review, not a final number.

**No money movement in this MVP.** Escrow/payment execution is explicitly out of scope for this submission and would require real regulatory review (payment processor licensing, cross-border FX compliance) before any code is written.

**Local GPU-based rate ranking requires CUDA/ROCm hardware.** `tools/rate_ranking.py` loads and runs a local Gemma model (`google/gemma-2-2b-it`) directly on GPU (`device_map="cuda"`) as part of the freelancer pricing flow. This path was built and tested on an AMD GPU pod and will not run on CPU-only free hosting tiers (e.g. Streamlit Community Cloud, Hugging Face Spaces free tier) without modification. See **Deployment** below.

**Authentication is custom, not Supabase Auth.** Login uses a simple email/password + bcrypt scheme with session state managed by Streamlit — Supabase is used purely as a Postgres database and file store, not for identity. Row Level Security policies on the database and storage bucket should be configured with this in mind (see `db/client.py`, `auth/session.py`).

---

## Architecture

```
Stage 1 — Input:               Client or freelancer starts a project thread
Stage 2 — Client Agent:        Extraction + clarification (asks, doesn't assume)
Stage 3 — Scope + Risk Score:  Included/excluded doc, rule-based risk score
Stage 4 — Milestones:          Finalized scope broken into sequenced deliverables
Stage 5 — Freelancer Agent:    Price floor from market comparables
Stage 6 — Mediator Agent:      Bounded, capped negotiation
Stage 7 — Contract Generation: Compiled PDF: scope, pricing, milestones, signatures
Stage 8 — Human Approval:      Plain-language review; accept or reject with reason
```

**Invariant across every stage:** every agent output is schema-validated JSON (via Pydantic models in `models/schemas.py`), never trusted as free text. No agent action finalizes a deal or moves money — humans approve every consequential step.

### Agents

| Agent | File | Responsibility |
|---|---|---|
| Client Agent | `agents/client_agent.py` | Extracts and clarifies requirements, sets budget ceiling and priorities |
| Freelancer Agent | `agents/freelancer_agent.py` | Researches market rate for skill/experience tier, sets price floor with reasoning |
| Mediator Agent | `agents/mediator_agent.py` | Runs the capped, bounded negotiation between floor and ceiling |

### Orchestration

`crew.py` sequences the three agents (Client → Freelancer → Mediator). CrewAI is used as the orchestration framework for this hackathon/MVP scope.

---

## Tech stack

- **Frontend/App:** Streamlit
- **Agent orchestration:** CrewAI
- **LLM inference:** Fireworks AI API (remote), with an optional local Gemma path on AMD GPU (ROCm/PyTorch) for rate ranking
- **Database & file storage:** Supabase (Postgres + Storage)
- **PDF generation:** ReportLab
- **Validation:** Pydantic

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <this-repo-url>
cd truce
pip install -r requirements.txt
```

> **Note:** `requirements.txt` is trimmed for general deployment (no heavy local-inference libraries). If you need the local Gemma rate-ranking path (GPU required), use `requirements-amd.txt` instead, which includes `transformers`, `accelerate`, `bitsandbytes`, and `safetensors`.

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase API key (see note below on RLS) |
| `LLM_BASE_URL` | Base URL for the remote LLM API (e.g. Fireworks AI) |
| `LLM_API_KEY` | API key for the remote LLM |
| `LLM_MODEL_ID` | Model identifier to use for remote calls |
| `NEGOTIATION_ROUND_CAP` | Hard cap on negotiation rounds (int) |
| `FIREWORKS_API_KEY` | Fireworks AI API key |
| `CLIENT_PROFILE_ID` | Demo/default client profile ID used by the MVP |
| `LOCAL_GEMMA_MODEL_ID` | *(optional)* Local Gemma model ID for GPU-based rate ranking |

**On `SUPABASE_KEY`:** since this app does not use Supabase Auth, using the `service_role` key is the simplest way to ensure database/storage calls succeed if Row Level Security is enabled on your project. Treat this key as a server-side secret only — never expose it to a browser/client context.

### 3. Set up the database

Provision the required tables and a private Supabase Storage bucket named `contracts` in your Supabase project. Schema setup is not automated in this MVP — see `db/operations.py` for the expected table/column shapes used by the app.

### 4. Run locally

```bash
streamlit run app.py
```

---

## Deployment

This app runs as a single Streamlit process ,  agent orchestration happens in-process, not on a separate server. It can be deployed on any host that runs Streamlit apps with Python dependencies and environment secrets:

- **Streamlit Community Cloud** (free) — point it at `app.py`, add secrets matching the `.env` variables above.

**GPU-dependent features will not work on free CPU-only hosting.** The local Gemma rate-ranking path in `tools/rate_ranking.py` requires an actual CUDA/ROCm-capable GPU. On CPU-only free hosts, this path will fail. For deployment on non-GPU infrastructure, either route rate ranking through the remote Fireworks API instead of local inference, or accept that this specific feature is limited to GPU-backed environments (e.g. the AMD Developer Cloud pod used during development).

---

## Testing

```bash
python run_tests.py
```

Covers the Client Agent, Freelancer Agent, Mediator Agent, and an end-to-end pipeline smoke test. Tests exercise the deterministic/procedural logic paths; LLM-dependent behavior is validated against schema conformance rather than exact output matching, since model outputs are non-deterministic by nature.

---

## Project structure

```
agents/          Agent logic
auth/            Custom session-based authentication
config/          Environment-driven settings
crew.py          Sequential pipeline orchestration
db/              Supabase client and query operations
models/          Pydantic schemas for all agent I/O
tools/           LLM client, contract generator, market research, rate ranking
ui/              Streamlit pages and components
tests/           Unit and end-to-end pipeline tests
```

---

## License

MIT (per hackathon submission requirements).
