import logging
from typing import Dict, Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

logger = logging.getLogger(__name__)


def generate_auto_predictions_s1(
    difficulties: pd.DataFrame,
    r_levels: Iterable[float],
    sd_true: float = 1.0,
    sd_pred: float = 1.0,
    seed: int | None = None,
) -> dict[str, pd.DataFrame]:
    """Genera predicciones de dificultad correlacionadas para distintos niveles de R.

    Para cada nivel r en ``r_levels``, se simula un vector ``true_b`` y un vector de
    predicciones ``pred_b`` con correlación aproximada r. Devuelve un diccionario
    particionado para ser persistido con ``PartitionedDataset``.

    Returns: mapping nombre_archivo -> DataFrame con columnas [item_id, true_b, pred_b].
    """
    rng = np.random.default_rng(seed)

    difficulties = difficulties.sort_values("item_id")
    item_ids = difficulties["item_id"].to_numpy()
    n_items = int(difficulties.shape[0])

    out: dict[str, pd.DataFrame] = {}
    for r in r_levels:
        r = float(r)
        cov = r * sd_true * sd_pred
        mean = [0.0, 0.0]
        cov_matrix = [[sd_true ** 2, cov], [cov, sd_pred ** 2]]
        sim = rng.multivariate_normal(mean, cov_matrix, n_items)
        true_b = sim[:, 0]
        pred_b = sim[:, 1]
        df = pd.DataFrame({"item_id": item_ids, "true_b": true_b, "pred_b": pred_b})
        # Nombre estable para el archivo de cada partición
        key = f"r_{str(r).replace('.', '_')}.csv"
        out[key] = df
        logger.info("[auto_pred_s1] r=%.2f, R2 aprox=%.3f", r, np.corrcoef(true_b, pred_b)[0, 1] ** 2)

    return out


def generate_predicted_difficulties_for_r(
    difficulties: pd.DataFrame,
    discrimination: float,
    seed: int | None = None,
) -> pd.DataFrame:
    """Genera predicciones de dificultad para un único nivel de discriminación.

    Interpreta ``discrimination`` como R^2 objetivo = corr(true, pred)^2.
    Genera predicciones que preservan media y varianza de ``true`` y con
    correlación objetivo r = sqrt(R^2_objetivo).

    Devuelve un DataFrame con columnas [item_id, predicted_difficulty].
    """
    if seed is not None:
        np.random.seed(seed + int(round(float(discrimination) * 100)))

    diffs = difficulties.sort_values("item_id").reset_index(drop=True)
    true = diffs["difficulty"].to_numpy(dtype=float)

    mu = float(true.mean())
    sd = float(true.std(ddof=0)) or 1.0

    # R^2 objetivo (corr^2) y correlación objetivo r
    r2_target = float(np.clip(discrimination, 0.0, 1.0))
    r = float(np.sqrt(r2_target))

    # Predicción sin estandarizar explícitamente: misma media y varianza que true
    noise_sd = sd * np.sqrt(max(1.0 - r * r, 0.0))
    pred = mu + r * (true - mu) + np.random.normal(0.0, noise_sd, size=true.shape[0])

    df = pd.DataFrame({
        "item_id": diffs["item_id"].to_numpy(),
        "predicted_difficulty": pred,
    })

    # Reportar la métrica de discriminación como corr^2 (r^2)
    try:
        corr = float(np.corrcoef(true, pred)[0, 1]) if true.size > 1 else 1.0
        r2_corr = corr * corr
        logger.info(
            "[auto_pred_s1] R2_objetivo=%.2f, items=%d, corr^2=%.3f",
            r2_target, true.size, r2_corr,
        )
    except Exception:
        logger.info("[auto_pred_s1] R2_objetivo=%.2f, items=%d (corr^2 no disponible)", r2_target, true.size)

    return df


def summarize_pred_discrimination(
    difficulties: pd.DataFrame,
    **preds: pd.DataFrame,
) -> pd.DataFrame:
    """Resumen de discriminación lograda por cada dataset de predicción.

    Espera ``difficulties`` con columnas [item_id, difficulty] y múltiples
    dataframes de predicción como kwargs, donde cada uno tiene columnas
    [item_id, predicted_difficulty]. Las claves de kwargs deben tener el
    formato ``pred_r_0_1``, ``pred_r_0_2``, etc., de donde se extrae el
    ``r_target``.
    """
    diffs = difficulties.sort_values("item_id").reset_index(drop=True)
    true = diffs["difficulty"].to_numpy(dtype=float)

    rows: list[dict] = []
    for key, df in sorted(preds.items()):
        # Extraer r objetivo de la clave 'pred_r_0_1' -> 0.1
        try:
            r_str = key.split("pred_r_")[-1]
            r_target = float(r_str.replace("_", "."))
            r2_target = r_target ** 2
        except Exception:
            r_target, r2_target = (float("nan"), float("nan"))

        pred_df = df.sort_values("item_id").reset_index(drop=True)
        pred = pred_df["predicted_difficulty"].to_numpy(dtype=float)

        # Alinear si fuese necesario
        if pred_df.shape[0] != diffs.shape[0] or not np.all(pred_df["item_id"].to_numpy() == diffs["item_id"].to_numpy()):
            merged = pd.merge(diffs, pred_df, on="item_id", how="inner")
            true_al = merged["difficulty"].to_numpy(dtype=float)
            pred_al = merged["predicted_difficulty"].to_numpy(dtype=float)
        else:
            true_al, pred_al = true, pred

        corr = float(np.corrcoef(true_al, pred_al)[0, 1]) if true_al.size > 1 else 1.0
        r2 = corr * corr
        rows.append({
            "dataset_key": key,
            "r_target": r_target,
            "r2_target": r2_target,
            "r_achieved": corr,
            "r2_achieved": r2,
            "n_items": int(true_al.size),
        })

    summary = pd.DataFrame(rows).sort_values("r_target").reset_index(drop=True)
    logger.info("[auto_pred_s1] resumen discriminación: %s", summary.to_dict(orient="list"))
    return summary
