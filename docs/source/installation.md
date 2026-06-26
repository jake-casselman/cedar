# Installation

## Supported Python versions

- **3.10, 3.11, 3.12** (recommended)
- **3.13** (works; may build SciPy from source on some Linux setups → slower CI)

## Stable

```bash
pip install cedar-toolkit
```

## Development install

```bash
git clone https://github.com/jake-casselman/cedar.git
cd cedar
python -m venv env
source env/bin/activate  # .\env\Scripts\activate on Windows
pip install --upgrade pip
pip install -e .[dev]
```

Verify core dependencies:

```bash
python -c "import CoolProp, numpy, scipy, matplotlib; print('All dependencies imported successfully.')"
```

## Running tests

```bash
pytest
# or with coverage:
pytest --cov=cedar --cov-report=term-missing -v
```

## Troubleshooting

```{tip}
**macOS (Apple Silicon):** use Python 3.12+ and recent `pip`; wheels are available
for `numpy`, `scipy`, `matplotlib`, and `CoolProp`.
```

```{warning}
If you see SciPy building from source in CI on Linux (long “Preparing metadata”
steps), pin your CI matrix to Python **<=3.12** until prebuilt wheels for 3.13
are available.
```
