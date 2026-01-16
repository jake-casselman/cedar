# Changelog

All notable changes to CEDAR will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [1.0.0] - 2026-01-16

### Added
- Initial public release of CEDAR
- **COP module**: Single-stage vapor-compression cycle COP via CoolProp
  - `SingleFluidCOP` class with vectorized evaluation and interpolation
  - `cop_single` low-level physics function
- **SHR module**: Sensible Heat Ratio from temperature + RH or dew point
  - `SensibleHeatRatioModel` class with optional grid interpolation
  - Physics helpers for RH computation from dew point
  - Validation warnings for non-standard `rh_out` and `t_evap_k` values
  - Detailed docstrings explaining physical assumptions (saturated coil air, 0°C evaporator)
- **PEP 8 compliant**: All variable and parameter names follow Python's official style guide
  - snake_case throughout (e.g., `t_evap_k`, `t_cond_k`, `rh_out`, `delta_t_cond`)
- **ECOP module**: Effective COP = COP × SHR
- **CDD module**: Cooling Degree Days exceedance calculation
- **eCDD module**: Effective CDD = CDD / ECOP
- Validation utilities for refrigerant names and thermodynamic parameters
- Plotting utilities for COP charts and SHR maps
- Full pytest suite with ≥85% coverage requirement
- Sphinx documentation with Furo theme
- Example scripts in `examples/`

[Unreleased]: https://github.com/jake-casselman/cedar/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jake-casselman/cedar/releases/tag/v1.0.0
