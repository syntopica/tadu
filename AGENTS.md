# Contributor notes

- One top-level unit per source file, with one responsibility. Split helpers into their own modules and import them explicitly.
- Each module has its own test file under `tests/`.
- Write everything in English: code, comments, docs and commit messages.
- Run the gate before committing:

```bash
uv sync && uv run pytest -v && uv run ruff check . && uv run ruff format --check . && uv run mypy tadu && uv run codeality-py gate
```
