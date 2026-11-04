# Task 5 report: workspace and local configuration

Status: DONE

## RED
`uv run pytest -q tests -k "workspace or local_config or toml or entries"` before any implementation:
`ModuleNotFoundError: No module named 'tadu.organization_entry'` ... 7 errors during collection (test_entries, test_load_local_config, test_load_workspace, test_read_toml, test_workspace_error, test_workspace_file_names, test_workspace_problems).

## GREEN
Full gate: 491 passed; ruff check, ruff format --check, mypy tadu tests, `codeality-py gate` (incl. 100% coverage, pip-audit, deptry) all passed; `uv run tadu doctor .` exit 0.

## Built
Required files from the brief plus small helpers (one unit each): table_rows, required_text, optional_text, text_list, parse_repository/project/roles/organization/person/paths, duplicate_problems, project_problems, person_problems. `workspace_file_names.py` registered in `[roles] data`.
Controller rulings followed: tomllib only; version must be int 1 (bool rejected); roles flattened in table then list order; name defaults to key; backlog absolute or containing `..` rejected; every malformed shape raises WorkspaceError naming table and key; `[paths]` values are `directory / value`.

## Notes
- Ruff EM/TRY003 forbid inline messages, so raises use `msg = ...; raise WorkspaceError(msg)`.
- Unknown `me` message: `me: unknown person <id>`; unknown path key: `paths: unknown repository <key>`.
- Project-level problems with the roles: an unknown repository in a project is reported by workspace_problems, so load_workspace joins them with "; ".
