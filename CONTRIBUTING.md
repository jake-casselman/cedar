# Contributing to CEDAR

Thanks for considering a contribution to **CEDAR — Climate & Energy Diagnostics
for Applied Refrigeration**!

## Contributor License Agreement (required)

CEDAR is released under the **AGPL-3.0**, and the maintainer may also offer it
under a separate commercial license in the future. To make that possible, every
contributor must agree to the **[Contributor License Agreement](CLA.md)** before
their contribution can be merged.

By opening a pull request you agree to the CLA. For an explicit record, sign your
commits:

```bash
git commit -s -m "Your message"
```

This adds a `Signed-off-by: Your Name <your.email@example.com>` line certifying
that you have the right to contribute the code under the CLA.

> The maintainer is under no obligation to accept any contribution and may
> decline pull requests for any reason.

## Development setup

- Use Python 3.11–3.13.
- Install in editable mode with dev extras: `pip install -e .[dev]`
- Run the test suite locally with `pytest` (coverage is enforced).
- Keep functions documented and small; prefer pure utilities over monoliths.

## Documentation

Docs live under `docs/` (Sphinx + MyST):

```bash
pip install -e .[dev]
pip install sphinx sphinx-rtd-theme myst-parser
cd docs && make html
open build/html/index.html  # macOS
```

## Attribution

CEDAR carries a required-attribution term (AGPL §7(b)); see [LICENSE](LICENSE).
Please do not remove existing copyright or attribution notices.
