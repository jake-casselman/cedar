"""
cedar.metrics.shr
-----------------
High-level Sensible Heat Ratio (SHR) interface.

Provides on-the-fly SHR calculation and an optional grid-based interpolator for
fast reuse. Accepts either relative humidity or dew point inputs.
"""

from __future__ import annotations

import warnings
from typing import Optional, Iterable
import numpy as np
from numpy.typing import ArrayLike
from scipy.interpolate import RegularGridInterpolator

from cedar.physics.shr import (
    compute_relative_humidity,
    sensible_heat_ratio,
)

# Physical constants for default assumptions
_DEFAULT_T_EVAP_K = 273.15  # 0°C — standard for comfort cooling coils
_DEFAULT_RH_OUT = 1.0       # Saturated air leaving the coil


class SensibleHeatRatioModel:
    """
    Compute Sensible Heat Ratio (SHR) for air-handling conditions.

    By default this computes SHR directly for the provided inputs (no prebuilt
    grid). If you supply `t_grid` and `rh_grid`, it will precompute a regular
    grid and interpolate for faster repeated calls.

    Important Physical Assumptions
    ------------------------------
    The default parameters assume a **standard comfort cooling scenario**:

    - **t_evap_k = 273.15 K (0°C)**: Evaporator surface temperature. This is a
      common design point for air conditioning where the coil operates just
      above freezing to maximize dehumidification without frost.

    - **rh_out = 1.0 (100%)**: Air leaving the cooling coil is assumed to be
      saturated. This is physically accurate when air passes over a cold coil
      at or below its dew point—moisture condenses until the air reaches
      saturation at the coil surface temperature.

    .. warning::
       Changing these defaults requires careful physical justification:

       - **rh_out < 1.0** implies incomplete contact with the coil or bypass
         air. Only use if modeling a specific coil with known bypass factor.

       - **t_evap_k ≠ 273.15 K (0°C)** should match your actual system design.
         Lower values (e.g., 263 K / -10°C for freezers) will change the
         saturation pressure and thus the SHR calculation significantly.
    """

    def __init__(
        self,
        *,
        p_atm: float = 101325.0,
        t_evap_k: float = _DEFAULT_T_EVAP_K,
        approach_temp: float = 1.0,
        C_p: float = 1020.05,
        H_fg: float = 2.501e6,
        rh_out: float = _DEFAULT_RH_OUT,
        t_grid: Optional[Iterable[float]] = None,
        rh_grid: Optional[Iterable[float]] = None,
    ) -> None:
        # Validate and warn about non-standard parameters
        self._validate_assumptions(t_evap_k, rh_out)

        self.p_atm = p_atm
        self.t_evap_k = t_evap_k
        self.approach_temp = approach_temp
        self.C_p = C_p
        self.H_fg = H_fg
        self.rh_out = rh_out

        self._interp = None
        if t_grid is not None and rh_grid is not None:
            self.t_vals = np.asarray(list(t_grid), dtype=float)
            self.rh_vals = np.asarray(list(rh_grid), dtype=float)
            self._build_interpolator()
        else:
            self.t_vals = None
            self.rh_vals = None

    @staticmethod
    def _validate_assumptions(t_evap_k: float, rh_out: float) -> None:
        """Warn users about non-standard parameter choices."""
        if rh_out != _DEFAULT_RH_OUT:
            warnings.warn(
                f"rh_out={rh_out} differs from the default of 1.0 (saturated air). "
                f"This assumes air leaving the coil is NOT fully saturated, which "
                f"is uncommon in standard cooling coil analysis. Only use this if "
                f"you are modeling a specific coil with a known bypass factor or "
                f"partial contact scenario. For most applications, rh_out=1.0 is "
                f"physically appropriate.",
                UserWarning,
                stacklevel=3,
            )

        if not np.isclose(t_evap_k, _DEFAULT_T_EVAP_K, atol=0.5):
            warnings.warn(
                f"t_evap_k={t_evap_k:.2f} K ({t_evap_k - 273.15:.1f}°C) differs from "
                f"the default of 273.15 K (0°C). The default assumes a comfort cooling "
                f"coil operating just above freezing. If you are modeling a different "
                f"system (e.g., refrigeration at 263 K / -10°C or heat pump at 278 K / +5°C), "
                f"ensure your t_evap_k matches the actual evaporator saturation temperature.",
                UserWarning,
                stacklevel=3,
            )

    def _build_interpolator(self) -> None:
        """Precompute SHR grid and build interpolator."""
        shr_grid = np.zeros((len(self.t_vals), len(self.rh_vals)))
        for i, T in enumerate(self.t_vals):
            for j, RH in enumerate(self.rh_vals):
                shr_grid[i, j] = sensible_heat_ratio(
                    T,
                    RH,
                    p_atm=self.p_atm,
                    t_evap_k=self.t_evap_k,
                    approach_temp=self.approach_temp,
                    C_p=self.C_p,
                    H_fg=self.H_fg,
                    rh_out=self.rh_out,
                )
        self._interpolator = RegularGridInterpolator(
            (self.t_vals, self.rh_vals),
            shr_grid,
            bounds_error=False,
            fill_value=None,
        )

    def interpolate_shr(self, T_array: ArrayLike, rh_array: ArrayLike) -> np.ndarray:
        """Interpolate SHR for matched temperature and RH arrays."""
        T_array = np.asarray(T_array, dtype=float)
        rh_array = np.asarray(rh_array, dtype=float)
        if T_array.shape != rh_array.shape:
            raise ValueError("T_array and rh_array must have the same shape.")

        points = np.column_stack((T_array.ravel(), rh_array.ravel()))
        shr_values = self._interpolator(points)
        return shr_values.reshape(T_array.shape)

    def shr(
        self,
        T_array: ArrayLike,
        *,
        rh_array: Optional[ArrayLike] = None,
        dewpoint_array: Optional[ArrayLike] = None,
    ) -> np.ndarray:
        """
        Compute SHR given temperature and either RH or dew point (one-to-one).
        """
        if (rh_array is None and dewpoint_array is None) or (
            rh_array is not None and dewpoint_array is not None
        ):
            raise ValueError("Provide exactly one of rh_array or dewpoint_array.")

        T_array = np.asarray(T_array, dtype=float)
        if dewpoint_array is not None:
            rh_array = compute_relative_humidity(T_array, dewpoint_array)
        else:
            rh_array = np.asarray(rh_array, dtype=float)

        if self._interp is not None:
            return self.interpolate_shr(T_array, rh_array)

        return sensible_heat_ratio(
            T_array,
            rh_array,
            p_atm=self.p_atm,
            t_evap_k=self.t_evap_k,
            approach_temp=self.approach_temp,
            C_p=self.C_p,
            H_fg=self.H_fg,
            rh_out=self.rh_out,
        )
