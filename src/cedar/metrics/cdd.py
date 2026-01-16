"""
cedar.metrics.cdd
-----------------
Cooling Degree Days (CDD) helper.

Computes per-hour degree exceedance above a base temperature. This is a simple
utility: given ambient temperatures, it returns the positive difference from the
base (°K) and zero otherwise. Daily/monthly aggregation is left to callers
(`xarray` resampling, summing, etc.).

Example:
    >>> cdd = CoolingDegreeDays(base_temperature_K=18.0 + 273.15)
    >>> cdd.exceedance([290.0, 293.0, 296.0])  # mix of below/above base
    array([0.  , 1.85, 4.85])
    >>> cdd.exceedance([270.0, 273.0])         # below base → zeros
    array([0., 0.])
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


class CoolingDegreeDays:
    """Compute hourly CDD exceedance against a base temperature."""

    def __init__(self, base_temperature_K: float = 18.0 + 273.15) -> None:
        self.base_temperature_K = base_temperature_K

    def exceedance(self, t_ambient_k: ArrayLike) -> np.ndarray:
        """Return degree exceedance [K] where ambient exceeds the base temperature."""
        T_arr = np.asarray(t_ambient_k, dtype=float)
        return np.clip(T_arr - self.base_temperature_K, 0.0, None)

    def cdd(self, t_ambient_k: ArrayLike) -> np.ndarray:
        """Alias for exceedance; represents hourly CDD contribution."""
        return self.exceedance(t_ambient_k)
