"""
cedar.physics.cop
-----------------
Core thermodynamic routine for a single-stage vapor-compression cycle.

This module is deliberately minimal: it computes the COP for *one* state point
given refrigerant, evaporator temperature, condenser temperature, and efficiency.

Warning, following layered architecture best practices, this module does NOT
perform any input validation, logging, or plotting. Those features belong in
higher-level modules.
"""

from CoolProp.CoolProp import PropsSI

def cop_single(
    fluid: str,
    t_evap_k: float,
    t_cond_k: float,
    eta_is: float = 0.8,
) -> float:
    """
    Compute the coefficient of performance (COP) for a single-stage
    vapor-compression refrigeration cycle.

    Parameters
    ----------
    fluid : str
        CoolProp fluid string, e.g. "R134a".
    t_evap_k : float
        Evaporator saturation temperature [K].
    t_cond_k : float
        Condenser saturation temperature [K].
    eta_is : float, optional
        Compressor isentropic efficiency (0 < eta_is ≤ 1).

    Returns
    -------
    float
        The COP value, or NaN if invalid or physically impossible.
    """
    if t_cond_k <= t_evap_k:
        return float("nan")

    try:
        h1 = PropsSI("H", "T", t_evap_k, "Q", 1, fluid)
        s1 = PropsSI("S", "T", t_evap_k, "Q", 1, fluid)
        P_c = PropsSI("P", "T", t_cond_k, "Q", 0, fluid)
        h2s = PropsSI("H", "P", P_c, "S", s1, fluid)
        h2 = h1 + (h2s - h1) / eta_is
        h3 = PropsSI("H", "T", t_cond_k, "Q", 0, fluid)
        w_in = h2 - h1
        if w_in <= 0:
            print(f"Invalid w_in={w_in:.3f} for fluid={fluid}, skipping.")
            return float("nan")
        return (h1 - h3) / w_in
    except Exception:
        return float("nan")