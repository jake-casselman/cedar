"""
Helper routines for input validation.
"""

import warnings

def validate_refrigerant(fluid: str, PropsSI) -> None:
    """Raise ValueError if the refrigerant name is not recognized."""
    try:
        PropsSI("P", "T", 273.15, "Q", 0, fluid)
    except ValueError as e:
        raise ValueError(f"Refrigerant '{fluid}' not recognised by CoolProp.") from e

def validate_params(t_evap_k, delta_t_cond, eta_is, delta_t_min):
    """Check basic parameter sanity and warn if temperatures seem non-Kelvin."""
    # Basic value checks
    if t_evap_k <= 0:
        raise ValueError("`t_evap_k` must be > 0 K.")
    if delta_t_cond < 0:
        raise ValueError("`delta_t_cond` must be ≥ 0 K.")
    if not (0 < eta_is <= 1):
        raise ValueError("`eta_is` must be in (0, 1].")
    if delta_t_min < 0:
        raise ValueError("`delta_t_min` must be ≥ 0 K.")

    # Kelvin plausibility checks (issue warnings, not errors)
    if t_evap_k < 100:
        warnings.warn(
            f"`t_evap_k` = {t_evap_k:.1f} is unusually low. "
            "Did you input Celsius instead of Kelvin?",
            UserWarning,
        )
    elif t_evap_k < 200:
        warnings.warn(
            f"`t_evap_k` = {t_evap_k:.1f} K is very low. "
            "Double-check if this is truly Kelvin.",
            UserWarning,
        )
    elif t_evap_k < 373 and t_evap_k < 200 + delta_t_cond:
        # optional subtle check: looks Celsius-like (20–40°C typical)
        if t_evap_k < 200:
            pass  # already warned
        else:
            warnings.warn(
                f"`t_evap_k` = {t_evap_k:.1f} might be in °C. "
                "Typical Kelvin values are around 270–310 K for HVAC systems.",
                UserWarning,
            )
 