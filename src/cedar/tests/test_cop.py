"""
Verbose test suite for cedar.metrics.cop and cedar.utils.validation

Covers:
 - Valid and invalid parameter combinations
 - Scalar and array COP evaluation
 - Plot generation
 - Verbose printing for human inspection
"""

import pytest
import numpy as np
import warnings
import math
import types
import sys

from cedar.metrics.cop import SingleFluidCOP
from cedar.physics.cop import cop_single
from cedar.utils.validation import validate_refrigerant, validate_params
from cedar.utils.plotting import plot_cop_chart

from CoolProp.CoolProp import PropsSI

# ───────────────────────────────────────────────────────────────
# VALIDATION TESTS
# ───────────────────────────────────────────────────────────────

def test_validate_params_warns_on_celsius_like_values():
    print("\n⚠️  Testing Celsius-like inputs that should trigger warnings...")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # 25°C -> 25 K → should warn
        validate_params(25, 10, 0.8, 10)
        # 100°C -> 100 K → should warn (likely °C)
        validate_params(100, 10, 0.8, 10)
        # borderline Kelvin (190 K) → low but possible
        validate_params(190, 10, 0.8, 10)

        for warning in w:
            print(f"⚠️  Warning captured: {warning.message}")

    assert any("Celsius" in str(w.message) or "low" in str(w.message) for w in w), \
        "Expected at least one Celsius-related warning"

def test_validate_params_no_warning_for_normal_kelvin():
    print("\n✅ Testing normal Kelvin values (should be silent)...")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        validate_params(275, 10, 0.8, 10)  # around 2°C
        validate_params(300, 10, 0.8, 10)  # ~27°C typical
        validate_params(310, 10, 0.8, 10)  # warm case

        for warning in w:
            print(f"❌ Unexpected warning: {warning.message}")

    assert len(w) == 0, "No warnings should be raised for realistic Kelvin inputs"

def test_validate_refrigerant_pass():
    print("\n✅ Testing valid refrigerant R134a...")
    validate_refrigerant("R134a", PropsSI)  # Should not raise
    print("   → Passed (CoolProp recognizes R134a).")

def test_validate_refrigerant_fail():
    print("\n⚠️ Testing invalid refrigerant name...")
    with pytest.raises(ValueError, match="not recognised"):
        validate_refrigerant("NOTAFRIG", PropsSI)
    print("   → Correctly raised ValueError for invalid refrigerant.")

@pytest.mark.parametrize(
    "t_evap_k, delta_t_cond, eta_is, delta_t_min, expected_error",
    [
        (0, 10, 0.8, 10, "`t_evap_k` must be > 0 K."),
        (273, -5, 0.8, 10, "`delta_t_cond` must be ≥ 0 K."),
        (273, 10, 1.5, 10, "`eta_is` must be in"),
        (273, 10, 0.8, -1, "`delta_t_min` must be ≥ 0 K."),
    ],
)
def test_validate_params_fail(t_evap_k, delta_t_cond, eta_is, delta_t_min, expected_error):
    print(f"\n⚙️ Testing validation failure case:")
    print(f"   Inputs: T_evap={t_evap_k}, ΔT_cond={delta_t_cond}, η={eta_is}, ΔT_min={delta_t_min}")
    with pytest.raises(ValueError, match=expected_error):
        validate_params(t_evap_k, delta_t_cond, eta_is, delta_t_min)
    print("   → Correctly failed with expected message.")

def test_validate_params_pass():
    print("\n✅ Testing validation with all valid params...")
    validate_params(273.15, 10, 0.85, 5)
    print("   → Passed with valid parameter set.")

# ───────────────────────────────────────────────────────────────
# COP MODEL TESTS
# ───────────────────────────────────────────────────────────────

def test_cop_scalar():
    print("\n🌡️ Testing SingleFluidCOP scalar computation...")
    hp = SingleFluidCOP("R134a", t_evap_k=273.15, delta_t_cond=10)
    val = hp.cop(298.15)
    print(f"   COP(298.15 K) = {val:.3f}")
    assert np.isfinite(val)

def test_cop_array():
    print("\n📈 Testing SingleFluidCOP vectorized computation...")
    hp = SingleFluidCOP("R134a", t_evap_k=273.15, delta_t_cond=10)
    temps = np.array([280.0, 290.0, 300.0])
    result = hp.cop(temps)
    print(f"   Input:  {temps}")
    print(f"   Output: {np.round(result, 3)}")
    assert result.shape == temps.shape
    assert np.all(np.isfinite(result))

def test_cop_out_of_bounds():
    print("\n🧊 Testing SingleFluidCOP extrapolation handling...")
    hp = SingleFluidCOP("R134a", t_evap_k=273.15, delta_t_cond=10)
    low_temp = 100.0  # Well below interpolation range
    val = hp.cop(low_temp)
    print(f"   COP(100 K) = {val}")
    assert np.isnan(val), "Out-of-bounds should return NaN"


def test_plot_output(tmp_path):
    print("\n🎨 Testing plotting utility...")
    hp = SingleFluidCOP("R134a", t_evap_k=273.15, delta_t_cond=10)
    out = tmp_path / "cop_chart.png"
    fig = hp.plot(show=False, save_path=out)
    print(f"   Saved figure to: {out}")
    assert out.exists(), "Plot file should have been created"
    assert fig is not None
    print("   → Plotting successful.")
    
def test_plotting_fallback_without_matplotlib(monkeypatch):
    """Simulate missing matplotlib and ensure graceful fallback with logger warning."""
    dummy_logger = types.SimpleNamespace(warning=lambda msg: print(f"⚠️ Logged warning: {msg}"))

    # Temporarily remove matplotlib
    monkeypatch.setitem(sys.modules, "matplotlib", None)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", None)

    result = plot_cop_chart(
        [280, 290, 300],
        [10, 8, 6],
        "R134a",
        show=False,
        logger=dummy_logger,
    )
    assert result is None
    print("✅ plot_cop_chart gracefully handled missing matplotlib.")

# ───────────────────────────────────────────────────────────────
# cop_single FUNCTION TESTS
# ───────────────────────────────────────────────────────────────

def test_cop_single_invalid_temperature_order():
    """t_cond_k <= t_evap_k should return NaN."""
    result = cop_single("R134a", t_evap_k=300, t_cond_k=290)
    assert math.isnan(result)
    print("✅ Returned NaN for invalid temperature order (cond <= evap).")

def test_cop_single_zero_work_condition():
    """Should return NaN when condenser temperature ≤ evaporator (no work possible)."""
    result = cop_single("R134a", t_evap_k=300.0, t_cond_k=300.0, eta_is=0.8)
    assert math.isnan(result)
    print("✅ Returned NaN for zero/negative work input condition (T_cond ≤ T_evap).")

def test_cop_single_invalid_fluid_triggers_exception():
    """Invalid fluid should trigger exception and return NaN."""
    result = cop_single("FakeFluid", t_evap_k=273.15, t_cond_k=300.0)
    assert math.isnan(result)
    print("✅ Returned NaN for invalid refrigerant (exception handled).")