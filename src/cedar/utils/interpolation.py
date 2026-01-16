"""
Helper routines for interpolation.
"""

import numpy as np
from scipy.interpolate import interp1d

def build_interpolator(x, y):
    """Return a cubic interpolator ignoring NaN values."""
    mask = ~np.isnan(y)
    if mask.sum() < 2:
        raise RuntimeError("Not enough valid points to build an interpolator.")
    return interp1d(
        np.asarray(x)[mask],
        np.asarray(y)[mask],
        kind="cubic",
        bounds_error=False,
        fill_value=np.nan,
    )
