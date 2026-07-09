# PROJECT_STATE.md
_Last updated: Day 3 (July 9, 2026), end of session — AMD Developer Hackathon ACT II, Track 3_

## Repository Topology
- **Upstream (source of truth):** https://github.com/duaasiraj/Truce
- **Fork (Laiba's dev):** https://github.com/LaibaAdamji/Truce
- **Workflow:** Laiba works on fork → PRs into upstream. Teammate (duaasiraj) works directly on upstream feature branches.

---

## ⚠️ Discrepancy Flagged — Needs Verification Before Trusting This File Further

The version of this file received this session describes the Mediator Agent as using an **exponential-decay offer curve (`k=3.0`)** with `test_negotiation_scenarios.py` passing three scenarios. That contradicts the actual `agents/mediator_agent.py` source reviewed directly from commit `057f0a9` this session, which implements **linear interpolation** in `_next_offer()`:
```python
t = min(round_index / cap, 1.0)
raw = ceiling - t * (ceiling - floor)
```
Possible explanations: teammate shipped a further rewrite after `057f0a9` that hasn't been shown to us directly, or this description is inaccurate. **Do not treat the exponential-decay claim as confirmed** — pull `feat/mediator-agent` fresh and diff `_next_offer()` before relying on it for integration or demo prep. This file records both claims below without resolving the conflict, since resolving it requires re-reading actual code, not more description.

Similarly, this session's incoming file attributes the **contract generator to teammate ("assigned, no visible branch yet")**. That's incorrect for our side of the work — Laiba built `tools/contract_generator.py` this session (see Progress below). It's possible the teammate is *also* independently building one — this is a **duplicate-work risk** and should be confirmed directly, not assumed either way.

---

## Branches
| Branch | Location | Status |
|---|---|---|
| `main` | upstream | updated with merged features (PR #4); PR #5 pending merge |
| `feat/client-agent` | upstream | merged via PR #4, safe to delete |
| `feat/mediator-agent` | upstream | PR #5 open, described as "all tests passing" — **offer-curve implementation unverified against source, see discrepancy note above** |
| `main` | fork (LaibaAdamji) | behind upstream `main` — Freelancer Agent + market_research + contract_generator ready to push, not yet committed |

## Pull Requests
| # | Title | Status |
|---|---|---|
| 4 | feat(client_agent): requirement extraction w/ confidence-based gap detection | **Merged** → upstream `main` |
| 5 | fix(mediator): offer curve + termination fix | **Open** — reported ready for review; offer-curve description unverified this session |

**Not yet opened (Laiba, this session):** PR for `agents/freelancer_agent.py` + `tools/market_research.py` + `tools/data/comparables.json` + `tools/contract_generator.py` — code complete and tested, still local/unpushed.

## Issues
| # | Title | Status |
|---|---|---|
| 1 | help101 | Closed |
| 2 | [Auth] Gemma key / Fireworks API missing | Open — de-prioritized (Groq fallback working) |
| 3 | Clean up debug statements before submission | Open — defer to cleanup pass |
| 4 | Project status enum mismatch (`no_deal_possible`) | Closed — fixed via valid enum values (`pricing_ready`/`cancelled`) |

---

## Current Milestone
**Get all four pieces — Freelancer Agent, Mediator Agent, contract generator, UI — merged and reconciled into one working end-to-end demo pipeline.**

## Progress

### ✅ Merged upstream (`duaasiraj/Truce main`)
- 27-table Supabase schema + CRUD layer, provider-agnostic `llm_client.py`
- **Client Agent** (`agents/client_agent.py`) — merged via PR #4

### 🟡 Teammate branch — open PR, unverified details (upstream `feat/mediator-agent`, PR #5)
- Mediator Agent + `crew.py` orchestration, per commit `057f0a9` (confirmed by direct source read): bounded negotiation loop, linear offer interpolation, convergence/duplicate-insert bug fixes, demo tuning (`rate_expectation=40.0`)
- This session's incoming report additionally claims an exponential-decay rewrite and a new `test_negotiation_scenarios.py` suite (3 scenarios passing) and an enum fix (`no_deal_possible` → `cancelled`/`pricing_ready`) — **not yet independently verified against source this session**

### 🟢 Local/fork work — Laiba, this session, tested and verified (not yet pushed)
- `tools/market_research.py` rewritten to read from `tools/data/comparables.json` (20 curated entries) instead of 4 inline strings — signature-compatible, zero changes needed in `freelancer_agent.py`
- Verified via standalone test (default call, skill filter, fallback-on-no-match all correct) **and** a real smoke test through `freelancer_agent.py` against live Groq — `PriceFloor` row persisted correctly, reasoning quality improved with richer comparable data
- **New this session:** `tools/contract_generator.py` — deterministic PDF contract generation (no LLM), triggered post-convergence from `crew.py`. Fields verified against real `models/schemas.py` (`Contract.storage_path`, `file_type`, `status="draft"`, `generated_by`; `Project.status="contract_generated"`; party names joined `ClientProfile`/`FreelancerProfile` → `Profiles.name`; scope pulled from `Requirement.value`)
- Contract generator upload to Supabase Storage (`contracts` bucket, private) — PDF render test **passed**; bucket upload test **failed** with `403 RLS policy violation` — root cause identified (anon key vs. private bucket RLS), fix given (switch to service role key), **not yet re-confirmed after fix applied**

### ⬜ Not started
- `app.py` — still stale placeholder, single biggest demo blocker
- `tools/rate_ranking.py` — AMD GPU ranking step
- `Dockerfile`, `seed/demo_data.py` — empty

---

## Testing
- Freelancer Agent + market_research.json swap: verified twice (unit-level function test + real Groq smoke test) — passing
- Contract generator: PDF render verified visually — passing. Bucket upload: failed on RLS, fix identified, **rerun pending**
- Mediator Agent test suite (`test_negotiation_scenarios.py`, 3 scenarios) — reported passing by teammate's branch description; not independently re-run or diffed this session
- Full-pipeline rehearsal (`test_full_pipeline_vague_brief.py`) — reported passing; not independently re-run this session

## Demo Readiness
- Client Agent, Freelancer Agent (local), Mediator Agent (branch, PR #5), and Contract Generator (local, near-complete) now cover the full agent chain conceptually — none of the four are simultaneously merged and confirmed together yet
- No UI — `app.py` remains the biggest gap for an interactive demo
- Contract generation is close (one config fix away from a full green run), not the "not started" gap it was 24 hours ago

## Blockers
- **Bucket RLS on private `contracts` bucket** — blocks contract upload until service role key is swapped in `.env`. Low effort, high priority.
- **Interface/description conflict on Mediator Agent** (see Discrepancy note) — needs a direct diff of `feat/mediator-agent` before either merging PR #5 or building further against it.
- **Possible duplicate contract-generator work** — confirm with teammate whether they've also started one, before both sides invest further.
- Gemma/Fireworks (Issue #2) — soft-blocked, irrelevant right now.

## Technical Debt
1. `model_used` field still missing from `GemmaCallLog`.
2. `app.py` stale — full rewrite needed.
3. RLS disabled on Supabase tables (accepted tradeoff); Storage RLS on `contracts` bucket now hit directly and needs the same accepted-tradeoff treatment (service role key) rather than a policy rebuild, given timeline.
4. Debug `print()` statements (Issue #3) — deferred.
5. No `seed/demo_data.py`, no Dockerfile.

## Decisions Log
- (Prior) Groq as active provider; provider-agnostic architecture preserved.
- (Prior) `PriceFloor` keyed to `version_id`; retry-with-strict-JSON pattern standard across agents.
- (This session) `market_research.py` rebuilt on a static `comparables.json` rather than live scraping — deliberate reduction of demo risk.
- (This session) Contract generator is fully deterministic (no LLM call) by design — scope/price/parties are already decided by convergence time, so no benefit to adding LLM failure surface.
- (This session) Contract PDF's signed URL is not persisted long-term; only `storage_path` is stored in the `contracts` row, with signed URLs regenerated on demand — avoids storing an expiring credential.
- (Incoming, unverified) Reported adoption of exponential-decay offer curve on Mediator Agent — flagged for verification, not yet adopted as fact in this log.

## Development Log
**Day 1–2:** Client Agent merged. Freelancer Agent + market_research built and smoke-tested locally.
**Day 2 (this session, per commit review):** Teammate pushed `feat/mediator-agent` (`057f0a9`) — Mediator Agent + `crew.py`, linear offer curve, two bug fixes, demo tuning.
**Day 3 (this session):** Laiba rebuilt `market_research.py` around `comparables.json`, re-verified Freelancer Agent compatibility against Mediator's actual `PriceFloor`/`version_id`/`amount` usage (confirmed compatible, no changes needed). Built `tools/contract_generator.py` end-to-end, corrected three rounds of schema mismatches against real `models/schemas.py` and `db/operations.py` (client accessor, `Contract` fields, `Project.status` enum, party-name join path, `Requirement.value`). PDF render test passed; bucket upload test failed on RLS, root cause diagnosed, fix pending confirmation. Received a second-hand report of further Mediator Agent changes (exponential decay, new test suite, enum fix) not yet verified against source.

---

## Immediate Next Task (single highest priority)

**Apply the service-role-key fix and rerun `test_upload_contract.py` to get a fully green contract generator, then push it alongside the already-tested Freelancer Agent in one PR.**

This is the single task standing between "everything built" and "everything verified and on upstream." Both pieces are code-complete and have been individually validated at every other step — this is the last unconfirmed link.

1. Set `SUPABASE_KEY` to the service role key in `.env`
2. Rerun `python test_upload_contract.py` — confirm signed URL opens a real PDF
3. Delete both throwaway test files (`test_render_contract.py`, `test_upload_contract.py`)
4. `git add agents/freelancer_agent.py tools/market_research.py tools/data/comparables.json tools/contract_generator.py`
5. Commit, push to fork, open PR into upstream `main`
6. Separately (not blocking the above): pull `feat/mediator-agent` fresh and diff `_next_offer()` to resolve the linear-vs-exponential-decay discrepancy before merging PR #5 or wiring `crew.py` against it
7. Ping teammate to confirm whether they're independently building a contract generator, to rule out duplicate work