# Getting started

**CEDAR: Climate & Energy Diagnostics for Applied Refrigeration** links climate
data to refrigeration physics and energy performance. Core metrics include:
- **COP** (vectorized, single-stage vapor-compression)
- **SHR** (dew point → RH or direct RH)
- **ECOP** = COP × SHR
- **CDD** and **eCDD** = CDD / (COP × SHR)

## TL;DR (three lines)

```python
from cedar.metrics.cop import SingleFluidCOP
from cedar.metrics.shr import SensibleHeatRatioModel
from cedar.metrics.effective_cop import EffectiveCOP

hp = SingleFluidCOP(
    "R134a",
    t_evap_k=273.15,
    delta_t_cond=10,
    eta_is=0.8,
    delta_t_min=10.0,
)
shr_model = SensibleHeatRatioModel()
ecop = EffectiveCOP(cop_model=hp, shr_model=shr_model)

hp.cop([280.0, 290.0, 300.0])             # COP array
shr_model.shr([295.0, 300.0], dewpoint_array=[283.0, 288.0])  # SHR
ecop.ecop([295.0, 300.0], dewpoint_array=[283.0, 288.0])      # ECOP
```

For a reference curve:

```python
hp.plot(show=True)
# or: hp.plot(show=False, save_path="outputs/cop_chart.png")
```

```{tip}
Working with gridded climate fields? Pass a NumPy array of shape `(lat, lon)` or
`(time, lat, lon)` directly to `hp.cop(...)`.
```

## What’s inside

```
src/
└── cedar/
    ├── metrics/            # High-level interfaces
    │   ├── cop.py          # COP models
    │   ├── shr.py          # SHR models
    │   ├── effective_cop.py# ECOP = COP × SHR
    │   ├── cdd.py          # Cooling Degree Days
    │   └── effective_cdd.py# eCDD = CDD / (COP × SHR)
    ├── physics/            # Core thermodynamic equations
    │   ├── cop.py
    │   └── shr.py
    ├── utils/              # Helpers
    │   ├── validation.py
    │   ├── interpolation.py
    │   └── plotting.py
    └── tests/
        ├── test_cop.py
        └── test_shr.py
```

## Next steps

- **Install** the package (see [Installation](installation.md)).
- **Run tests** to verify your environment:
  ```bash
  pytest --cov=cedar --cov-report=term-missing -v
  ```
- **Browse examples** in your README or tutorials to wire this into your pipeline.
