"""Effective CDD example (CDD / (COP × SHR))."""

from pathlib import Path

import numpy as np

from cedar.metrics.effective_cdd import EffectiveCDD


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    ecdd_model = EffectiveCDD(
        cop_kwargs=dict(
            fluid="R134a",
            t_evap_k=273.15,
            delta_t_cond=10,
            eta_is=0.8,
            delta_t_min=10.0,
        ),
        shr_kwargs=dict(
            p_atm=101_325.0,
            t_evap_k=273.15,
            approach_temp=1.0,
            C_p=1020.05,
            H_fg=2.501e6,
            rh_out=1.0,
        ),
        cdd_kwargs=dict(base_temperature_K=18.0 + 273.15),
    )

    temps_K = np.array([295.0, 300.0, 305.0])
    dewpoint_K = temps_K - 12.0

    ecdd_vals = ecdd_model.ecdd(temps_K, dewpoint_array=dewpoint_K)
    print("eCDD values:", ecdd_vals.tolist())

    np.savetxt(
        output_dir / "ecdd_profile.csv",
        np.column_stack([temps_K, dewpoint_K, ecdd_vals]),
        fmt="%.4f",
        delimiter=",",
        header="t_ambient_k,dewpoint_K,eCDD",
        comments="",
    )
    print(f"Saved eCDD profile to {output_dir / 'ecdd_profile.csv'}")


if __name__ == "__main__":
    main()
