"""
Tests for SensibleHeatRatioModel and supporting SHR physics.
"""

import numpy as np
import pytest

from cedar.physics.shr import compute_relative_humidity, sensible_heat_ratio
from cedar.metrics.shr import SensibleHeatRatioModel


def test_compute_relative_humidity_matches_reference():
    rh = compute_relative_humidity(293.15, 283.15)
    assert np.isclose(rh, 0.5254, atol=1e-3)

    # Clip at saturation when dew point exceeds temperature
    rh_high = compute_relative_humidity(280.0, 285.0)
    assert np.isclose(rh_high, 1.0)


def test_sensible_heat_ratio_matches_reference_value():
    shr = sensible_heat_ratio(295.0, 0.4)
    assert np.isclose(shr, 0.7766, atol=1e-3)


def test_model_supports_both_rh_and_dewpoint_paths():
    model = SensibleHeatRatioModel()
    temps = np.array([295.0, 300.0])
    dew = np.array([283.15, 288.15])

    rh_from_dew = compute_relative_humidity(temps, dew)
    shr_from_rh = model.shr(temps, rh_array=rh_from_dew)
    shr_from_dew = model.shr(temps, dewpoint_array=dew)

    assert shr_from_rh.shape == temps.shape
    assert np.allclose(shr_from_dew, shr_from_rh, atol=1e-6)

    # First value should match a known reference
    assert np.isclose(shr_from_dew[0], 0.7037, atol=1e-3)


def test_shr_interpolator_path_and_shape():
    model = SensibleHeatRatioModel(t_grid=[295.0, 300.0], rh_grid=[0.4, 0.6])
    temps = np.array([[295.0, 300.0], [297.5, 299.0]])
    rh = np.array([[0.4, 0.6], [0.5, 0.55]])
    result = model.shr(temps, rh_array=rh)
    assert result.shape == temps.shape
    assert np.all((result >= 0) & (result <= 1))


def test_shr_raises_when_both_inputs_provided():
    model = SensibleHeatRatioModel()
    with pytest.raises(ValueError):
        model.shr(295.0, rh_array=0.5, dewpoint_array=283.0)
