# Universal LLM Safeguard Layer

## Overview

This project is a universal, open-source, plug-and-play middleware to safeguard AI-generated content—protecting minors, vulnerable users, and the general public from exposure to inappropriate or harmful outputs from LLMs and chatbots. Designed for easy integration into any Python-based backend (FastAPI, Flask, Django, REST), it ships as a pip-installable library, with modular filters, transparent logging, and fully auditable rules.

---

## 🚨 Start Here: Trinity Project Files

> **All contributors, GPT-4.5, and new devs MUST read these three canonical docs in**
> `docs/blueprints/.trinity/` **before making any changes, asking for code, or extending this project:**
>
> * `PROJECT_SEED.md` — Project intent, structure, and contribution rules
> * `safeguard_manifesto.md` — Purpose, philosophy, integration, config, scope
> * `safeguard_plan.md` — Phase-by-phase, stepwise build order and rules
>
> **Do not reference any file, variable, or config not defined in these docs.**

---

## Installation

```bash
pip install universal-llm-safeguard
```

---

## Quick Usage

### Python Library

```python
from universal_llm_safeguard.core.orchestrator import run_safeguard_pipeline

result = run_safeguard_pipeline("Your text input here")
print(result)
```

### Middleware: FastAPI Example

```python
from fastapi import FastAPI
from universal_llm_safeguard.integrations.fastapi_middleware import SafeguardMiddleware

app = FastAPI()
app.add_middleware(SafeguardMiddleware)
```

### REST API (Microservice Mode)

* POST `/filter` with JSON: `{ "text": "content here" }`
* Returns: `{ "status": "blocked|allowed", "flags": [...], "reasons": [...] }`

---

## Project Structure

* **docs/blueprints/.trinity/** — Canonical docs (“Trinity”), must-read for any code or LLM extension
* **docs/blueprints/** — Implementation blueprints/specs for every core module
* **core/**, **hooks/**, **utils/** — Python package modules (see blueprints for stubs)
* **tests/** — Full test coverage (to be implemented)
* **config/safeguard\_config.json** — Rules, thresholds, and all filtering settings
* **logs/** — Filter flag/audit logs (GDPR-compliant)

---

## Philosophy

* **Child-first, privacy-forward, open source (MIT)**
* **Transparent**: Every filter action is logged and explainable
* **Modular**: Extensible with new filters, languages, or compliance hooks
* **OSS-first**: Community improvements, open audits, and safe for any LLM deployment

---

## Contributing & Community

* See `CONTRIBUTING.md` (to be added)
* Join our \[Discord/Slack] (link TBA) for collaboration
* Feedback and suggestions via GitHub Issues

---

## License

MIT. Use, fork, and extend without restriction. Attribution appreciated.
