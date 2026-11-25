"""
cedar.physics.shr
-----------------
Core physics routines for Sensible Heat Ratio (SHR).

Provides relative humidity from dew point and the base SHR calculation.
All units are SI: Kelvin, Pascal, and dimensionless ratios.
"""

from __future__ import annotations

import math
import numpy as np
from numpy.typing import ArrayLike


def compute_relative_humidity(t2m: ArrayLike, d2m: ArrayLike) -> np.ndarray:
    """Return relative humidity [0,1] from temperature and dewpoint in Kelvin."""
    t2m = np.asarray(t2m, dtype=float)
    d2m = np.asarray(d2m, dtype=float)
    rh = np.exp(
        (17.625 * (d2m - 273.15) / (243.04 + (d2m - 273.15)))
        - (17.625 * (t2m - 273.15) / (243.04 + (t2m - 273.15)))
    )
    return np.clip(rh, 0.0, 1.0)


def _p_sat(T_K: ArrayLike) -> np.ndarray:
    """Saturation vapor pressure (Pa) given absolute temperature (K) via Magnus."""
    T_K = np.asarray(T_K, dtype=float)
    return 610.78 * np.exp((17.27 * (T_K - 273.15)) / ((T_K - 273.15) + 237.3))


def _p_v(rh: ArrayLike, T_K: ArrayLike) -> np.ndarray:
    """Partial vapor pressure (Pa)."""
    rh = np.asarray(rh, dtype=float)
    return rh * _p_sat(T_K)


def _humidity_ratio(p_v: ArrayLike, p_atm: float) -> np.ndarray:
    """Humidity ratio (kg water/kg dry air)."""
    p_v = np.asarray(p_v, dtype=float)
    return 0.622 * p_v / (p_atm - p_v)


def sensible_heat_ratio(
    t_in_k: ArrayLike,
    rh_in: ArrayLike,
    *,
    p_atm: float = 101325.0,
    t_evap_k: float = 273.15,
    approach_temp: float = 1.0,
    C_p: float = 1020.05,
    H_fg: float = 2.501e6,
    rh_out: float = 1.0,
) -> np.ndarray:
    """
    Compute SHR for inlet air temperature and relative humidity.

    Parameters
    ----------
    t_in_k : array-like
        Inlet air temperature [K].
    rh_in : array-like
        Inlet relative humidity [0, 1].
    p_atm : float
        Atmospheric pressure [Pa].
    t_evap_k : float
        Evaporator saturation temperature [K].
    approach_temp : float
        Approach temperature [K].
    C_p : float
        Specific heat capacity of air at constant pressure [J/kg-K].
    H_fg : float
        Latent heat of vaporization of water [J/kg].
    rh_out : float
        Outlet relative humidity [0, 1], capped at saturation.
    """
    t_in_k = np.asarray(t_in_k, dtype=float)
    rh_in = np.asarray(rh_in, dtype=float)

    t_out_k = t_evap_k + approach_temp

    # inlet
    p_v_in = _p_v(rh_in, t_in_k)
    w_in = _humidity_ratio(p_v_in, p_atm)

    # outlet (saturate at rh_out)
    p_v_out = _p_v(np.minimum(rh_out, 0.999), t_out_k)
    w_out = _humidity_ratio(p_v_out, p_atm)

    sensible_heat = C_p * (t_in_k - t_out_k)
    latent_heat = H_fg * np.maximum(w_in - w_out, 0.0)
    total_heat = sensible_heat + latent_heat

    shr = sensible_heat / total_heat
    return np.clip(shr, 0.0, 1.0)


def sensible_heat_ratio_components(
    t_in_k: ArrayLike,
    rh_in: ArrayLike,
    *,
    p_atm: float = 101325.0,
    t_evap_k: float = 273.15,
    approach_temp: float = 1.0,
    C_p: float = 1020.05,
    H_fg: float = 2.501e6,
    rh_out: float = 1.0,
) -> dict[str, np.ndarray]:
    """
    Compute SHR and its physical component terms.

    Returns
    -------
    dict
        Mapping containing:
        - ``rh_in``: inlet relative humidity [0, 1]
        - ``p_v_in``: inlet partial vapor pressure [Pa]
        - ``w_in``: inlet humidity ratio [kg/kg dry air]
        - ``p_v_out``: outlet partial vapor pressure [Pa]
        - ``w_out``: outlet humidity ratio [kg/kg dry air]
        - ``sensible_heat``: sensible heat term [J/kg dry air]
        - ``latent_heat``: latent heat term [J/kg dry air]
        - ``total_heat``: total heat term [J/kg dry air]
        - ``shr``: sensible heat ratio [0, 1]
    """
    t_in_k = np.asarray(t_in_k, dtype=float)
    rh_in = np.asarray(rh_in, dtype=float)

    t_out_k = t_evap_k + approach_temp

    p_v_in = _p_v(rh_in, t_in_k)
    w_in = _humidity_ratio(p_v_in, p_atm)

    p_v_out = _p_v(np.minimum(rh_out, 0.999), t_out_k)
    w_out = _humidity_ratio(p_v_out, p_atm)

    sensible_heat = C_p * (t_in_k - t_out_k)
    latent_heat = H_fg * np.maximum(w_in - w_out, 0.0)
    total_heat = sensible_heat + latent_heat
    shr = np.clip(sensible_heat / total_heat, 0.0, 1.0)

    return {
        "rh_in": rh_in,
        "p_v_in": p_v_in,
        "w_in": w_in,
        "p_v_out": np.asarray(p_v_out, dtype=float),
        "w_out": np.asarray(w_out, dtype=float),
        "sensible_heat": sensible_heat,
        "latent_heat": latent_heat,
        "total_heat": total_heat,
        "shr": shr,
    }


def sensible_heat_ratio_from_dewpoint(
    t_in: ArrayLike,
    dewpoint: ArrayLike,
    **kwargs,
) -> np.ndarray:
    """Convenience wrapper: compute SHR when dew point is provided instead of RH."""
    rh = compute_relative_humidity(t_in, dewpoint)
    return sensible_heat_ratio(t_in, rh, **kwargs)
