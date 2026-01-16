from __future__ import annotations
"""
cedar.utils.plotting
--------------------
Helper routines for plotting and saving results.
"""

from pathlib import Path
import contextlib

def plot_cop_chart(
    T_dense,
    cop_dense,
    fluid: str,
    *,
    show: bool = True,
    save_path: Path | str | None = None,
    dpi: int = 300,
    figsize: tuple[int, int] = (6, 4),
    tight_layout: bool = True,
    logger=None,
    verbose: bool = False,
):
    """
    Display and/or save the COP reference chart (T_ambient vs COP).

    Parameters
    ----------
    T_dense : array-like
        Ambient temperature grid [K].
    cop_dense : array-like
        Corresponding COP values.
    fluid : str
        Fluid label for the plot title.
    show : bool, default True
        Show the figure interactively.
    save_path : str | pathlib.Path | None, optional
        Filepath to save the plot (determines format by extension).
    dpi : int, default 300
        Output resolution when saving.
    figsize : (int, int), default (6, 4)
        Figure size in inches.
    tight_layout : bool, default True
        Call fig.tight_layout() before showing/saving.
    logger : logging.Logger, optional
        If provided, logs the save path.
    verbose : bool, default False
        Controls whether to log save messages.

    Returns
    -------
    matplotlib.figure.Figure | None
        The figure object if matplotlib is available, else None.
    """
    with contextlib.suppress(ImportError):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(T_dense, cop_dense, lw=1.4)
        ax.set_xlabel("Ambient temperature [K]")
        ax.set_ylabel("COP")
        ax.set_title(f"COP reference chart – {fluid}")
        ax.grid(True, which="both", ls="--", alpha=0.5)

        if tight_layout:
            fig.tight_layout()

        # save if needed
        if save_path is not None:
            save_path = Path(save_path).expanduser()
            save_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
            if verbose and logger:
                logger.info("COP chart saved to '%s'", save_path)

        if show:
            plt.show()
        else:
            plt.close(fig)

        return fig

    if logger:
        logger.warning("matplotlib not found – install it via 'pip install matplotlib>=3.8'")
    return None