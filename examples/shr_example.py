"""Minimal SHR example for CEDAR."""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from cedar.metrics.shr import SensibleHeatRatioModel


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    shr_model = SensibleHeatRatioModel(
        p_atm=101_325.0,
        t_evap_k=273.15,
        approach_temp=1.0,
        C_p=1020.05,
        H_fg=2.501e6,
        rh_out=1.0,
    )

    temps_K = np.array([295.0, 300.0, 305.0])

    # Dew point path: dew point -> RH -> SHR
    dewpoint_K = temps_K - 12.0
    shr_from_dew = shr_model.shr(temps_K, dewpoint_array=dewpoint_K)

    # Relative humidity path (direct)
    rh = np.array([0.47, 0.65, 0.55])
    shr_from_rh = shr_model.shr(temps_K, rh_array=rh)

    print("SHR from dew point:", shr_from_dew.tolist())
    print("SHR from RH:", shr_from_rh.tolist())

    # SHR map with temperature on x-axis and relative humidity on y-axis
    temp_axis = np.linspace(283.15, 333.15, 120)  # 10°C to 60°C
    rh_axis = np.linspace(0.0, 1.0, 100)  # full RH range
    temp_grid, rh_grid = np.meshgrid(temp_axis, rh_axis)
    shr_grid = shr_model.shr(temp_grid, rh_array=rh_grid)

    fig, ax = plt.subplots(figsize=(6, 4))
    h = ax.pcolormesh(temp_axis, rh_axis, shr_grid, shading="auto", cmap="viridis", vmin=0, vmax=1)
    cs = ax.contour(
        temp_axis,
        rh_axis,
        shr_grid,
        levels=np.arange(0.0, 1.01, 0.1),
        colors="k",
        linewidths=0.6,
        alpha=0.6,
    )
    ax.clabel(cs, fmt="%.1f", fontsize=7)
    fig.colorbar(h, ax=ax, label="SHR")
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Relative Humidity (-)")
    ax.set_title("SHR vs Temperature and Relative Humidity")
    map_path = output_dir / "shr_temp_rh_map.png"
    fig.tight_layout()
    fig.savefig(map_path, dpi=200)
    plt.close(fig)
    print(f"Saved SHR temperature/RH map to {map_path}")

    np.savetxt(
        output_dir / "shr_1d_profile.csv",
        np.column_stack([temps_K, shr_from_dew, shr_from_rh]),
        fmt="%.4f",
        delimiter=",",
        header="t_ambient_k,SHR_from_dewpoint,SHR_from_RH",
        comments="",
    )
    print(f"Saved 1D SHR comparison to {output_dir / 'shr_1d_profile.csv'}")


if __name__ == "__main__":
    main()
