"""Effective COP example (COP × SHR)."""

from pathlib import Path
import numpy as np

from cedar.metrics.effective_cop import EffectiveCOP

def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    ecop_model = EffectiveCOP(
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
    )

    temps_K = np.array([295.0, 300.0, 305.0])
    dewpoint_K = temps_K - 12.0

    ecop_vals = ecop_model.ecop(temps_K, dewpoint_array=dewpoint_K)
    print("ECOP values:", ecop_vals.tolist())

    np.savetxt(
        output_dir / "ecop_profile.csv",
        np.column_stack([temps_K, dewpoint_K, ecop_vals]),
        fmt="%.4f",
        delimiter=",",
        header="t_ambient_k,dewpoint_K,ECOP",
        comments="",
    )
    print(f"Saved ECOP profile to {output_dir / 'ecop_profile.csv'}")


if __name__ == "__main__":
    main()
