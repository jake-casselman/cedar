import numpy as np
import pytest

from cedar.metrics.cdd import CoolingDegreeDays
from cedar.metrics.effective_cdd import EffectiveCDD
from cedar.metrics.effective_cop import EffectiveCOP
from cedar.metrics.shr import SensibleHeatRatioModel


class DummyCOP:
    def __init__(self, value=3.0):
        self.value = value

    def cop(self, t_ambient_k):
        arr = np.asarray(t_ambient_k, dtype=float)
        return np.full_like(arr, self.value, dtype=float)


class DummySHR:
    def __init__(self, value=0.7):
        self.value = value

    def shr(self, T_array, *, rh_array=None, dewpoint_array=None):
        arr = np.asarray(T_array, dtype=float)
        return np.full_like(arr, self.value, dtype=float)


def test_effective_cop_with_dummy_models(monkeypatch):
    # Patch kwargs branch to use dummy model without CoolProp
    monkeypatch.setattr("cedar.metrics.effective_cop.SingleFluidCOP", DummyCOP)
    monkeypatch.setattr("cedar.metrics.effective_cop.SensibleHeatRatioModel", DummySHR)

    ecop = EffectiveCOP(
        cop_kwargs={"value": 4.0},
        shr_kwargs={"value": 0.5},
    )
    vals = ecop.ecop([295.0, 300.0], rh_array=[0.5, 0.6])
    assert np.allclose(vals, [2.0, 2.0])

    with pytest.raises(ValueError):
        ecop.ecop([295.0], rh_array=[0.5], dewpoint_array=[283.0])


def test_cdd_exceedance_basic():
    cdd = CoolingDegreeDays(base_temperature_K=18.0 + 273.15)
    temps = [290.0, 293.0, 296.0]
    exceed = cdd.cdd(temps)
    assert np.allclose(exceed, [0.0, 1.85, 4.85], atol=1e-2)


def test_effective_cdd_with_dummy_models(monkeypatch):
    monkeypatch.setattr("cedar.metrics.effective_cdd.SingleFluidCOP", DummyCOP)
    monkeypatch.setattr("cedar.metrics.effective_cdd.SensibleHeatRatioModel", DummySHR)
    ecdd = EffectiveCDD(
        cdd_kwargs={"base_temperature_K": 18.0 + 273.15},
        cop_kwargs={"value": 4.0},
        shr_kwargs={"value": 0.5},
    )
    temps = [295.0, 300.0]
    vals = ecdd.ecdd(temps, rh_array=[0.5, 0.6])
    # CDD exceedance divided by ECOP (4*0.5 = 2)
    expected_cdd = np.clip(np.asarray(temps) - (18.0 + 273.15), 0, None)
    assert np.allclose(vals, expected_cdd / 2.0)
