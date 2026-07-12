# Truce — Business Case

### Private AI Negotiation Infrastructure, Powered by AMD + Gemma

> Technical implementation and product mechanics are documented in [`README.md`](./README.md). This document explains the business problem, why private AI matters for this category, and why AMD-accelerated inference is a strategic fit.

---

## Executive summary

Truce transforms freelance agreements from ambiguous conversations into structured, transparent agreements before work begins.

It uses specialized AI agents representing different perspectives in a transaction: understanding requirements, evaluating feasibility and pricing, and mediating toward a bounded agreement that both sides can review.

The core insight is that freelance negotiations contain some of the most sensitive information in a business relationship: budgets, pricing expectations, constraints, and negotiation history. These are not ordinary chat messages — they are commercial signals.

AMD-powered local inference enables a future where this intelligence can increasingly remain private, reducing dependency on external APIs while improving cost efficiency and trust. The MVP demonstrates this direction today through a local Gemma model running inference directly on AMD hardware for pricing intelligence.

---

# The problem

Freelance work often breaks down before execution begins.

The failure is rarely a lack of available talent. It comes from:

* unclear requirements
* misunderstood expectations
* scope expansion after agreement
* pricing misalignment
* difficult negotiations

The result is lost time, unhappy clients, and freelancers absorbing unpaid work.

Freelance agreements also contain sensitive commercial information:

* Client budget constraints
* Freelancer pricing strategy
* Project requirements
* Negotiation history
* Business priorities

Current AI workflows typically send this information to external providers, creating challenges around privacy, recurring costs, and vendor dependency.

Truce focuses on making the agreement stage more structured, transparent, and trustworthy.

---

## The pain is measurable

* **52%** of projects experience scope creep, and unclear requirements are a major contributor to project failure according to PMI research.
* Freelance engagements often lack the formal processes used in larger organizations to prevent scope drift.
* Documented best practices consistently emphasize explicit scope definitions and change-management processes as effective ways to reduce ambiguity.

Truce automates these practices into the workflow instead of requiring every freelancer or client to manually create them.

---

# Why now?

Three shifts make this problem newly addressable:

### Local AI inference is becoming practical

Smaller open models are increasingly capable of running efficiently on accessible hardware, making private AI workflows more realistic.

### Open AI hardware ecosystems are expanding

AMD + ROCm provide an alternative path for teams building private inference systems without relying exclusively on hosted AI infrastructure.

### Freelance work is becoming increasingly global

Independent professionals and small agencies are handling increasingly complex projects across borders, while many still rely on informal communication channels for critical business decisions.

At the same time, AI agents are moving beyond simple assistants toward systems capable of structured workflows and multi-step reasoning.

---

# Why AMD + Gemma

Cloud-only AI introduces challenges for this use case:

| Challenge | Why it matters                                                      |
| --------- | ------------------------------------------------------------------- |
| Privacy   | Pricing strategy and negotiation context are commercially sensitive |
| Cost      | Repeated AI interactions create ongoing inference expenses          |
| Latency   | Negotiation workflows benefit from responsive interaction           |

AMD hardware combined with efficient open models like Gemma creates a path toward private, cost-efficient inference for sensitive workflow components.

The goal is not necessarily to move every computation locally, but to place the most sensitive intelligence closer to the user.

---

# Current implementation: hybrid architecture

Truce already demonstrates this approach with a hybrid stack:

| Layer               | Technology                | Role                                         |
| ------------------- | ------------------------- | -------------------------------------------- |
| Cloud inference     | Fireworks AI              | General reasoning and language understanding |
| Cloud fallback      | Groq                      | Reliability fallback                         |
| Local AMD inference | Gemma 2B via ROCm/PyTorch | Pricing intelligence and scoring             |

The local model is loaded directly onto AMD hardware, with inference performed on-device rather than through a hosted endpoint.

This proves the core direction: sensitive AI-assisted decisions can progressively move toward private execution.

---

# Business value of AMD integration

| Advantage       | Impact                                                                                  |
| --------------- | --------------------------------------------------------------------------------------- |
| Privacy         | Sensitive commercial information can remain closer to the user's environment            |
| Cost efficiency | Reduces dependence on repeated external inference calls                                 |
| Performance     | Enables responsive interactive workflows                                                |
| Trust           | Makes AI adoption easier when users understand where sensitive information is processed |

For negotiation-based systems, trust is not just a technical feature — it is a product advantage.

---

# Market opportunity

The freelance economy represents a large global market of independent professionals and small teams managing increasingly complex work.

Existing categories demonstrate willingness to pay for parts of this workflow:

* Freelance management platforms
* Contract management systems
* Marketplaces and talent platforms
* Enterprise negotiation software

However, these solutions typically address individual parts of the workflow rather than the full agreement process.

Truce focuses on the layer before execution:

**creating trusted agreements between people before work begins.**

---

# Initial market focus

Truce is initially designed for:

### Freelancers

Developers, designers, consultants, and specialists who need clearer scope and pricing confidence.

### Small agencies

Teams managing multiple client engagements that need consistent agreement workflows.

### Growing freelance ecosystems

Markets where independent work is expanding and tooling habits are still developing.

The underlying problem is universal: whenever two parties collaborate, they need alignment on expectations, scope, and value.

---

# Competitive differentiation

| Category        | What exists                             | Gap                                                                  |
| --------------- | --------------------------------------- | -------------------------------------------------------------------- |
| Freelance tools | Contracts, invoices, project management | Limited intelligence around negotiation and alignment                |
| Marketplaces    | Connecting clients and talent           | Do not solve the agreement process itself                            |
| Enterprise CLM  | Powerful contract workflows             | Built primarily for larger organizations                             |
| AI assistants   | General productivity support            | Do not represent competing interests or enforce agreement boundaries |

Truce combines:

* requirement understanding
* scope alignment
* pricing intelligence
* bounded negotiation
* agreement generation

into one workflow.

---

# Why this is difficult to replicate

The challenge is not simply generating text.

The difficult parts are:

* Representing different stakeholder objectives.
* Creating negotiation boundaries that remain predictable.
* Maintaining human approval and transparency.
* Building trust around AI-assisted commercial decisions.
* Integrating private inference where it provides real value.

---

# Long-term vision

Truce aims to become a trusted AI layer for freelance collaboration — helping people create clearer agreements while keeping sensitive business decisions transparent and controlled.

The goal is not to replace human negotiation.

The goal is to make agreements fairer, clearer, and easier to reach.

AMD provides the infrastructure path that makes private AI-powered collaboration increasingly possible.

---
