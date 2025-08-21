import pandas as pd
import matplotlib.pyplot as plt
from typing import Literal


def _plot_metric_vs_percent(df: pd.DataFrame, metric: Literal["mse", "r2"], title: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    # Hay dos casos: MMLE (solo percent) y Bayes (percent y r_level)
    if "r_level" in df.columns and df["r_level"].notna().any():
        # Graficar una línea por r_level
        for r, sub in df.groupby("r_level", dropna=True):
            sub2 = sub.sort_values("percent")
            ax.plot(sub2["percent"], sub2[metric], marker="o", label=f"r={r}")
        ax.legend(title="r_level", loc="best")
    else:
        sub2 = df.sort_values("percent")
        ax.plot(sub2["percent"], sub2[metric], marker="o")

    ax.set_xlabel("percent")
    ax.set_ylabel(metric)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_mmle_summary(mmle_summary: pd.DataFrame) -> dict:
    """Genera figuras percent vs MSE y percent vs R2 para MMLE.

    Espera columnas: [percent, mse, r2].
    Devuelve dict con claves: mmle_fig_percent_vs_mse, mmle_fig_percent_vs_r2
    """
    figs = {}
    figs["mmle_fig_percent_vs_mse"] = _plot_metric_vs_percent(mmle_summary, "mse", "MMLE: percent vs MSE")
    figs["mmle_fig_percent_vs_r2"] = _plot_metric_vs_percent(mmle_summary, "r2", "MMLE: percent vs R2")
    return figs


def plot_bayes_summary(bayes_summary: pd.DataFrame) -> dict:
    """Genera figuras percent vs MSE y percent vs R2 para Bayes.

    Espera columnas: [percent, r_level, mse, r2].
    Devuelve dict con claves: bayes_fig_percent_vs_mse, bayes_fig_percent_vs_r2
    """
    figs = {}
    figs["bayes_fig_percent_vs_mse"] = _plot_metric_vs_percent(bayes_summary, "mse", "Bayes: percent vs MSE (por r)")
    figs["bayes_fig_percent_vs_r2"] = _plot_metric_vs_percent(bayes_summary, "r2", "Bayes: percent vs R2 (por r)")
    return figs


# --- Nuevos: Bayes con líneas horizontales de MMLE como baseline ---

def _plot_bayes_with_mmle_hlines(
    bayes_summary: pd.DataFrame,
    mmle_summary: pd.DataFrame,
    metric: Literal["mse", "r2"],
    title: str,
) -> plt.Figure:
    # Graficar Bayes (líneas por r) como antes
    fig, ax = plt.subplots(figsize=(6, 4))
    for r, sub in bayes_summary.groupby("r_level", dropna=True):
        sub2 = sub.sort_values("percent")
        ax.plot(sub2["percent"], sub2[metric], marker="o", label=f"Bayes r={r}")

    # Determinar rango en X (percent)
    percents = sorted(bayes_summary["percent"].unique().tolist())
    if len(percents) == 0:
        x_min, x_max = 0.0, 1.0
    else:
        x_min, x_max = float(min(percents)), float(max(percents))

    # Línea horizontal (baseline MMLE) usando SOLO percent=1.0
    baseline_drawn = False
    mmle_p1 = mmle_summary.loc[mmle_summary["percent"] == 1.0, ["percent", metric]].dropna()
    if not mmle_p1.empty:
        y = float(mmle_p1.iloc[0][metric])
        ax.hlines(y=y, xmin=x_min, xmax=x_max, colors="tab:gray", linestyles="dashed", alpha=0.7)
        baseline_label = "MMLE baseline (percent=1.0)"
        baseline_drawn = True

    # Leyenda: añadir baseline sólo si fue dibujada
    from matplotlib.lines import Line2D
    handles, labels = ax.get_legend_handles_labels()
    if baseline_drawn:
        custom = [Line2D([0], [0], color="tab:gray", linestyle="--", alpha=0.8, label=baseline_label)]
        ax.legend(handles + custom, labels + [baseline_label], loc="best")
    else:
        ax.legend(loc="best")

    ax.set_xlabel("percent")
    ax.set_ylabel(metric)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_bayes_vs_mmle_baselines(
    mmle_summary: pd.DataFrame,
    bayes_summary: pd.DataFrame,
) -> dict:
    """Figuras combinadas Bayes (por r) + líneas horizontales MMLE por percent.

    Devuelve dict con claves: bayes_r2_with_mmle_hlines, bayes_mse_with_mmle_hlines
    """
    figs = {}
    figs["bayes_r2_with_mmle_hlines"] = _plot_bayes_with_mmle_hlines(
        bayes_summary, mmle_summary, "r2", "Bayes vs MMLE: percent vs R2 (por r + baseline MMLE)"
    )
    figs["bayes_mse_with_mmle_hlines"] = _plot_bayes_with_mmle_hlines(
        bayes_summary, mmle_summary, "mse", "Bayes vs MMLE: percent vs MSE (por r + baseline MMLE)"
    )
    return figs
