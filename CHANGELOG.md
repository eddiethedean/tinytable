# Changelog

## 0.16.5

- Packaging: Add pyproject.toml, MANIFEST.in, py.typed; keep setup.py.
- CI: Add GitHub Actions for Python 3.8–3.13 with tests, mypy, ruff.
- Bugfix: Avoid mutable default in Table.__init__.
- Bugfix: label_tail(n) now returns last n labels.
- Bugfix: filter_by_indexes no longer mutates original table state.
- Bugfix: drop_row guards when labels is None.
- Bugfix: Join error message aligned with JoinStrategy ("full", not "outer").
- Bugfix: edit_column(..., inplace=False) preserves labels.
- Cleanup: Fix typos in docstrings/messages.
- Docs: Rewrite README with install, quickstart, and notes.
