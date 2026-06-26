# Contributing

Thanks for considering a contribution!

> **Contributor License Agreement required.** Before a contribution can be
> merged, contributors must agree to the
> [CLA](https://github.com/jake-casselman/cedar/blob/main/CLA.md). By opening a
> pull request you agree to its terms; sign your commits with `git commit -s`.
> See [`CONTRIBUTING.md`](https://github.com/jake-casselman/cedar/blob/main/CONTRIBUTING.md)
> for details. The maintainer may decline any contribution.

- Use Python 3.11–3.13.
- Run tests locally with `pytest`.
- Keep functions documented and small; prefer pure utilities over monoliths.
- Docs live under `docs/` (Sphinx + MyST). Build with `make html` from the
  `docs` directory.

## Building docs locally

```bash
pip install -e .[docs]
cd docs && make html
open build/html/index.html  # macOS
```
