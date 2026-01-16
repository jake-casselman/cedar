# Contributing

Thanks for considering a contribution!

- Use Python 3.11–3.13.
- Run tests locally with `pytest`.
- Keep functions documented and small; prefer pure utilities over monoliths.
- Docs live under `docs/` (Sphinx + MyST). Build with `make html` from the
  `docs` directory.

## Building docs locally

```bash
pip install -e .[dev]
pip install sphinx sphinx-rtd-theme myst-parser
cd docs && make html
open build/html/index.html  # macOS
```
