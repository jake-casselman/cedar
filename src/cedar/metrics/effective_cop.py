"""
cedar.metrics.effective_cop
---------------------------
Effective COP metric (ECOP) combining COP and SHR.

ECOP = COP × SHR represents the fraction of input work that produces
*sensible* cooling, accounting for both thermodynamic efficiency and
the latent load penalty under humid conditions.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from numpy.typing import ArrayLike

from cedar.metrics.cop import SingleFluidCOP
from cedar.metrics.shr import SensibleHeatRatioModel


class EffectiveCOP:
    """
    Compute ECOP = COP × SHR.

    You can pass pre-built models or provide kwargs to build them here.
    """

    def __init__(
        self,
        cop_model: Optional[SingleFluidCOP] = None,
        *,
        shr_model: Optional[SensibleHeatRatioModel] = None,
        cop_kwargs: Optional[dict] = None,
        shr_kwargs: Optional[dict] = None,
    ) -> None:
        if cop_model is None and cop_kwargs is None:
            raise ValueError("Provide either cop_model or cop_kwargs to build one.")
        if cop_model is None:
            cop_model = SingleFluidCOP(**cop_kwargs)  # type: ignore[arg-type]
        self.cop_model = cop_model
        self.shr_model = shr_model or SensibleHeatRatioModel(**(shr_kwargs or {}))

    def ecop(
        self,
        t_ambient_k: ArrayLike,
        *,
        rh_array: Optional[ArrayLike] = None,
        dewpoint_array: Optional[ArrayLike] = None,
    ) -> np.ndarray:
        """
        Return effective COP for given ambient temps and humidity (RH or dew point).
        """
        if (rh_array is None and dewpoint_array is None) or (
            rh_array is not None and dewpoint_array is not None
        ):
            raise ValueError("Provide exactly one of rh_array or dewpoint_array.")

        shr = self.shr_model.shr(
            t_ambient_k, rh_array=rh_array, dewpoint_array=dewpoint_array
        )
        cop = self.cop_model.cop(t_ambient_k)
        return np.asarray(shr, dtype=float) * np.asarray(cop, dtype=float)
