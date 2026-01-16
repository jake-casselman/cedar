# COP quickstart

Two ways to compute COP in **CEDAR: Climate & Energy Diagnostics for Applied Refrigeration**:
1) a fast, vectorized class for ambient temperature fields, and  
2) a minimal “single state” helper for one operating point.

```{tip}
For a longer, figure-heavy tutorial adapted from `cedar.ipynb`, see
[Cedar walkthrough](cedar-walkthrough.md).
```

## 1) Vectorized workflow — `SingleFluidCOP`

```python
from cedar.metrics.cop import SingleFluidCOP

hp = SingleFluidCOP(
    "R134a",
    t_evap_k=273.15,
    delta_t_cond=10,
    eta_is=0.8,
    delta_t_min=10.0,
)

print(hp.cop(298.15))                # single value (K)
print(hp.cop([280, 290, 300]))       # vectorized over an array
hp.plot(show=True)                   # quick reference plot
# Or save instead of showing:
# hp.plot(show=False, save_path="outputs/r134a_cop.png", dpi=300)
```

```{note}
`SingleFluidCOP` builds a dense lookup table once (CoolProp sweep) and then
returns fast interpolated values for arbitrary 1–3D arrays of ambient
temperature.
```

## 2) Single state helper — `cop_single`

```python
from cedar.physics.cop import cop_single

cop = cop_single("R134a", t_evap_k=273.15, t_cond_k=295.0, eta_is=0.8)
print(cop)  # returns NaN if the state is unphysical
```

```{warning}
`cop_single` is intentionally minimal: **no** input validation, plotting, or
logging. Use it inside higher-level code that handles those concerns.
```

## Notes & tips

- Refrigerant names are validated against **CoolProp** (in the vectorized class).
- Unphysical conditions (e.g., `t_cond_k <= t_evap_k` or too small lift) return `NaN`.
- Temperatures are **Kelvin**. If you think in °C, use `T[K] = T[°C] + 273.15`.

---

# SHR quickstart

Compute Sensible Heat Ratio (SHR) using temperature plus either relative humidity or dew point.

```{figure} ../_static/shr_temp_rh_map.png
:alt: SHR vs temperature and relative humidity
:width: 75%
:align: center

Example SHR map for temperature (x) and relative humidity (y) with 0.1 contours.
```

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

# Dew point path (dew point -> RH -> SHR)
temps_K = [295.0, 300.0]
dewpoint_K = [283.15, 288.15]
shr = shr_model.shr(temps_K, dewpoint_array=dewpoint_K)
print(shr)  # e.g., [0.704..., 0.62...]

# Or provide relative humidity directly
rh = [0.47, 0.65]
shr_direct = shr_model.shr(temps_K, rh_array=rh)
```

If you pass both `rh_array` and `dewpoint_array`, or neither, the model raises a
`ValueError` to prevent ambiguous inputs.

See also the runnable scripts in `examples/`:
- `examples/cop_example.py` for COP basics
- `examples/shr_example.py` for SHR via RH or dew point
- `examples/effective_cop_example.py` for ECOP (COP × SHR) using COP/SHR kwargs

---

# ECOP quickstart (COP × SHR)

Compute effective COP by combining COP and SHR models.

```python
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

```{note}
Keep COP and SHR assumptions aligned (e.g., same evaporator temperature,
approach temperature, outlet RH) so ECOP and eCDD reflect one operating point.
```

---

# CDD & eCDD quickstart

- **CDD** (hourly exceedance):

```python
from cedar.metrics.cdd import CoolingDegreeDays

cdd = CoolingDegreeDays(base_temperature_K=18.0 + 273.15)
temps_K = [290.0, 293.0, 296.0]
exceed = cdd.cdd(temps_K)
print(exceed)
```

- **eCDD** (CDD / eCOP):

```python
from cedar.metrics.effective_cdd import EffectiveCDD

ecdd_model = EffectiveCDD(
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
    cdd_kwargs=dict(base_temperature_K=18.0 + 273.15),
)

temps_K = [295.0, 300.0]
dewpoint_K = [283.15, 288.15]
ecdd_vals = ecdd_model.ecdd(temps_K, dewpoint_array=dewpoint_K)
print(ecdd_vals)
```
