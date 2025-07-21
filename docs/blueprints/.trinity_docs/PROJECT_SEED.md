# 🛡️ Universal LLM Safeguard Layer — Project Seed

**This document is the canonical project seed for the Universal LLM Safeguard Layer.  
It must be used to prime any LLM, developer, or build process before working on the codebase or documentation.  
All instructions, code, and extensions must strictly follow this seed and the referenced blueprint files.**

---

## 1. Project Purpose

A modular, open-source Python middleware to safeguard LLM and chatbot outputs—designed to protect minors, vulnerable users, and general audiences from harmful or inappropriate content.  
Usable as a standalone Python package, REST API, or middleware for FastAPI/Flask/Django.

---

## 2. Core Principles (Reference: Manifesto)

- Child-first, privacy-focused, and open source (MIT).
- All filter/block actions are logged and explainable.
- Parent/moderator override is always auditable.
- Designed for *plug-and-play*—no hardcoded dependencies.
- No invented files, features, or config fields—**only use those defined in this seed and the current plan**.

---

## 3. Canonical File/Folder Structure

```plaintext
llm_safeguard/
├── config/
│   └── safeguard_config.json
├── core/
│   ├── orchestrator.py
│   ├── keyword_filter.py
│   ├── regex_filter.py
│   ├── classifier_filter.py
│   └── perspective_api_filter.py
├── logs/
│   └── safeguard_flags.log
├── hooks/
│   ├── pre_process_hook.py
│   └── post_process_hook.py
├── utils/
│   ├── logger.py
│   └── anonymizer.py
├── tests/
│   ├── test_filters.py
│   └── test_integration.py
└── README.md
