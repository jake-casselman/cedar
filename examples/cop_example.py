"""Minimal COP example for CEDAR."""

from pathlib import Path

import numpy as np

from cedar.metrics.cop import SingleFluidCOP


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    hp = SingleFluidCOP(
        "R134a",
        t_evap_k=273.15,
        delta_t_cond=10,
        eta_is=0.8,
        delta_t_min=10.0,
    )

    # Scalar/vector examples
    cop_scalar = hp.cop(298.15)
    cop_array = hp.cop([280, 290, 300])

    print("COP at 298.15 K:", float(cop_scalar))
    print("COP at 280/290/300 K:", cop_array.tolist())

    # Fake climate profile for charting (e.g., diurnal temps)
    ambient_profile = np.linspace(280, 305, 50)
    cop_profile = hp.cop(ambient_profile)

    # Save a reference COP curve
    chart_path = output_dir / "cop_curve.png"
    hp.plot(show=False, save_path=chart_path, dpi=200)
    print(f"Saved COP curve to {chart_path}")

    # Save the synthetic profile values alongside COP
    np.savetxt(
        output_dir / "cop_profile.csv",
        np.column_stack([ambient_profile, cop_profile]),
        fmt="%.4f",
        delimiter=",",
        header="t_ambient_k,COP",
        comments="",
    )
    print(f"Saved synthetic COP profile to {output_dir / 'cop_profile.csv'}")


if __name__ == "__main__":
    main()
