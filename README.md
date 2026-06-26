# CEDAR: Climate & Energy Diagnostics for Applied Refrigeration

<p align="center">
<img src="docs/source/_static/cedar_logo.png" alt="CEDAR logo" width="50%" />
</p>

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18274828.svg)](https://doi.org/10.5281/zenodo.18274828)
![PyPI](https://img.shields.io/badge/PyPI-coming_soon-lightgrey)
![Python](https://img.shields.io/badge/python-3.10–3.13-blue)
![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)
![Code Style](https://img.shields.io/badge/code_style-PEP_8-blue)
![Docs](https://img.shields.io/badge/docs-in_progress-lightgrey)
![Paper](https://img.shields.io/badge/paper-in_review-blueviolet)

> **CEDAR: Climate & Energy Diagnostics for Applied Refrigeration** — a Python library linking climate data to refrigeration physics and thermal system performance.

---

## Overview

The **CEDAR** platform provides a modular, research-grade framework for analyzing how **climate conditions affect thermal system performance** (COP and SHR) from refrigeration and HVAC to broader cooling and heating applications.  
It bridges the gap between **climate science** and **energy engineering**, with runnable examples in `examples/` so you can learn by doing.

---


## Current Features

- Compute **COP** for single-stage vapor-compression systems via **CoolProp**.  
- Compute **Sensible Heat Ratio (SHR)** from temperature + RH or dew point.  
- Compute **Effective COP (ECOP)** as `COP × SHR` for more realistic system performance.  
- Compute **Cooling Degree Days (CDD)** exceedance and **eCDD** (`CDD / (COP × SHR)`).  
- Validate refrigerant names and thermodynamic parameters before computation.  
- Automatically handle **physically impossible** or **unstable** states (returns `NaN`).  
- Generate **COP reference charts** and **SHR temperature–RH maps** with optional saving.  
- Includes a full **pytest** suite with coverage enforcement.  

---

## Installation

Stable:
```bash
pip install cedar-toolkit
```

Development version:
```bash
git clone https://github.com/jake-casselman/cedar.git
cd cedar
pip install -e .[dev]
```

---


## COP Reference Chart Example

<p align="center">
<img src="docs/source/_static/cop_chart_example.png" alt="COP reference chart" width="75%" />
</p>

### SHR temperature–RH map

<p align="center">
<img src="docs/source/_static/shr_temp_rh_map.png" alt="SHR vs temperature and relative humidity map" width="75%" />
</p>

## Example usage

```python
from cedar.metrics.cop import SingleFluidCOP

hp = SingleFluidCOP(
    "R134a",
    t_evap_k=273.15,
    delta_t_cond=10,
    eta_is=0.8,
    delta_t_min=10.0,
)
print(hp.cop(298.15))           # Single value
print(hp.cop([280, 290, 300]))  # Vectorized array
hp.plot(show=True)              # Plot COP curve
```

> **Warning:** Following layered architecture best practices, this function does **not** perform any input validation, logging, or plotting. Those features belong in higher-level modules.

See also runnable examples in `examples/`:
- `examples/cop_example.py` — COP calculation + saved chart/CSV.
- `examples/shr_example.py` — SHR from dew point or RH + saved map/CSV.
- `examples/effective_cop_example.py` — ECOP (COP × SHR) demo.
- `examples/cdd_example.py` — CDD exceedance demo.
- `examples/effective_cdd_example.py` — eCDD (CDD / eCOP) demo.

### Sensible Heat Ratio (SHR) example

```python
from cedar.metrics.shr import SensibleHeatRatioModel

shr_model = SensibleHeatRatioModel(
    p_atm=101_325.0,
    t_evap_k=273.15,
    approach_temp=1.0,
    C_p=1020.05,
    H_fg=2.501e6,
    rh_out=1.0,
)

# Use dew point (Kelvin) to compute RH internally
temps_K = [295.0, 300.0]
dewpoint_K = [283.15, 288.15]
shr = shr_model.shr(temps_K, dewpoint_array=dewpoint_K)
print(shr)  # array of SHR values

# Or supply RH directly:
# rh = [0.47, 0.65]
# shr = shr_model.shr(temps_K, rh_array=rh)
```

### Effective COP (ECOP) example

```python
from cedar.metrics.cop import SingleFluidCOP
from cedar.metrics.effective_cop import EffectiveCOP

ecop_model = EffectiveCOP(
    cop_kwargs=dict(
        fluid="R134a",
        t_evap_k=273.15,
        delta_t_cond=10,
        eta_is=0.8,
        delta_t_min=10.0,
    ),
    shr_kwargs=dict(
        p_atm=101_325.0,
        t_evap_k=273.15,
        approach_temp=1.0,
        C_p=1020.05,
        H_fg=2.501e6,
        rh_out=1.0,
    ),
)

temps_K = [295.0, 300.0]
dewpoint_K = [283.15, 288.15]
ecop_vals = ecop_model.ecop(temps_K, dewpoint_array=dewpoint_K)
print(ecop_vals)  # COP × SHR
```
> **Note:** Use consistent thermodynamic setup between COP and SHR (e.g., same
> evaporator temperature, approach, and outlet RH assumptions) so ECOP/eCDD
> reflect the same operating point.

---

## Project structure

```text
src/
└── cedar/
    ├── metrics/
    │   ├── cop.py               # High-level COP model interface
    │   └── shr.py               # Sensible heat ratio model (RH or dew point)
    ├── physics/
    │   ├── cop.py               # Core thermodynamic equations (COP)
    │   └── shr.py               # SHR physics helpers and RH-from-dewpoint
    ├── utils/
    │   ├── validation.py        # Input validation helpers
    │   ├── interpolation.py     # Interpolation utilities
    │   └── plotting.py          # Plotting helpers
    └── tests/
        └── test_cop.py          # Pytest suite with coverage ≥85%
```

---

## Local Development

```bash
git clone https://github.com/jake-casselman/cedar.git
cd cedar
python3 -m venv venv && source venv/bin/activate
pip install -e .[dev]
```

<details>
<summary><strong>macOS ARM (Apple Silicon) users</strong></summary>

SciPy requires OpenBLAS. Install system dependencies first:

```bash
brew install openblas cmake pkg-config llvm
```

Then export the following before `pip install`:

```bash
export CC="$(brew --prefix llvm)/bin/clang"
export CXX="$(brew --prefix llvm)/bin/clang++"
export CPPFLAGS="-I$(brew --prefix llvm)/include -I$(brew --prefix openblas)/include"
export LDFLAGS="-L$(brew --prefix llvm)/lib -L$(brew --prefix openblas)/lib"
export PKG_CONFIG_PATH="$(brew --prefix openblas)/lib/pkgconfig"
```

</details>

---

## Documentation

```bash
# Install documentation dependencies (docs extra)
pip install -e .[docs]

# Build and view
cd docs
make clean && make html
open build/html/index.html   # macOS
```

---

## Funding

This research is based upon work supported by the National Science Foundation under award number EEC-2330175 for the Engineering Research Center EARTH.

---

## Citation

If you use **CEDAR** in your research, please cite **both** the software and the
accompanying paper (see [`CITATION.cff`](CITATION.cff)):

**Software:**

> Casselman, J. W., & Karamperidou, C. (2026). *CEDAR: Climate & Energy
> Diagnostics for Applied Refrigeration* (v1.0.0). Zenodo.
> <https://doi.org/10.5281/zenodo.18274828>

**Paper:**

> Casselman, J. W., & Karamperidou, C. (2026). *Efficiency-weighted cooling
> degree days reveal opposing temperature and humidity effects on energy
> demand.* Nature Communications. <https://doi.org/10.21203/rs.3.rs-8683958/v1>
> (in press)

**Corresponding authors:**

- Jake W. Casselman — [jakewc@hawaii.edu](mailto:jakewc@hawaii.edu)
- Christina Karamperidou — [ckaramp@hawaii.edu](mailto:ckaramp@hawaii.edu)

---

## License

Released under the [GNU Affero General Public License v3.0](LICENSE).

CEDAR is free software: you may use, modify, and redistribute it under the terms
of the AGPL-3.0. If you run a modified version of CEDAR to provide a service over
a network, you must make the complete corresponding source code of your modified
version available to its users. See the [LICENSE](LICENSE) for full terms.

**Attribution required.** Under an additional term (AGPL §7(b)), any work that
uses, conveys, or makes CEDAR available over a network must preserve the CEDAR
attribution notice in its credits / "Appropriate Legal Notices." See
[LICENSE-ADDITIONAL-TERMS.md](LICENSE-ADDITIONAL-TERMS.md) for the exact wording.

If you use CEDAR in research, please also cite it — see [Citation](#-citation)
above.

---

## Acknowledgments

Developed by **Jake W. Casselman** as part of ongoing climate–energy research at the **University of Hawai‘i** and **[ERC Earth](https://erc-earth.ku.edu/)**.  

---
