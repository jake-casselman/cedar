"""
cedar.metrics.effective_cdd
---------------------------
Effective Cooling Degree Days (eCDD) combining CDD, COP, and SHR.

eCDD = CDD / (COP × SHR) = CDD / ECOP represents cooling demand
adjusted for system efficiency under real climate conditions.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from numpy.typing import ArrayLike

from cedar.metrics.cdd import CoolingDegreeDays
from cedar.metrics.cop import SingleFluidCOP
from cedar.metrics.shr import SensibleHeatRatioModel


class EffectiveCDD:
    """
    Compute eCDD = CDD / (COP × SHR) to approximate load adjusted by efficiency.

    You can pass pre-built models or provide kwargs to build them here.
    """

    def __init__(
        self,
        *,
        cdd_model: Optional[CoolingDegreeDays] = None,
        cop_model: Optional[SingleFluidCOP] = None,
        shr_model: Optional[SensibleHeatRatioModel] = None,
        cdd_kwargs: Optional[dict] = None,
        cop_kwargs: Optional[dict] = None,
        shr_kwargs: Optional[dict] = None,
    ) -> None:
        self.cdd_model = cdd_model or CoolingDegreeDays(**(cdd_kwargs or {}))
        if cop_model is None and cop_kwargs is None:
            raise ValueError("Provide either cop_model or cop_kwargs to build one.")
        if cop_model is None:
            cop_model = SingleFluidCOP(**cop_kwargs)  # type: ignore[arg-type]
        self.cop_model = cop_model
        self.shr_model = shr_model or SensibleHeatRatioModel(**(shr_kwargs or {}))

    def ecdd(
        self,
        t_ambient_k: ArrayLike,
        *,
        rh_array: Optional[ArrayLike] = None,
        dewpoint_array: Optional[ArrayLike] = None,
    ) -> np.ndarray:
        """
        Return effective CDD given ambient temps and humidity (RH or dew point).

        eCDD is defined as CDD / (COP × SHR). Using ECOP = COP × SHR keeps the
        relationship consistent with ECOP usage elsewhere.
        """
        if (rh_array is None and dewpoint_array is None) or (
            rh_array is not None and dewpoint_array is not None
        ):
            raise ValueError("Provide exactly one of rh_array or dewpoint_array.")

        cdd = self.cdd_model.cdd(t_ambient_k)
        shr = self.shr_model.shr(
            t_ambient_k, rh_array=rh_array, dewpoint_array=dewpoint_array
        )
        cop = self.cop_model.cop(t_ambient_k)
        ecop = np.asarray(cop, dtype=float) * np.asarray(shr, dtype=float)
        return np.asarray(cdd, dtype=float) / ecop
