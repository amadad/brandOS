# brand-os

CLI-first toolkit to normalize brand identity, signals, and content artifacts across existing projects.

## Install

```bash
uv sync
```

## CLI

```bash
# Identity normalization
brandos identity from-persona path/to/persona.yaml --format json
brandos identity from-social path/to/brand.yml --format yaml
brandos identity from-brandos path/to/config.yaml brand_key --format json

# Intel scaffolding
brandos intel from-brandos path/to/config.yaml givecare --query "remote care" --format json
brandos intel filter signals.json --keywords "givecare,telehealth" --stop-phrases "bosch"

# Planning scaffold
brandos plan outline "Launch brief" --format json

# Evaluation (rubric-based)
brandos eval grade path/to/rubric.yml "draft text" --score safety=8 --score choice=7

# Queue management
brandos produce queue add givecare "Post text" --platform twitter
brandos produce queue list givecare
brandos produce queue clear givecare
```

## Structure

```
src/brand_os/
├── cli.py
├── cli_utils.py
├── core/
│   ├── identity.py
│   ├── evaluation.py
│   ├── llm.py
│   ├── signals.py
│   └── storage.py
└── adapters/
    ├── persona.py
    ├── social.py
    └── brandos.py
```

## Goal

Keep existing repos intact while providing shared schemas and adapters for CLI-first workflows. Shared utilities cover identity, evaluation, signals, storage paths, and a pluggable LLM interface.
