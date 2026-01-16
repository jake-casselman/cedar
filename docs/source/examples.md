# Examples (Python scripts)

Prefer a narrative, notebook-style walkthrough? See
[Cedar walkthrough](user-guide/cedar-walkthrough.md) (adapted from `cedar.ipynb`).

Hands-on Python scripts demonstrating COP, SHR, and ECOP workflows:

- **COP**: `examples/cop_example.py` — instantiate `SingleFluidCOP`, compute scalar/array COP values, and adjust efficiency or minimum lift.
- **SHR**: `examples/shr_example.py` — compute sensible heat ratio using either dew point (converted to RH internally) or direct RH input with `SensibleHeatRatioModel`.
- **ECOP**: `examples/effective_cop_example.py` — compute effective COP (`COP × SHR`) for ambient temps + humidity.
- **CDD**: `examples/cdd_example.py` — hourly cooling degree days exceedance.
- **eCDD**: `examples/effective_cdd_example.py` — effective CDD (`CDD / (COP × SHR)`).

Run locally (Python 3.12+ recommended):

```bash
pip install -e .[dev]
python examples/cop_example.py   # saves outputs/cop_curve.png and cop_profile.csv
python examples/shr_example.py   # saves outputs/shr_field.png and shr_1d_profile.csv
python examples/effective_cop_example.py  # saves outputs/ecop_profile.csv
python examples/cdd_example.py   # saves outputs/cdd_profile.csv
python examples/effective_cdd_example.py  # saves outputs/ecdd_profile.csv
```

Feel free to drop these into a notebook if you prefer an interactive workflow.
