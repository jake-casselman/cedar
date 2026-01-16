"""CDD exceedance example."""

from pathlib import Path

import numpy as np

from cedar.metrics.cdd import CoolingDegreeDays


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    cdd_model = CoolingDegreeDays(base_temperature_K=18.0 + 273.15)

    temps_K = np.array([290.0, 293.0, 296.0])
    cdd_vals = cdd_model.cdd(temps_K)
    print("CDD exceedance:", cdd_vals.tolist())

    np.savetxt(
        output_dir / "cdd_profile.csv",
        np.column_stack([temps_K, cdd_vals]),
        fmt="%.4f",
        delimiter=",",
        header="t_ambient_k,CDD_exceedance",
        comments="",
    )
    print(f"Saved CDD profile to {output_dir / 'cdd_profile.csv'}")


if __name__ == "__main__":
    main()
