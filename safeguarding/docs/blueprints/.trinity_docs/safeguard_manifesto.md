# Universal LLM Safeguard Layer Manifesto

## Purpose

To protect children, vulnerable users, and general audiences from exposure to harmful, abusive, or developmentally inappropriate content in AI-generated conversations.
This project delivers an open-source, modular, and auditable middleware for content safeguarding—usable by any AI developer, platform, or company.

---

## Philosophy & Principles

* **Child-first:** Default settings err on the side of caution for minors.
* **Transparency:** All filtering actions are logged and explainable. No “silent” blocking.
* **Override with accountability:** Parents, moderators, and admins may override blocks with secure phrases, every action logged for audit.
* **Ecosystem-first:** Designed as plug-and-play middleware; open, extensible, and portable.
* **Privacy aware:** No data is sent to external APIs without user opt-in. All logs are anonymized by default, and GDPR principles guide storage.
* **Composable:** Multiple filtering strategies—rules, classifiers, cloud APIs—may be combined, tuned, or disabled per deployment.
* **Continuous improvement:** Community-driven updates to keyword lists, models, and rules.
* **Open source:** MIT-licensed. Use, improve, fork, or embed in your AGI/LLM stack.

---

## Scope

* Blocks, flags, and logs user and LLM messages that contain or suggest sexual, abusive, hateful, or otherwise unsafe material.
* Offers pre/post-processing hooks for any Python-based chatbot or LLM API server.
* Ships with English defaults but is designed for multi-language extension.
* Easily integrates with FastAPI, Flask, Django, or any Python backend.

---

## Limitations

* Classifier models are not perfect—may miss subtleties or generate false positives/negatives.
* Contextual, multi-turn grooming detection is experimental and not a guarantee.
* No model or config can replace vigilant human oversight; this is a tool, not a guarantee of safety.

---

## Integration and Deployment

### Python Library Usage

```python
from universal_llm_safeguard.core.orchestrator import run_safeguard_pipeline

result = run_safeguard_pipeline("Your text input here")
print(result)
```

### Middleware Usage

#### FastAPI

```python
from fastapi import FastAPI, Request
from universal_llm_safeguard.integrations.fastapi_middleware import SafeguardMiddleware

app = FastAPI()
app.add_middleware(SafeguardMiddleware)
```

#### Flask

```python
from flask import Flask, request
from universal_llm_safeguard.integrations.flask_middleware import safeguard_filter

app = Flask(__name__)

@app.route('/', methods=['POST'])
def home():
    content = request.json['text']
    result = safeguard_filter(content)
    return result
```

#### Django

In `settings.py`:

```python
MIDDLEWARE = [
    'universal_llm_safeguard.integrations.django_middleware.SafeguardMiddleware',
    # existing middleware...
]
```

### REST Microservice Usage

* **POST /filter**
* Payload:

  ```json
  {
    "text": "User-generated content here"
  }
  ```
* Returns:

  ```json
  {
    "status": "blocked|allowed",
    "flags": ["keyword", "regex", "classifier", "perspective_api"],
    "reasons": ["Reason details"]
  }
  ```

---

## Config Template

`config/safeguard_config.json`:

```json
{
  "rules": {
    "banned_keywords": ["sex", "drugs", "violence", "suicide", "kill", "groom", "address", "meet", "alone"],
    "banned_regex": [".*naked.*", ".*let's keep this secret.*"]
  },
  "classifier": {
    "enabled": true,
    "model": "unitary/toxic-bert",
    "thresholds": {
      "toxic": 0.8,
      "severe_toxic": 0.7,
      "insult": 0.75,
      "sexually_explicit": 0.7,
      "threat": 0.7
    }
  },
  "perspective_api": {
    "enabled": false,
    "api_key": "",
    "thresholds": {
      "TOXICITY": 0.8,
      "SEVERE_TOXICITY": 0.7,
      "INSULT": 0.75,
      "SEXUALLY_EXPLICIT": 0.7,
      "THREAT": 0.7
    }
  },
  "logging": {
    "log_path": "safeguard_flags.log",
    "anonymize": true,
    "retain_days": 30
  },
  "override": {
    "parent_phrases": ["override123", "parentbypass!"],
    "moderator_phrases": ["modunlock!"]
  }
}
```

---

## Testing & Development

* Full test suite:

  * `tests/test_filters.py`, `tests/test_integration.py`
* Run with:

  ```bash
  python -m unittest discover tests
  ```
* Integration and deployment docs: see `README.md`.

---

## Community & Collaboration

* GitHub repository, clear labels, CONTRIBUTING.md, and community channels.
* Community feedback loop for classifier and rule updates.
* Encourage forking, embedding, extending—MIT license.

---

## Continuous Improvement

* Community-driven model and rules update.
* Regularly review for new risks and language.

---

*This manifesto is canonical and must be referenced by any implementation, contributor, or extension of the Universal LLM Safeguard Layer project.*
