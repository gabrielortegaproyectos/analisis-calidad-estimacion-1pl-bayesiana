import logging
from typing import Dict

import numpy as np
import pandas as pd
from girth import rasch_mml

logger = logging.getLogger(__name__)


def _filter_responses_with_mask(responses: pd.DataFrame, mask: pd.DataFrame) -> pd.DataFrame:
    """Filtra filas de ``responses`` usando una máscara 0/1.

    Asume que ``responses`` tiene columna ``person_id`` y columnas ``item_1..item_N``.
    Asume que la máscara tiene columna ``mask`` con largo igual al número total de personas.
    Se alinea por orden: ``person_id`` ascendente ↔ índice 0..N-1 de la máscara.
    """
    if "mask" not in mask.columns:
        raise ValueError("La máscara debe tener una columna 'mask'.")

    resp = responses.sort_values("person_id").reset_index(drop=True)
    m = mask["mask"].to_numpy().astype(int)
    if m.size != resp.shape[0]:
        raise ValueError(f"Tamaño de máscara {m.size} no coincide con n_responses={resp.shape[0]}")

    selected = resp[m == 1]
    selected = selected.reset_index(drop=True)
    return selected


def _responses_to_items_x_persons_matrix(filtered_responses: pd.DataFrame) -> np.ndarray:
    """Convierte el DF de respuestas filtradas a matriz [items x participantes] de 0/1."""
    if "person_id" not in filtered_responses.columns:
        raise ValueError("Se espera columna 'person_id' en responses.")
    X = filtered_responses.drop(columns=["person_id"]).to_numpy(dtype=int)
    # Rasch MML espera [items x participants]
    return X.T


def mmle_estimate_for_mask(responses: pd.DataFrame, mask: pd.DataFrame) -> pd.DataFrame:
    """Aplica filtro por ``mask`` y estima dificultades con ``girth.rasch_mml``.

    Devuelve DF con columnas: [item_id, est_difficulty].
    """
    filtered = _filter_responses_with_mask(responses, mask)
    n_selected = int(filtered.shape[0])
    X_items_by_persons = _responses_to_items_x_persons_matrix(filtered)

    if n_selected < 2:
        logger.warning("[mmle_s1] Muy pocos participantes seleccionados: %d", n_selected)

    try:
        result: Dict[str, np.ndarray | float] = rasch_mml(X_items_by_persons, discrimination=1)
        diffs = np.asarray(result["Difficulty"], dtype=float)
        # Alineamos con item_id = 1..N (como en sample__s1)
        out = pd.DataFrame({
            "item_id": np.arange(1, diffs.size + 1, dtype=int),
            "est_difficulty": diffs,
        })
        logger.info("[mmle_s1] Estimación OK: persons=%d, items=%d", n_selected, diffs.size)
        return out
    except Exception as ex:  # pragma: no cover
        logger.exception("[mmle_s1] Error en rasch_mml con persons=%d: %s", n_selected, ex)
        # Devuelve NaNs para mantener el flujo
        n_items = filtered.shape[1] - 1
        return pd.DataFrame({
            "item_id": np.arange(1, n_items + 1, dtype=int),
            "est_difficulty": np.full((n_items,), np.nan, dtype=float),
        })


def summarize_mmle_estimation(
    difficulties: pd.DataFrame,
    **estimates: pd.DataFrame,
) -> pd.DataFrame:
    """Compara dificultades estimadas vs verdaderas para cada máscara.

    ``difficulties``: columnas [item_id, difficulty]
    ``estimates``: kwargs con claves como 'est_p_0_1', valores DF [item_id, est_difficulty]
    """
    true_df = difficulties.sort_values("item_id").reset_index(drop=True)

    rows: list[dict] = []
    for key, est_df in sorted(estimates.items()):
        # extrae el percent de la clave 'est_p_0_1' -> 0.1
        try:
            p_str = key.split("est_p_")[-1]
            percent = float(p_str.replace("_", "."))
        except Exception:
            percent = float("nan")

        est_df = est_df.sort_values("item_id").reset_index(drop=True)
        merged = pd.merge(true_df, est_df, on="item_id", how="inner")
        y_true = merged["difficulty"].to_numpy(dtype=float)
        y_hat = merged["est_difficulty"].to_numpy(dtype=float)

        if y_true.size < 2 or np.all(~np.isfinite(y_hat)):
            r = np.nan
            r2 = np.nan
            mse = np.nan
            mae = np.nan
            bias = np.nan
        else:
            r = float(np.corrcoef(y_true, y_hat)[0, 1])
            r2 = r * r
            err = y_hat - y_true
            mse = float(np.mean(err ** 2))
            mae = float(np.mean(np.abs(err)))
            bias = float(np.mean(err))

        rows.append({
            "dataset_key": key,
            "percent": percent,
            "r": r,
            "r2": r2,
            "mse": mse,
            "mae": mae,
            "bias": bias,
            "n_items": int(y_true.size),
        })

    summary = pd.DataFrame(rows).sort_values("percent").reset_index(drop=True)
    logger.info("[mmle_s1] resumen estimación: %s", summary.to_dict(orient="list"))
    return summary
