tinytable
=========

Pure Python, lightweight DataFrame-like table for small datasets. Zero C extensions. Friendly API inspired by pandas, but tiny.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/eddiethedean/tinytable/workflows/CI/badge.svg)](https://github.com/eddiethedean/tinytable/actions)

Installation
------------

```bash
pip install tinytable
```

Supports Python 3.8–3.13.

Quickstart
----------

```python
from tinytable import Table, read_csv, read_excel, read_sqlite

# Read from files
t1 = read_csv('tests/data/people.csv')
t2 = read_excel('tests/data/people.xlsx', sheet_name='Sheet1')
t3 = read_sqlite('tests/data/data.db', 'people')

# Construct manually
t = Table({'id': [1, 2, 3], 'name': ['a', 'b', 'c']}, labels=[('r1',), ('r2',), ('r3',)])

# Column/row access
ids = t['id']           # Column
row1 = t[0]             # Row
subset = t[['id']]      # New Table with only id

# Filter and slice
adults = t[t['id'] > 1] # boolean filter
head = t[:2]            # slice rows

# Edit
t.edit_value('name', 0, 'z')
t2 = t.edit_column('id', [10, 20, 30], inplace=False)

# IO
t.to_csv('out.csv')
t.to_excel('out.xlsx', sheet_name='Sheet1')
t.to_sqlite('out.db', table_name='people', primary_key='id', replace_table=True)
```

Features
--------

- **Pure Python**: No C extensions, easy to install and debug
- **Pandas-like API**: Familiar interface for data manipulation
- **Multiple I/O formats**: CSV, Excel, SQLite support
- **Type-safe**: Full mypy type checking support
- **Well-tested**: Comprehensive test suite with 76% coverage (235 tests)
- **Modern packaging**: Uses `pyproject.toml` and supports Python 3.8-3.13

API surface
-----------

- `Table`: core container with column/row operations, `head`, `tail`, joins, group stats, NA ops.
- Readers: `read_csv`, `read_excel`, `read_sqlite`.
- Writers: `to_csv`, `to_excel`, `to_sqlite`.

Development
-----------

This package has been fully modernized with:

- ✅ **Modern Python packaging** (`pyproject.toml`)
- ✅ **Comprehensive testing** (pytest with 235 tests, all passing)
- ✅ **Type safety** (mypy strict checking)
- ✅ **Code quality** (ruff linting and formatting)
- ✅ **CI/CD** (GitHub Actions)
- ✅ **100% backward compatibility**

Contributing
------------

PRs welcome. Run tests and linters:

```bash
pip install -e .[dev]
pytest -q
mypy tinytable
ruff check .
ruff format .
```

Notes
-----

- This release (v0.18.1) includes comprehensive modernization, bug fixes, improved type safety, and robust empty table handling.
- See `CHANGELOG.md` for detailed release notes.