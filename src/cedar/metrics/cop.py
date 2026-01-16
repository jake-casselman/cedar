"""
cedar.metrics.cop
-----------------
High-performance COP calculator for a single refrigerant.

Builds a dense lookup table once (CoolProp sweep) and provides
fast interpolated access for arbitrary temperature fields (1–3D arrays).
"""

from typing import Union, Optional
from pathlib import Path
import numpy as np
import logging

from cedar.physics.cop import cop_single
from cedar.utils.validation import validate_refrigerant, validate_params
from cedar.utils.interpolation import build_interpolator
from cedar.utils.plotting import plot_cop_chart
class SingleFluidCOP:
    """
    Compute COP for one refrigerant across a wide temperature range.
    Fast because it builds a dense lookup table once and interpolates thereafter.

    Parameters
    ----------
    fluid : str
        CoolProp fluid string, e.g. "R134a".
    t_evap_k : float
        Evaporator saturation temperature [K].
    delta_t_cond : float
        Condenser–ambient temperature difference [K].
    eta_is : float, default 0.8
        Compressor isentropic efficiency (0 < η ≤ 1].
    delta_t_min : float, default 10
        Minimum allowable temperature lift [K].
    verbose : bool, default False
        Log progress info.
    logger : logging.Logger, optional
        Custom logger. If None, a module-level logger is created.
    """

    def __init__(
        self,
        fluid: str,
        t_evap_k: float,
        delta_t_cond: float,
        eta_is: float = 0.8,
        delta_t_min: float = 10.0,
        *,
        verbose: bool = False,
        logger: Optional[logging.Logger] = None,
    ) -> None:

        self._log = logger or logging.getLogger("SingleFluidCOP")
        self._verbose = bool(verbose)

        # Validate inputs
        from CoolProp.CoolProp import PropsSI  # lazy import for startup speed
        validate_refrigerant(fluid, PropsSI)
        validate_params(t_evap_k, delta_t_cond, eta_is, delta_t_min)

        self.fluid = fluid
        self.t_evap_k = float(t_evap_k)
        self.delta_t_cond = float(delta_t_cond)
        self.eta_is = float(eta_is)
        self.delta_t_min = float(delta_t_min)

        if self._verbose:
            self._log.info(f"🔧 Building COP lookup for {fluid}")
            self._log.info(f"   T_evap: {t_evap_k:.1f} K  ΔT_cond: {delta_t_cond:.1f} K")

        # Build dense table
        self.T_dense = np.linspace(175.0, 330.0, 2000)
        self._build_table()

        if self._verbose:
            valid = np.isfinite(self.cop_dense).sum()
            self._log.info(f"✅ Table ready ({valid}/{self.T_dense.size} valid points)")

        # Interpolator
        self._interp = build_interpolator(self.T_dense, self.cop_dense)

    # ------------------------------------------------------------------
    def _build_table(self):
        """Run dense CoolProp sweep once per fluid setup."""
        cop_vals = np.full_like(self.T_dense, np.nan, dtype=float)
        for i, T_amb in enumerate(self.T_dense):
            T_cond = T_amb + self.delta_t_cond
            if (T_cond - self.t_evap_k) >= self.delta_t_min:
                cop_vals[i] = cop_single(self.fluid, self.t_evap_k, T_cond, self.eta_is)
        self.cop_dense = cop_vals

    # ------------------------------------------------------------------
    def cop(self, t_ambient_k: Union[float, int, np.ndarray]) -> np.ndarray:
        """Return COP for arbitrary-shaped temperature array [K]."""
        return self._interp(np.asarray(t_ambient_k, dtype=float))

    # ------------------------------------------------------------------
    def plot(self, **kwargs):
        """Quick plotting wrapper."""
        kwargs.setdefault("verbose", self._verbose)
        return plot_cop_chart(
            self.T_dense,
            self.cop_dense,
            self.fluid,
            logger=self._log,
            **kwargs,
        )