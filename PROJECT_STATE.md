# PROJECT_STATE.md

> Last Updated:
> Updated By:
> Current Branch:
> Commit Hash (optional):

---

# Project

**Name:**
**Hackathon:**
**Track:**

## Elevator Pitch
(2-3 sentence summary of what we're building.)

---

# Current Goal

Current milestone:

Target for today:

Target before next demo:

Deadline:

---

# Architecture

## Tech Stack

Backend:
Frontend:
Database:
LLM Provider:
Deployment:
Other Services:

---

## Repository Structure

List major folders and what they contain.

Example:

agents/
tools/
db/
config/
ui/
tests/

---

# Current LLM Provider

Provider:
Model:
Reason:

Migration plan:

Current
↓

Next

↓

Final

Example:

Groq
↓

Fireworks Cheap Model
↓

Gemma

---

# Features

## Completed

- [ ]

- [ ]

- [ ]

---

## In Progress

- [ ]

---

## Not Started

- [ ]

---

# Agents

## Client Agent

Status:

Responsibilities:

Completed:

Remaining:

Files:

---

## Freelancer Agent

Status:

Responsibilities:

Completed:

Remaining:

Files:

---

## Mediator Agent

Status:

Responsibilities:

Completed:

Remaining:

Files:

---

# Tools

## Market Research

Status:

Files:

Notes:

---

## Rate Ranking

Status:

Files:

Notes:

---

## Other Tools

...

---

# Database

Schema Status:

Completed Tables:

Pending Tables:

Migration Status:

Known Issues:

---

# APIs

Current APIs:

External APIs:

Environment Variables Required:

---

# Current Branches

main

feature branches

merged branches

important PRs

---

# Open Issues

Issue:

Priority:

Owner:

Status:

---

# Known Bugs

Bug:

Cause:

Temporary Fix:

Permanent Fix:

---

# Technical Debt

List shortcuts taken intentionally.

Explain why.

---

# Testing

Passing:

Failing:

Smoke Tests:

Golden Path:

---

# Demo Readiness

Client Agent:

Freelancer Agent:

Mediator:

Main Loop:

UI:

Database:

Deployment:

Overall:

---

# Immediate Next Task

Objective:

Files:

Estimated Time:

Definition of Done:

---

# After That

Task 1

Task 2

Task 3

---

# Decisions Log

Chronological list of major decisions.

Example:

- Switched from Fireworks to Groq because Gemma access unavailable.
- Architecture changed to provider-agnostic LLM interface.
- Client Agent uses deterministic gap detection instead of LLM.

---

# Lessons Learned

Only permanent lessons that future work should follow.

---

# Prompting Rules

- Provider agnostic prompts.
- Strict JSON output.
- Retry once with stricter prompt.
- Log model_used.
- Keep deterministic logic outside the LLM whenever possible.

---

# Session Summary

Today I completed:

Current blocker:

Next session should begin with:

If someone else continues this project, they should first:
